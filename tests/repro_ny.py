from app.etl.extract import YrNoFetcher, OpenMeteoFetcher
from app.etl.transform import WeatherTransformer
from app.etl.load import WeatherLoader
from app.core.database import SessionLocal, engine, Base

import traceback

def test_ny():
    lat = 40.71427
    lon = -74.00597
    
    print(f"Testing for NY: {lat}, {lon}")
    
    # 1. Test Fetchers
    print("\n--- Fetching ---")
    try:
        print("Fetching Yr.no...")
        yr = YrNoFetcher()
        yr_data = yr.fetch_forecast(lat, lon)
        print("Yr.no Success")
    except Exception as e:
        print(f"Yr.no Failed: {e}")
        traceback.print_exc()
        yr_data = None

    try:
        print("Fetching OpenMeteo...")
        om = OpenMeteoFetcher()
        om_data = om.fetch_forecast(lat, lon)
        print("OpenMeteo Success")
    except Exception as e:
        print(f"OpenMeteo Failed: {e}")
        traceback.print_exc()
        om_data = None

    # 2. Test Transform
    print("\n--- Transforming ---")
    yr_points = []
    om_points = []
    
    if yr_data:
        try:
            yr_points = WeatherTransformer.transform_yr(yr_data, lat, lon)
            print(f"Yr Points: {len(yr_points)}")
        except Exception as e:
            print(f"Yr Transform Failed: {e}")
            traceback.print_exc()

    if om_data:
        try:
            om_points = WeatherTransformer.transform_open_meteo(om_data, lat, lon)
            print(f"OM Points: {len(om_points)}")
        except Exception as e:
            print(f"OM Transform Failed: {e}")
            traceback.print_exc()

    # 3. Test Load (if we have points)
    if yr_points or om_points:
        print("\n--- Loading ---")
        try:
            db = SessionLocal()
            loader = WeatherLoader(db)
            loader.load_data(yr_points + om_points)
            print("Load Success")
            
            # 4. Test Query (Current API Logic)
            print("\n--- Querying (Exact Match) ---")
            from app.models.sql_models import WeatherTable
            from datetime import datetime
            
            # Using fresh float values to simulate API request
            query_lat = float("40.71427")
            query_lon = float("-74.00597")
            
            records = db.query(WeatherTable).filter(
                WeatherTable.lat == query_lat,
                WeatherTable.lon == query_lon
            ).all()
            
            print(f"Query Result Count: {len(records)}")
            if len(records) == 0:
                print("QUERY FAILED: Exact float match failed!")
                
                # Check what is actually there
                all_recs = db.query(WeatherTable).limit(5).all()
                print("First 5 records in DB:")
                for r in all_recs:
                    print(f"Lat: {r.lat}, Lon: {r.lon}")
            else:
                print("QUERY SUCCESS")

            db.close()
        except Exception as e:
            print(f"Load/Query Failed: {e}")
            traceback.print_exc()
    else:
        print("No points to load.")

if __name__ == "__main__":
    test_ny()
