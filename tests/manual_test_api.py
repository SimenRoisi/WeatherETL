import requests
import time
import subprocess
import sys
import threading

def run_server():
    subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8001"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def test_api():
    base_url = "http://127.0.0.1:8001"
    
    # Needs to wait for server
    print("Waiting for server to start...")
    time.sleep(5)
    
    try:
        # Test 1: Health
        print("Testing Root...")
        r = requests.get(f"{base_url}/")
        print(f"Root: {r.status_code}")
        
        # Test 2: Current Weather (will trigger ETL)
        # Using Bergen to ensure fresh data
        lat, lon = 60.39, 5.32
        print(f"\nTesting Current Weather for Bergen ({lat}, {lon})...")
        r = requests.get(f"{base_url}/api/v1/weather/current", params={"lat": lat, "lon": lon})
        if r.status_code == 200:
            data = r.json()
            print("Success!")
            print(f"Avg Temp: {data.get('average_temperature')}")
            print(f"Sources: {len(data.get('sources', []))}")
        else:
            print(f"Failed: {r.status_code} - {r.text}")

        # Test 3: Daily Average
        print("\nTesting Daily Average (Oslo)...")
        # Need to ensure Oslo data exists first, hit current endpoint again just in case
        requests.get(f"{base_url}/api/v1/weather/current", params={"lat": 59.91, "lon": 10.75})
        
        r = requests.get(f"{base_url}/api/v1/weather/daily-average", params={"location": "oslo"})
        if r.status_code == 200:
            print("Success!", r.json())
        else:
            print(f"Failed: {r.status_code} - {r.text}")

    except Exception as e:
        print(f"Test failed with exception: {e}")

if __name__ == "__main__":
    # Start server in separate thread/process
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    test_api()
