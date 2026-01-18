from typing import Tuple, Optional
from sqlalchemy.orm import Session
from app.etl.extract import YrNoFetcher, OpenMeteoFetcher
from app.etl.transform import WeatherTransformer
from app.etl.load import WeatherLoader

# Simple hardcoded location mapping
LOCATIONS = {
    "oslo": (59.91, 10.75),
    "bergen": (60.39, 5.32),
    "trondheim": (63.43, 10.39),
    "stavanger": (58.97, 5.73),
    "kristiansand": (58.15, 8.02),
    "tromsø": (69.65, 18.96)
}

def resolve_location(name: str) -> Optional[Tuple[float, float]]:
    """Resolves a location name to (lat, lon)."""
    return LOCATIONS.get(name.lower())

def run_etl_pipeline(lat: float, lon: float, db: Session):
    """
    Runs the full Extract -> Transform -> Load pipeline for a specific location.
    """
    print(f"Triggering ETL pipeline for {lat}, {lon}")
    
    # 1. Extract
    try:
        yr_fetcher = YrNoFetcher()
        om_fetcher = OpenMeteoFetcher()
        
        yr_data = yr_fetcher.fetch_forecast(lat, lon)
        om_data = om_fetcher.fetch_forecast(lat, lon)
    except Exception as e:
        print(f"Extraction failed: {e}")
        raise e

    # 2. Transform
    try:
        yr_points = WeatherTransformer.transform_yr(yr_data, lat, lon)
        om_points = WeatherTransformer.transform_open_meteo(om_data, lat, lon)
        all_points = yr_points + om_points
    except Exception as e:
        print(f"Transformation failed: {e}")
        raise e

    # 3. Load
    try:
        loader = WeatherLoader(db)
        loader.load_data(all_points)
    except Exception as e:
        print(f"Loading failed: {e}")
        raise e
        
    return len(all_points)
