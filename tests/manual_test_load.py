from datetime import datetime, timezone
from app.etl.load import WeatherLoader
from app.models.schemas import WeatherDataPoint, WeatherSource
from app.core.database import SessionLocal, engine, Base
from app.models.sql_models import WeatherTable

def test_load():
    # Setup fresh DB for verification
    # Drop tables to ensure clean slate if running multiple times locally
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    loader = WeatherLoader(db)
    
    # Create mock data
    points = [
        WeatherDataPoint(
            timestamp=datetime(2026, 1, 12, 12, 0, 0),
            lat=59.91,
            lon=10.75,
            source=WeatherSource.YR_NO,
            temperature=5.5,
            precipitation=0.0
        ),
        WeatherDataPoint(
            timestamp=datetime(2026, 1, 12, 13, 0, 0),
            lat=59.91,
            lon=10.75,
            source=WeatherSource.YR_NO,
            temperature=6.0,
            precipitation=0.1
        )
    ]
    
    print("Loading data...")
    loader.load_data(points)
    
    # Verify data in DB
    print("Verifying data in DB...")
    rows = db.query(WeatherTable).all()
    print(f"Found {len(rows)} rows.")
    for row in rows:
        print(f"ID: {row.id}, Time: {row.timestamp}, Temp: {row.temperature}, Source: {row.source}")
        
    if len(rows) == 2:
        print("Load Layer Success!")
    else:
        print("Load Layer Failed: count mismatch")

    # Test Update (Upsert) Logic
    print("\nTesting Update Logic...")
    updated_points = [
        WeatherDataPoint(
            timestamp=datetime(2026, 1, 12, 12, 0, 0),
            lat=59.91,
            lon=10.75,
            source=WeatherSource.YR_NO,
            temperature=10.0, # Changed temp
            precipitation=0.0
        )
    ]
    loader.load_data(updated_points)
    
    updated_row = db.query(WeatherTable).filter(
        WeatherTable.timestamp == datetime(2026, 1, 12, 12, 0, 0),
        WeatherTable.source == "yr"
    ).first()
    
    print(f"Updated Row Temp: {updated_row.temperature}")
    if updated_row.temperature == 10.0:
        print("Update Logic Success!")
    else:
        print("Update Logic Failed")

    db.close()

if __name__ == "__main__":
    test_load()
