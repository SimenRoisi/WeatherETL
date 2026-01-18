from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from typing import List, Optional

from app.core.database import get_db
from app.models.sql_models import WeatherTable
from app.core.utils import run_etl_pipeline, resolve_location

router = APIRouter()

@router.get("/weather/current")
def get_current_weather(
    lat: float, 
    lon: float, 
    db: Session = Depends(get_db)
):
    """
    Get current weather for specific coordinates.
    Triggers ETL if data is missing for the current hour.
    """
    now = datetime.utcnow()
    # Simple check: do we have data for this hour?
    # Rounding down to hour for simplicity in this demo logic
    current_hour_start = now.replace(minute=0, second=0, microsecond=0)
    
    records = db.query(WeatherTable).filter(
        WeatherTable.lat.between(lat - 0.0001, lat + 0.0001),
        WeatherTable.lon.between(lon - 0.0001, lon + 0.0001),
        WeatherTable.timestamp >= current_hour_start
    ).all()
    
    if not records:
        # Trigger ETL
        try:
            run_etl_pipeline(lat, lon, db)
            # Query again with fuzzy match
            records = db.query(WeatherTable).filter(
                WeatherTable.lat.between(lat - 0.0001, lat + 0.0001),
                WeatherTable.lon.between(lon - 0.0001, lon + 0.0001),
                WeatherTable.timestamp >= current_hour_start
            ).all()
        except Exception as e:
            # Log the specific error for debugging
            print(f"ETL Failure Detail: {e}")
            raise HTTPException(status_code=500, detail=f"ETL Pipeline failed: {str(e)}")

    if not records:
         raise HTTPException(status_code=404, detail="No weather data available even after ETL attempt.")

    # Aggregate
    temps = [r.temperature for r in records if r.temperature is not None]
    avg_temp = sum(temps) / len(temps) if temps else None
    
    return {
        "location": {"lat": lat, "lon": lon},
        "average_temperature": avg_temp,
        "sources": [
            {
                "source": r.source,
                "temperature": r.temperature, 
                "timestamp": r.timestamp
            } for r in records
        ]
    }

@router.get("/weather/daily-average")
def get_daily_average(
    location: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    Get daily average temperature for a location.
    """
    if location:
        coords = resolve_location(location)
        if not coords:
            raise HTTPException(status_code=400, detail=f"Unknown location: {location}")
        lat, lon = coords
    
    if lat is None or lon is None:
        raise HTTPException(status_code=400, detail="Must provide location name or lat/lon")
        
    # Aggregate by date
    # SQLite has limited date functions, using strftime
    results = db.query(
        func.strftime("%Y-%m-%d", WeatherTable.timestamp).label("date"),
        func.avg(WeatherTable.temperature).label("avg_temp"),
        func.avg(WeatherTable.precipitation).label("avg_precip")
    ).filter(
        WeatherTable.lat.between(lat - 0.0001, lat + 0.0001),
        WeatherTable.lon.between(lon - 0.0001, lon + 0.0001)
    ).group_by(
        func.strftime("%Y-%m-%d", WeatherTable.timestamp)
    ).all()
    
    return [
        {
            "date": r.date,
            "average_temperature": r.avg_temp,
            "average_precipitation": r.avg_precip
        }
        for r in results
    ]

@router.get("/weather/source-deviation")
def get_source_deviation(
    date: date,
    location: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    Compare sources for a specific date.
    """
    if location:
        coords = resolve_location(location)
        if not coords:
            raise HTTPException(status_code=400, detail=f"Unknown location: {location}")
        lat, lon = coords
        
    if lat is None or lon is None:
         raise HTTPException(status_code=400, detail="Must provide location name or lat/lon")

    # Filter by date string matching
    date_str = date.strftime("%Y-%m-%d")
    
    records = db.query(WeatherTable).filter(
        WeatherTable.lat.between(lat - 0.0001, lat + 0.0001),
        WeatherTable.lon.between(lon - 0.0001, lon + 0.0001),
        func.strftime("%Y-%m-%d", WeatherTable.timestamp) == date_str
    ).all()
    
    # Group by source
    by_source = {}
    for r in records:
        if r.source not in by_source:
            by_source[r.source] = []
        if r.temperature is not None:
            by_source[r.source].append(r.temperature)
            
    avgs = {s: sum(v)/len(v) for s, v in by_source.items() if v}
    
    deviation = None
    if "yr" in avgs and "open-meteo" in avgs:
        deviation = abs(avgs["yr"] - avgs["open-meteo"])
        
    return {
        "date": date_str,
        "location": {"lat": lat, "lon": lon},
        "source_averages": avgs,
        "deviation_yr_vs_openmeteo": deviation
    }

@router.get("/weather/search")
def search_location(
    name: str = Query(..., min_length=2, description="Name of the location to search for")
):
    """
    Search for a location by name.
    """
    from app.etl.extract import GeocodingFetcher
    from app.models.schemas import LocationSearchResult
    
    fetcher = GeocodingFetcher()
    try:
        data = fetcher.search(name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geocoding service failed: {str(e)}")
        
    results = []
    if "results" in data:
        for item in data["results"]:
            results.append(LocationSearchResult(
                name=item.get("name"),
                lat=item.get("latitude"),
                lon=item.get("longitude"),
                country=item.get("country", "Unknown"),
                region=item.get("admin1")
            ))
            
    return results
