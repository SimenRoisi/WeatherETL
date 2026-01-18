import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.core.config import settings

class WeatherFetcher(ABC):
    """Abstract base class for weather data fetchers."""
    
    @abstractmethod
    def fetch_forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Fetch weather forecast for a given latitude and longitude.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Raw JSON response as a dictionary.
        """
        pass

class YrNoFetcher(WeatherFetcher):
    """Fetcher for Yr.no (MET Norway)."""
    
    def fetch_forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        headers = {
            "User-Agent": settings.USER_AGENT
        }
        params = {
            "lat": lat,
            "lon": lon
        }
        
        try:
            response = requests.get(settings.YR_NO_BASE_URL, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching from Yr.no: {e}")
            raise

class OpenMeteoFetcher(WeatherFetcher):
    """Fetcher for Open-Meteo."""
    
    def fetch_forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,precipitation",
            "timezone": "auto"
        }
        
        try:
            response = requests.get(settings.OPEN_METEO_BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching from Open-Meteo: {e}")
            raise

class GeocodingFetcher:
    """Fetcher for Open-Meteo Geocoding API."""
    
    def search(self, query: str) -> Dict[str, Any]:
        params = {
            "name": query,
            "count": 10,
            "language": "en",
            "format": "json"
        }
        
        try:
            response = requests.get(settings.OPEN_METEO_GEOCODING_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching from Open-Meteo Geocoding: {e}")
            raise
