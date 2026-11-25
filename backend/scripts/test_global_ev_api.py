import os
import json
import time
import requests

from pathlib import Path
from dotenv import load_dotenv

# Backend directory
BASE_DIR = Path(__file__).resolve().parents[1]

# Load API key
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("OPEN_CHARGE_MAP_API_KEY")

if not API_KEY:
    raise ValueError("API key not found")

# API endpoint
URL = "https://api.openchargemap.io/v3/poi/"

headers = {
    "X-API-Key": API_KEY
}

# Cities for testing
cities = {
    "Hyderabad": (17.3850, 78.4867),
    "London": (51.5074, -0.1278),
    "New_York": (40.7128, -74.0060),
    "Tokyo": (35.6762, 139.6503),
    "Dubai": (25.2048, 55.2708),
    "Sydney": (-33.8688, 151.2093)
}

# Output directory
output_dir = BASE_DIR / "data" / "raw"
output_dir.mkdir(parents=True, exist_ok=True)

# Store unique stations
all_stations = {}

# Retrieve data for each city
for city, coordinates in cities.items():

    latitude, longitude = coordinates

    print(f"\nFetching stations in {city}...")

    params = {
        "output": "json",
        "latitude": latitude,
        "longitude": longitude,
        "distance": 10,
        "distanceunit": "KM",
        "maxresults": 100
    }

    try:
        response = requests.get(
            URL,
            params=params,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        stations = response.json()

        print("Status Code:", response.status_code)
        print("Stations Retrieved:", len(stations))

        # Save individual city data
        file_path = output_dir / f"ev_stations_{city.lower()}.json"

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(
                stations,
                file,
                indent=4,
                ensure_ascii=False
            )

        # Combine unique stations
        for station in stations:
            station_id = station.get("ID")

            if station_id is not None:
                all_stations[station_id] = station

        print("Data saved successfully")

    except requests.RequestException as error:
        print(f"Request failed for {city}: {error}")

    # Small delay between requests
    time.sleep(2)

# Save combined dataset
combined_file = output_dir / "global_ev_stations_sample.json"

with open(combined_file, "w", encoding="utf-8") as file:
    json.dump(
        list(all_stations.values()),
        file,
        indent=4,
        ensure_ascii=False
    )

print("\n==============================")
print("DATA COLLECTION COMPLETED")
print("Total Unique Stations:", len(all_stations))
print("Combined File:", combined_file)
print("==============================")