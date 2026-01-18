import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.etl.extract import YrNoFetcher, OpenMeteoFetcher
from app.etl.transform import WeatherTransformer

def trace_etl_for_berlin():
    # Berlin Coordinates
    lat = 52.52
    lon = 13.40
    
    print(f"--- 1. EXTRACTION (Berlin: {lat}, {lon}) ---")
    
    # 1. Fetch Raw Data
    yr_fetcher = YrNoFetcher()
    om_fetcher = OpenMeteoFetcher()
    
    print("\nFetching raw data from YR.no...")
    yr_raw = yr_fetcher.fetch_forecast(lat, lon)
    # Print a snippet of YR structure (nested)
    yr_snippet = {
        "type": yr_raw.get("type"),
        "properties": {
            "timeseries": [
                yr_raw["properties"]["timeseries"][0] # Just show first hour
            ]
        }
    }
    print("YR.no RAW JSON Structure (Truncated):")
    print(json.dumps(yr_snippet, indent=2))
    
    print("\nFetching raw data from Open-Meteo...")
    om_raw = om_fetcher.fetch_forecast(lat, lon)
    # Print a snippet of Open-Meteo structure (arrays)
    om_snippet = {
        "hourly": {
            "time": om_raw["hourly"]["time"][:1], # First item
            "temperature_2m": om_raw["hourly"]["temperature_2m"][:1],
            "precipitation": om_raw["hourly"]["precipitation"][:1]
        }
    }
    print("Open-Meteo RAW JSON Structure (Truncated):")
    print(json.dumps(om_snippet, indent=2))
    
    print("\n--- 2. NORMALIZATION & TRANSFORMATION ---")
    
    # 2. Transform to Unified Model
    print("\nNormalizing YR data...")
    yr_points = WeatherTransformer.transform_yr(yr_raw, lat, lon)
    print(f"-> Converted to {len(yr_points)} WeatherDataPoint objects.")
    print(f"Example Point 1: {yr_points[0]}")
    
    print("\nNormalizing Open-Meteo data...")
    om_points = WeatherTransformer.transform_open_meteo(om_raw, lat, lon)
    print(f"-> Converted to {len(om_points)} WeatherDataPoint objects.")
    print(f"Example Point 1: {om_points[0]}")
    
    all_points = yr_points + om_points
    
    print("\n--- 3. AGGREGATION (Consensus) ---")
    
    # 3. Calculate Consensus
    print("Calculating Weighted Consensus...")
    consensus_points = WeatherTransformer.calculate_consensus(all_points)
    
    # Find the consensus corresponding to the first timestamp we looked at
    target_ts = yr_points[0].timestamp
    matching_consensus = next((p for p in consensus_points if p.timestamp == target_ts), None)
    
    print(f"Found {len(consensus_points)} consensus points.")
    if matching_consensus:
        print(f"\nConsensus Result for {target_ts}:")
        print(f"YR Temp: {yr_points[0].temperature} (Weight 0.6)")
        
        # Find matching OM point
        om_p = next((p for p in om_points if p.timestamp.replace(tzinfo=None) == target_ts.replace(tzinfo=None)), None)
        if om_p:
            print(f"Open-Meteo Temp: {om_p.temperature} (Weight 0.4)")
            
        print(f"FINAL WEIGHTED TEMP: {matching_consensus.weighted_temperature:.4f}")
        print(f"Consensus Object: {matching_consensus}")

if __name__ == "__main__":
    trace_etl_for_berlin()
