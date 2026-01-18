import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get database URL from environment, default to SQLite for local development
# In serverless environments (Vercel), use /tmp directory which is writable
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Check if we're in a serverless environment (Vercel sets VERCEL env var)
    if os.getenv("VERCEL"):
        # Use /tmp directory in serverless environment (only writable location)
        DATABASE_URL = "sqlite:////tmp/weather.db"
    else:
        # Local development
        DATABASE_URL = "sqlite:///./weather.db"

# SQLite requires special connect_args, PostgreSQL does not
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    # For PostgreSQL or other databases
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables. Call this on app startup."""
    Base.metadata.create_all(bind=engine)
