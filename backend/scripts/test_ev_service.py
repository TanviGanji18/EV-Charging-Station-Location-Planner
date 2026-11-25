import sys
import json

from pathlib import Path

# Add backend directory to Python path
BASE_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(BASE_DIR))

from app.services.ev_station_service import (
    get_nearby_ev_stations
)


# Test a new international location
latitude = 48.8566
longitude = 2.3522

result = get_nearby_ev_stations(
    latitude=latitude,
    longitude=longitude,
    radius_km=10,
    max_results=100
)

print("=" * 60)
print("EV STATION SERVICE TEST")
print("=" * 60)

print("\nTest Location: Paris, France")

print("Search Location:", result["search_location"])

print("Search Radius:", result["radius_km"], "km")

print("Total Stations:", result["total_stations"])

print(
    "Result Limit Reached:",
    result["result_limit_reached"]
)

print("\nFIRST FIVE STATIONS:")

for station in result["stations"][:5]:

    print("\n" + "-" * 50)

    print("Station ID:", station["station_id"])

    print("Station Name:", station["station_name"])

    print("Country:", station["country"])

    print("Latitude:", station["latitude"])

    print("Longitude:", station["longitude"])

    print("Distance:", station["distance_km"], "km")

    print("Operator:", station["operator"])

    print("Charging Points:", station["charging_points"])

    print("Connector Types:", station["connector_types"])

    print("Maximum Power:", station["max_power_kw"], "kW")

    print("Reported Status:", station["operational_status"])

    print("Last Verified:", station["last_verified"])


# Save structured response for testing
output_dir = BASE_DIR / "data" / "processed"

output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / "ev_service_test_paris.json"

with open(output_file, "w", encoding="utf-8") as file:

    json.dump(
        result,
        file,
        indent=4,
        ensure_ascii=False
    )

print("\n" + "=" * 60)

print("SERVICE TEST COMPLETED")

print("Output File:", output_file)

print("=" * 60)