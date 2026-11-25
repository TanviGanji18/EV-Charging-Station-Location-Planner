import os
import time
import requests

from pathlib import Path
from dotenv import load_dotenv
from collections import Counter


# --------------------------------------------------
# 1. Load environment variables
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

RADIUS = 1000
LIMIT = 100


# --------------------------------------------------
# 3. Worldwide test locations
# --------------------------------------------------

cities = [
    {
        "city": "Hyderabad",
        "country": "India",
        "latitude": 17.3850,
        "longitude": 78.4867
    },
    {
        "city": "London",
        "country": "United Kingdom",
        "latitude": 51.5074,
        "longitude": -0.1278
    },
    {
        "city": "New York",
        "country": "United States",
        "latitude": 40.7128,
        "longitude": -74.0060
    },
    {
        "city": "Tokyo",
        "country": "Japan",
        "latitude": 35.6762,
        "longitude": 139.6503
    },
    {
        "city": "Dubai",
        "country": "UAE",
        "latitude": 25.2048,
        "longitude": 55.2708
    },
    {
        "city": "Sydney",
        "country": "Australia",
        "latitude": -33.8688,
        "longitude": 151.2093
    },
    {
        "city": "Singapore",
        "country": "Singapore",
        "latitude": 1.3521,
        "longitude": 103.8198
    },
    {
        "city": "Paris",
        "country": "France",
        "latitude": 48.8566,
        "longitude": 2.3522
    }
]


# --------------------------------------------------
# 4. Infrastructure categories
# --------------------------------------------------

categories = {
    "commercial.shopping_mall": "Shopping Mall",
    "commercial.supermarket": "Supermarket",
    "parking.cars": "Parking",
    "catering.restaurant": "Restaurant",
    "catering.cafe": "Cafe",
    "accommodation.hotel": "Hotel",
    "service.vehicle.fuel": "Fuel Station",
    "healthcare.hospital": "Hospital",
    "office": "Office",
    "service.vehicle.charging_station": "EV Charging Station"
}


# --------------------------------------------------
# 5. Initialize result containers
# --------------------------------------------------

city_results = []

global_category_counts = Counter()

unique_place_ids = set()

total_records = 0

successful_cities = 0

failed_cities = 0


# --------------------------------------------------
# 6. Start worldwide testing
# --------------------------------------------------

print("=" * 65)
print("WORLDWIDE GEOAPIFY INFRASTRUCTURE API TEST")
print("=" * 65)

print("Total Cities:", len(cities))
print("Search Radius:", RADIUS, "metres")
print("Maximum Results Per City:", LIMIT)


# --------------------------------------------------
# 7. Retrieve infrastructure for each city
# --------------------------------------------------

