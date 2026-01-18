"""
Vercel serverless function entry point for FastAPI application.
This file adapts the FastAPI ASGI app to work with Vercel's serverless runtime.
"""
from mangum import Mangum
from app.main import app

# Mangum handler converts ASGI (FastAPI) to AWS Lambda/Vercel format
handler = Mangum(app, lifespan="off")
