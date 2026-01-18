from sqlalchemy import Column, Integer, String, Float, DateTime
from app.core.database import Base

class WeatherTable(Base):
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    lat = Column(Float)
    lon = Column(Float)
    source = Column(String)
    temperature = Column(Float)
    precipitation = Column(Float)
