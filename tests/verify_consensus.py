from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.etl.transform import WeatherTransformer
from app.models.schemas import WeatherDataPoint, WeatherSource

def test_consensus_calculation():
    now = datetime.utcnow()
    lat = 59.91
    lon = 10.75
    
    # Simulate data
    points = [
        # Source 1: YR (10.0 degrees)
        WeatherDataPoint(
            timestamp=now,
            lat=lat,
            lon=lon,
            source=WeatherSource.YR_NO,
            temperature=10.0
        ),
        # Source 2: Open-Meteo (20.0 degrees)
        WeatherDataPoint(
            timestamp=now,
            lat=lat,
            lon=lon,
            source=WeatherSource.OPEN_METEO,
            temperature=20.0
        )
    ]
    
    # Expected weighted average:
    # (10.0 * 0.6) + (20.0 * 0.4) = 6.0 + 8.0 = 14.0
    # Denominator = 1.0
    
    consensus = WeatherTransformer.calculate_consensus(points)
    
    assert len(consensus) == 1, "Should produce 1 consensus point"
    result = consensus[0]
    
    print(f"YR Temp: 10.0")
    print(f"OM Temp: 20.0")
    print(f"Calculated Weighted Temp: {result.weighted_temperature}")
    
    assert abs(result.weighted_temperature - 14.0) < 0.001, f"Expected 14.0, got {result.weighted_temperature}"
    print("✅ Consensus calculation verified!")

if __name__ == "__main__":
    test_consensus_calculation()
