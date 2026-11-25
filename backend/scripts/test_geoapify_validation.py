import os
import time
import requests

from pathlib import Path
from dotenv import load_dotenv


# --------------------------------------------------
# 1. Load API key
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GEOAPIFY_API_KEY")

if not API_KEY:
    raise ValueError("Geoapify API key not found")


# --------------------------------------------------
# 2. API configuration
# --------------------------------------------------

BASE_URL = "https://api.geoapify.com/v2/places"

LIMIT = 100

ALL_CATEGORIES = (
    "commercial.shopping_mall,"
    "commercial.supermarket,"
    "parking.cars,"
    "catering.restaurant,"
    "catering.cafe,"
    "accommodation.hotel,"
    "service.vehicle.fuel,"
    "healthcare.hospital,"
    "office,"
    "service.vehicle.charging_station"
)


# --------------------------------------------------
# 3. Define validation tests
# --------------------------------------------------

tests = [
    {
        "name": "Singapore - Original Location",
        "latitude": 1.3521,
        "longitude": 103.8198,
        "radius": 2000,
        "categories": ALL_CATEGORIES
    },
    {
        "name": "Singapore - Marina Bay",
        "latitude": 1.2834,
        "longitude": 103.8607,
        "radius": 1000,
        "categories": ALL_CATEGORIES
    },
    {
        "name": "London - Offices Only",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "radius": 1000,
        "categories": "office"
    },
    {
        "name": "Hyderabad - Offices Only",
        "latitude": 17.3850,
        "longitude": 78.4867,
        "radius": 1000,
        "categories": "office"
    },
    {
        "name": "Tokyo - Restaurants Only",
        "latitude": 35.6762,
        "longitude": 139.6503,
        "radius": 1000,
        "categories": "catering.restaurant"
    },
    {
        "name": "Tokyo - Parking Only",
        "latitude": 35.6762,
        "longitude": 139.6503,
        "radius": 1000,
        "categories": "parking.cars"
    }
]


# --------------------------------------------------
# 4. Execute validation tests
# --------------------------------------------------

results = []

print("=" * 65)
print("GEOAPIFY INFRASTRUCTURE VALIDATION")
print("=" * 65)

for index, test in enumerate(tests, start=1):

    print("\n" + "=" * 65)
    print(f"TEST {index}: {test['name']}")
    print("=" * 65)

    latitude = test["latitude"]
    longitude = test["longitude"]
    radius = test["radius"]

    print("Latitude:", latitude)
    print("Longitude:", longitude)
    print("Radius:", radius, "metres")

    params = {
        "categories": test["categories"],
        "filter": (
            f"circle:{longitude},"
            f"{latitude},{radius}"
        ),
        "bias": (
            f"proximity:{longitude},{latitude}"
        ),
        "limit": LIMIT,
        "lang": "en",
        "apiKey": API_KEY
    }

    try:

        response = requests.get(
            BASE_URL,
            params=params,
            timeout=(10, 45)
        )

        print("Status Code:", response.status_code)

        if response.status_code != 200:

            print(
                response.text.replace(
                    API_KEY, "[REDACTED]"
                )[:500]
            )

            results.append({
                "test": test["name"],
                "status": "Failed",
                "count": None,
                "limit_reached": None
            })

            if response.status_code in (401, 403, 429):
                print("Stopping due to API access or limit issue")
                break

            continue

        data = response.json()

        features = data.get("features")

        if not isinstance(features, list):
            raise ValueError("Invalid API response")

        total_places = len(features)

        limit_reached = total_places >= LIMIT

        print("Total Places Found:", total_places)
        print("Result Limit Reached:", limit_reached)

        print("\nFirst 5 Places:")

        for feature in features[:5]:

            properties = feature.get("properties") or {}

            print(
                "-",
                properties.get("name") or "Unknown",
                "| Distance:",
                properties.get("distance", "Unknown"),
                "metres"
            )

            print(
                "  Categories:",
                properties.get("categories", [])
            )

        results.append({
            "test": test["name"],
            "status": "Success",
            "count": total_places,
            "limit_reached": limit_reached
        })

    except requests.Timeout:

        print("API request timed out")

        results.append({
            "test": test["name"],
            "status": "Timeout",
            "count": None,
            "limit_reached": None
        })

    except (requests.RequestException, ValueError):

        print("Request or response processing failed")

        results.append({
            "test": test["name"],
            "status": "Failed",
            "count": None,
            "limit_reached": None
        })

    finally:

        time.sleep(2)


# --------------------------------------------------
# 5. Display validation summary
# --------------------------------------------------

print("\n" + "=" * 65)
print("VALIDATION TEST SUMMARY")
print("=" * 65)

for result in results:

    print(
        result["test"],
        "| Status:", result["status"],
        "| Places:", result["count"],
        "| Limit Reached:", result["limit_reached"]
    )

print("\n" + "=" * 65)
print("VALIDATION COMPLETED")
print("=" * 65)