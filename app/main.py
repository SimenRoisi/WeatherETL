import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.v1.weather import router as weather_router
from app.core.database import init_db

app = FastAPI(title="WeatherETL", description="A weather data ETL pipeline API")

# Initialize database tables on startup
@app.on_event("startup")
def startup_event():
    init_db()

app.include_router(weather_router, prefix="/api/v1", tags=["weather"])

# Mount static files directory
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/health")
def health_check():
    return {"status": "healthy"}
