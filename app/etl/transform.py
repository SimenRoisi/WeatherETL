from typing import List, Dict, Any
from datetime import datetime
from app.models.schemas import WeatherDataPoint, WeatherSource
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
                # OpenMeteo returns naive local time if timezone is not UTC, 
                # but we requested auto timezone or can assume UTC if 'isodate' used.
                # The 'time' field in OpenMeteo is ISO8601 but without offset if timezone is not specified.
                # However, our extractor requests timezone='auto', let's stick to safe parsing.
                
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
