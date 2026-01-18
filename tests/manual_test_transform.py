from app.etl.transform import WeatherTransformer
from app.models.schemas import WeatherSource
import json
from datetime import datetime

def test_transforms():
    # Mock Yr.no data
    yr_mock = {
        "properties": {
            "timeseries": [
                {
                    "time": "2026-01-12T12:00:00Z",
                    "data": {
                        "instant": {"details": {"air_temperature": 5.0}},
                        "next_1_hours": {"details": {"precipitation_amount": 0.5}}
                    }
                }
            ]
        }
    }
    
    print("Testing Yr.no Transform...")
    points = WeatherTransformer.transform_yr(yr_mock, 59.91, 10.75)
    if points and points[0].temperature == 5.0 and points[0].source == WeatherSource.YR_NO:
        print("Yr.no Transform Success!")
        print(points[0])
    else:
        print("Yr.no Transform Failed")

    # Mock Open-Meteo data
    om_mock = {
        "hourly": {
            "time": ["2026-01-12T12:00:00"],
            "temperature_2m": [3.5],
            "precipitation": [0.0]
        }
    }

    print("\nTesting Open-Meteo Transform...")
    points = WeatherTransformer.transform_open_meteo(om_mock, 59.91, 10.75)
    if points and points[0].temperature == 3.5 and points[0].source == WeatherSource.OPEN_METEO:
        print("Open-Meteo Transform Success!")
        print(points[0])
    else:
        print("Open-Meteo Transform Failed")

if __name__ == "__main__":
    test_transforms()
