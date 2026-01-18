from app.etl.extract import GeocodingFetcher
import json

def test_geocoding():
    fetcher = GeocodingFetcher()
    
    queries = ["Oslo", "Santa Cruz", "Los Angeles"]
    
    for q in queries:
        print(f"\nSearching for '{q}'...")
        try:
            data = fetcher.search(q)
            if "results" in data:
                print(f"Found {len(data['results'])} results.")
                for item in data['results'][:3]: # Show top 3
                    print(f" - {item.get('name')}, {item.get('country')} ({item.get('latitude')}, {item.get('longitude')})")
            else:
                print("No results found.")
        except Exception as e:
            print(f"Search Failed: {e}")

if __name__ == "__main__":
    test_geocoding()
