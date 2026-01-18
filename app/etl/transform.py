from typing import List, Dict, Any
from datetime import datetime
from app.models.schemas import WeatherDataPoint, WeatherSource, ConsensusDataPoint
from dateutil import parser

class WeatherTransformer:
    @staticmethod
    def transform_yr(raw_data: Dict[str, Any], lat: float, lon: float) -> List[WeatherDataPoint]:
        """
        Transforms Yr.no GeoJSON response into unified WeatherDataPoints.
        """
        points = []
        try:
            timeseries = raw_data.get("properties", {}).get("timeseries", [])
            for item in timeseries:
                time_str = item.get("time")
                data = item.get("data", {})
                instant = data.get("instant", {}).get("details", {})
                next_1h = data.get("next_1_hours", {}).get("details", {})

                # If temperature is missing, skip this point or handle accordingly.
                # Here we skip if critical data is missing.
                if "air_temperature" not in instant:
                    continue

                timestamp = parser.isoparse(time_str)
                temperature = instant.get("air_temperature")
                precipitation = next_1h.get("precipitation_amount", 0.0)

                points.append(WeatherDataPoint(
                    timestamp=timestamp,
                    lat=lat,
                    lon=lon,
                    source=WeatherSource.YR_NO,
                    temperature=temperature,
                    precipitation=precipitation
                ))
        except Exception as e:
            print(f"Error transforming Yr.no data: {e}")
            # In a real pipeline we might want to log this or raise partial error
        
        return points

    @staticmethod
    def transform_open_meteo(raw_data: Dict[str, Any], lat: float, lon: float) -> List[WeatherDataPoint]:
        """
        Transforms Open-Meteo response into unified WeatherDataPoints.
        """
        points = []
        try:
            hourly = raw_data.get("hourly", {})
            times = hourly.get("time", [])
            temps = hourly.get("temperature_2m", [])
            precips = hourly.get("precipitation", [])

            # Ensure all arrays are same length
            if not (len(times) == len(temps) == len(precips)):
                print("Mismatch in Open-Meteo array lengths")
                return []

            for i in range(len(times)):
                timestamp = parser.isoparse(times[i])
                # Ensure UTC awareness if naive
                if timestamp.tzinfo is None:
                     timestamp = timestamp.replace(tzinfo=datetime.timezone.utc) if hasattr(datetime, 'timezone') else timestamp
                # Fallback for older python or just use dateutil properly? 
                # Actually, simpliest is to assume Open-Meteo returns UTC (Z) if we didn't specify timezone,
                # but we used timezone=auto. Let's force it to match YR's awareness.
                from datetime import timezone
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
                
                points.append(WeatherDataPoint(
                    timestamp=timestamp,
                    lat=lat,
                    lon=lon,
                    source=WeatherSource.OPEN_METEO,
                    temperature=temps[i],
                    precipitation=precips[i]
                ))
        except Exception as e:
             print(f"Error transforming Open-Meteo data: {e}")

        return points

    @staticmethod
    def calculate_consensus(points: List[WeatherDataPoint]) -> List[ConsensusDataPoint]:
        """
        Calculates a consensus temperature based on weighted sources.
        YR: 0.6
        Open-Meteo: 0.4
        """
        grouped = {}
        # Group by timestamp (assuming lat/lon are consistent for the batch)
        for p in points:
            key = p.timestamp
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(p)
            
        consensus_points = []
        
        for ts, group in grouped.items():
            if not group:
                continue
                
            lat = group[0].lat
            lon = group[0].lon
            
            yr_temp = next((p.temperature for p in group if p.source == WeatherSource.YR_NO), None)
            om_temp = next((p.temperature for p in group if p.source == WeatherSource.OPEN_METEO), None)
            
            weighted_sum = 0.0
            total_weight = 0.0
            
            if yr_temp is not None:
                weighted_sum += yr_temp * 0.6
                total_weight += 0.6
                
            if om_temp is not None:
                weighted_sum += om_temp * 0.4
                total_weight += 0.4
            
            if total_weight > 0:
                final_temp = weighted_sum / total_weight
                consensus_points.append(ConsensusDataPoint(
                    timestamp=ts,
                    lat=lat,
                    lon=lon,
                    weighted_temperature=final_temp,
                    source_count=len(group)
                ))
                
        return consensus_points
