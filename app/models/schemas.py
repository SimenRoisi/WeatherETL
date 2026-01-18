from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Optional

class WeatherSource(str, Enum):
    YR_NO = "yr"
    OPEN_METEO = "open-meteo"

class WeatherDataPoint(BaseModel):
    timestamp: datetime
    lat: float
    lon: float
    source: WeatherSource
    temperature: float
    precipitation: float = 0.0

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2026-01-12T12:00:00Z",
                "lat": 59.91,
                "lon": 10.75,
                "source": "yr",
                "temperature": 1.5,
                "precipitation": 0.2
            }
        }

class LocationSearchResult(BaseModel):
    name: str
    lat: float
    lon: float
    country: str
    region: Optional[str] = None
