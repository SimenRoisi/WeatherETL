from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "WeatherETL"
    
    # API Configurations
    YR_NO_BASE_URL: str = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1/forecast"
    OPEN_METEO_GEOCODING_URL: str = "https://geocoding-api.open-meteo.com/v1/search"
    
    # Identification
    USER_AGENT: str = "WeatherETL/1.0 (https://github.com/yourusername/weather-etl)"

    class Config:
        env_file = ".env"

settings = Settings()
