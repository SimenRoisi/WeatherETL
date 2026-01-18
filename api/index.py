"""
Vercel serverless function entry point for FastAPI application.
This file adaptations the FastAPI ASGI app to work with Vercel's serverless runtime.
"""
from app.main import app

# Vercel's Python runtime will automatically detect the 'app' object
# and serve it as a FastAPI/ASGI application.

