from typing import List
from sqlalchemy.orm import Session
from app.models.schemas import WeatherDataPoint
from app.models.sql_models import WeatherTable, Base
from app.core.database import engine

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

class WeatherLoader:
    def __init__(self, db: Session):
        self.db = db

    def load_data(self, points: List[WeatherDataPoint]):
        """
        Loads a list of WeatherDataPoints into the database.
        Merges duplicates based on business keys if implemented, 
        currently does simple inserts.
        """
        for point in points:
            # Check for existing record to avoid duplicates (naive approach)
            # In a real high-throughput scenario, use "upsert" or unique constraints.
            # We assume (timestamp, lat, lon, source) is unique.
            existing = self.db.query(WeatherTable).filter(
                WeatherTable.timestamp == point.timestamp,
                WeatherTable.lat == point.lat,
                WeatherTable.lon == point.lon,
                WeatherTable.source == point.source
            ).first()

            if existing:
                # Update existing record
                existing.temperature = point.temperature
                existing.precipitation = point.precipitation
            else:
                # Create new record
                db_item = WeatherTable(
                    timestamp=point.timestamp,
                    lat=point.lat,
                    lon=point.lon,
                    source=point.source,
                    temperature=point.temperature,
                    precipitation=point.precipitation
                )
                self.db.add(db_item)
        
        try:
            self.db.commit()
            print(f"Successfully loaded {len(points)} records.")
        except Exception as e:
            self.db.rollback()
            print(f"Error loading data: {e}")
            raise
