# WeatherETL

A production-ready Weather ETL pipeline that extracts data from yr.no and open-meteo.com, transforms and normalizes the data, and loads it into a database. This project demonstrates end-to-end ETL pipeline knowledge and data engineering best practices.

## 🎯 Project Goal

The goal is to systematically compare and normalize weather data from multiple sources (yr.no and open-meteo.com) to provide more robust weather estimates. This project showcases ETL pipeline development, data engineering, and API design skills.

## 🏗️ Architecture

### Extract
- Multiple weather APIs (yr.no, open-meteo.com)
- Different timezones, coordinate formats, and variable names
- Robust error handling and rate limiting

### Transform
- Time normalization across sources
- Spatial normalization (lat/lon vs location names)
- Unit conversion (m/s vs km/h, mm vs cm, etc.)
- Variable normalization (precipitation vs precipitation_amount)
- Data quality checks (missing values, outliers)

### Load
- Raw tables per source
- Normalized tables per source
- Aggregated views
- Optimized indexing for time and location queries

### Aggregation
- Simple average as baseline
- Weighted average based on historic deviation
- Confidence intervals based on source reliability

## 🚀 Live API

**Deployed on Vercel**: [https://weather-etl.vercel.app](https://weather-etl.vercel.app)

**API Documentation**: [https://weather-etl.vercel.app/docs](https://weather-etl.vercel.app/docs)

### Example Endpoints

```
GET /weather/current?lat=59.9139&lon=10.7522
GET /weather/daily-average?location=Oslo
GET /weather/source-deviation?date=2026-01-10
```

## 🛠️ Local Development

### Prerequisites
- Python 3.9+
- pip

### Setup

1. **Clone the repository**:
```bash
git clone https://github.com/SimenRoisi/WeatherETL.git
cd WeatherETL
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run the development server**:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Environment Variables

Copy `.env.example` to `.env` and configure as needed:
```bash
cp .env.example .env
```

For local development, the default SQLite database will be used automatically.

## 📊 Tech Stack

- **FastAPI** - Modern Python web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **SQLite/PostgreSQL** - Database (SQLite for local, Postgres for production)
- **Vercel** - Serverless deployment platform
- **Mangum** - ASGI adapter for serverless functions
- **Pydantic** - Data validation using Python type annotations

## 📁 Project Structure

```
WeatherETL/
├── app/
│   ├── api/           # API routes and endpoints
│   ├── core/          # Core configuration and database
│   ├── etl/           # ETL pipeline (extract, transform, load)
│   ├── models/        # Data models and schemas
│   └── main.py        # FastAPI application entry point
├── api/
│   └── index.py       # Vercel serverless entry point
├── tests/             # Test files
├── requirements.txt   # Python dependencies
├── vercel.json        # Vercel deployment configuration
└── README.md
```

## 🚢 Deployment

This project is configured for deployment on Vercel:

1. Push to GitHub
2. Import project in Vercel dashboard
3. Vercel will automatically detect the configuration
4. (Optional) Add Vercel Postgres database for production persistence

## 📝 License

This project is part of my portfolio showcasing data engineering and ETL pipeline development skills.

---

**Author**: Simen Roisi  
**Website**: [simenroisi.dev](https://simenroisi.dev)
