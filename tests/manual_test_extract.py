from app.etl.extract import YrNoFetcher, OpenMeteoFetcher
import json

def test_fetchers():
    # Oslo coordinates
    lat = 59.91
    lon = 10.75
    
    print("Testing YrNoFetcher...")
    yr = YrNoFetcher()
    try:
        data = yr.fetch_forecast(lat, lon)
        print("Yr.no Response (keys):", data.keys())
        if 'properties' in data:
            print("Yr.no Success!")
    except Exception as e:
        print(f"Yr.no Failed: {e}")

    print("\nTesting OpenMeteoFetcher...")
    om = OpenMeteoFetcher()
    try:
        data = om.fetch_forecast(lat, lon)
        print("OpenMeteo Response (keys):", data.keys())
        if 'hourly' in data:
            print("OpenMeteo Success!")
    except Exception as e:
        print(f"OpenMeteo Failed: {e}")

if __name__ == "__main__":
    test_fetchers()