for index, location in enumerate(cities, start=1):

    city = location["city"]
    country = location["country"]

    latitude = location["latitude"]
    longitude = location["longitude"]

    print("\n" + "=" * 65)

    print(f"TEST {index}: {city}, {country}")

    print("=" * 65)

    print("Latitude:", latitude)
    print("Longitude:", longitude)

    params = {
        "categories": ",".join(categories.keys()),
        "filter": (
            f"circle:{longitude},"
            f"{latitude},{RADIUS}"
        ),
        "bias": (
            f"proximity:{longitude},{latitude}"
        ),
        "limit": LIMIT,
        "lang": "en",
        "apiKey": API_KEY
    }

    try:

        start_time = time.perf_counter()

        response = requests.get(
            BASE_URL,
            params=params,
            timeout=(10, 45)
        )

        response_time = (
            time.perf_counter() - start_time
        )

        print("Status Code:", response.status_code)

        print(
            "Response Time:",
            round(response_time, 2),
            "seconds"
        )

        if response.status_code != 200:

            failed_cities += 1

            print("API request failed.")

            print(
                response.text.replace(
                    API_KEY, "[REDACTED]"
                )[:500]
            )

            city_results.append({
                "city": city,
                "country": country,
                "status": "Failed",
                "total_places": None,
                "limit_reached": None
            })

            if response.status_code in (401, 403, 429):
                print(
                    "Stopping test due to authentication "
                    "or request limit issue."
                )
                break

            continue

        data = response.json()

        features = data.get("features")

        if not isinstance(features, list):
            raise ValueError(
                "Invalid Geoapify response"
            )

        category_counts = Counter()

        total_places = len(features)

        limit_reached = total_places >= LIMIT

        total_records += total_places

        successful_cities += 1

        print("Total Places Found:", total_places)

        print("Result Limit Reached:", limit_reached)


        # ------------------------------------------
        # 8. Count infrastructure categories
        # ------------------------------------------

        for feature in features:

            properties = (
                feature.get("properties") or {}
            )

            place_id = properties.get("place_id")

            if place_id:
                unique_place_ids.add(place_id)

            place_categories = (
                properties.get("categories") or []
            )

            for category, label in categories.items():

                if any(
                    value == category
                    or value.startswith(category + ".")
                    for value in place_categories
                ):

                    category_counts[label] += 1

                    global_category_counts[label] += 1


        print("\nInfrastructure Distribution:")

        for label in categories.values():

            print(
                f"{label}: "
                f"{category_counts.get(label, 0)}"
            )


        # ------------------------------------------
        # 9. Display first three places
        # ------------------------------------------

        print("\nFirst 3 Places:")

        for feature in features[:3]:

            properties = (
                feature.get("properties") or {}
            )

            print(
                "-",
                properties.get("name") or "Unknown",
                "| Distance:",
                properties.get("distance", "Unknown"),
                "metres"
            )


        # ------------------------------------------
        # 10. Store city-level summary in memory
        # ------------------------------------------

        city_results.append({
            "city": city,
            "country": country,
            "status": "Success",
            "total_places": total_places,
            "limit_reached": limit_reached,
            "response_time": round(response_time, 2)
        })


    except requests.Timeout:

        failed_cities += 1

        print("API request timed out")

        city_results.append({
            "city": city,
            "country": country,
            "status": "Timeout",
            "total_places": None,
            "limit_reached": None
        })


    except (requests.RequestException, ValueError):

        failed_cities += 1

        print("Request or response processing failed")

        city_results.append({
            "city": city,
            "country": country,
            "status": "Failed",
            "total_places": None,
            "limit_reached": None
        })


    finally:

        # Avoid sending requests too quickly

        time.sleep(2)


# --------------------------------------------------
# 11. Display worldwide testing summary
# --------------------------------------------------

print("\n" + "=" * 65)
print("WORLDWIDE INFRASTRUCTURE TEST SUMMARY")
print("=" * 65)

print("Planned Cities:", len(cities))
print("Attempted Cities:", len(city_results))
print("Successful Cities:", successful_cities)
print("Failed Cities:", failed_cities)

print("Total Place Records:", total_records)

print(
    "Unique Non-Empty Place IDs:",
    len(unique_place_ids)
)


# --------------------------------------------------
# 12. City-wise results
# --------------------------------------------------

print("\nCITY-WISE RESULTS")
print("-" * 65)

for result in city_results:

    print(
        result["city"],
        "| Status:", result["status"],
        "| Places:", result["total_places"],
        "| Limit Reached:", result["limit_reached"]
    )


# --------------------------------------------------
# 13. Global category distribution
# --------------------------------------------------

print("\nGLOBAL INFRASTRUCTURE DISTRIBUTION")
print("-" * 65)

for label in categories.values():

    print(
        f"{label}: "
        f"{global_category_counts.get(label, 0)}"
    )


print("\n" + "=" * 65)
print("WORLDWIDE GEOAPIFY TEST FINISHED")
print("=" * 65)

print("API Provider: Geoapify")
print("Attribution: https://www.geoapify.com/")