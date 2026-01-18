from fastapi import FastAPI
from app.api.v1.weather import router as weather_router
from app.core.database import init_db

app = FastAPI(title="WeatherETL", description="A weather data ETL pipeline API")

# Initialize database tables on startup
@app.on_event("startup")
def startup_event():
    init_db()

app.include_router(weather_router, prefix="/api/v1", tags=["weather"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the WeatherETL API", "docs": "/docs"}
