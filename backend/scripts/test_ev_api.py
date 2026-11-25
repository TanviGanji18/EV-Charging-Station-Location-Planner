import os
import requests
import json

from pathlib import Path
from dotenv import load_dotenv

# Backend directory
BASE_DIR = Path(__file__).resolve().parents[1]

# Load environment variables
load_dotenv(BASE_DIR / ".env")

# Retrieve API key
API_KEY = os.getenv("OPEN_CHARGE_MAP_API_KEY")

if not API_KEY:
    raise ValueError("Open Charge Map API key not found")

# Open Charge Map API endpoint
URL = "https://api.openchargemap.io/v3/poi/"

# Request parameters
params = {
    "output": "json",
    "latitude": 51.5074,
    "longitude": -0.1278,
    "distance": 10,
    "distanceunit": "KM",
    "maxresults": 100
}

# Authentication headers
headers = {
    "X-API-Key": API_KEY
}

# Send API request
response = requests.get(
    URL,
    params=params,
    headers=headers,
    timeout=30
)

print("Status Code:", response.status_code)

response.raise_for_status()

# Convert response into Python data
stations = response.json()

print("Total Stations Retrieved:", len(stations))

# Create output directory
output_dir = BASE_DIR / "data" / "raw"
output_dir.mkdir(parents=True, exist_ok=True)

# Save original API response
output_file = output_dir / "ev_stations_london.json"

with open(output_file, "w", encoding="utf-8") as file:
    json.dump(stations, file, indent=4, ensure_ascii=False)

print("Data saved successfully:", output_file)

# Display first five charging stations
for station in stations[:5]:

    address = station.get("AddressInfo") or {}

    print("\n----------------------------")
    print("Station ID:", station.get("ID"))
    print("Station Name:", address.get("Title"))
    print("Latitude:", address.get("Latitude"))
    print("Longitude:", address.get("Longitude"))
    print("Address:", address.get("AddressLine1"))
    print("Charging Points:", station.get("NumberOfPoints"))