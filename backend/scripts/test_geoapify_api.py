import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from collections import Counter

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

latitude = 17.3850
longitude = 78.4867

radius = 1000
limit = 100


# --------------------------------------------------
# 3. Infrastructure categories
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
# 4. Request parameters
# --------------------------------------------------

params = {
    "categories": ",".join(categories.keys()),
    "filter": f"circle:{longitude},{latitude},{radius}",
    "bias": f"proximity:{longitude},{latitude}",
    "limit": limit,
    "lang": "en",
    "apiKey": API_KEY
}


# --------------------------------------------------
# 5. Display testing information
# --------------------------------------------------

print("=" * 60)
print("GEOAPIFY PLACES API TEST")
print("=" * 60)

print("Location: Hyderabad, India")
print("Latitude:", latitude)
print("Longitude:", longitude)
print("Search Radius:", radius, "metres")
print("Maximum Results:", limit)


# --------------------------------------------------
# 6. Send API request
# --------------------------------------------------

try:

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=(10, 45)
    )

    print("\nStatus Code:", response.status_code)

    if response.status_code != 200:
        print("API request failed.")
        print(
            response.text.replace(
                API_KEY, "[REDACTED]"
            )[:1000]
        )
        raise SystemExit(1)

    data = response.json()

    features = data.get("features")

    if not isinstance(features, list):
        raise ValueError("Unexpected Geoapify response")

    print("Total Places Found:", len(features))

    print(
        "Result Limit Reached:",
        len(features) >= limit
    )


    # ----------------------------------------------
    # 7. Infrastructure category distribution
    # ----------------------------------------------

    category_counts = Counter()

    for feature in features:

        properties = feature.get("properties") or {}

        place_categories = properties.get(
            "categories", []
        ) or []

        for category, label in categories.items():

            if any(
                value == category
                or value.startswith(category + ".")
                for value in place_categories
            ):
                category_counts[label] += 1


    print("\n" + "=" * 60)
    print("INFRASTRUCTURE CATEGORY DISTRIBUTION")
    print("=" * 60)

    for label in categories.values():

        print(
            f"{label}: "
            f"{category_counts.get(label, 0)}"
        )


    # ----------------------------------------------
    # 8. Display first 10 places
    # ----------------------------------------------

    print("\n" + "=" * 60)
    print("FIRST 10 INFRASTRUCTURE RECORDS")
    print("=" * 60)

    for index, feature in enumerate(
        features[:10], start=1
    ):

        properties = feature.get("properties") or {}

        geometry = feature.get("geometry") or {}

        coordinates = geometry.get(
            "coordinates", []
        )

        place_latitude = properties.get("lat")
        place_longitude = properties.get("lon")

        if (
            geometry.get("type") == "Point"
            and len(coordinates) >= 2
        ):
            place_longitude = coordinates[0]
            place_latitude = coordinates[1]

        print("\nRecord:", index)

        print(
            "Place ID:",
            properties.get("place_id", "Unknown")
        )

        print(
            "Name:",
            properties.get("name", "Unknown")
        )

        print(
            "Address:",
            properties.get("formatted", "Unknown")
        )

        print("Latitude:", place_latitude)
        print("Longitude:", place_longitude)

        print(
            "Distance (metres):",
            properties.get("distance", "Unknown")
        )

        print(
            "Categories:",
            properties.get("categories", [])
        )

        print(
            "Data Source:",
            properties.get("datasource", {})
        )

        print("-" * 50)


    # ----------------------------------------------
    # 9. Final status
    # ----------------------------------------------

    print("\n" + "=" * 60)
    print("GEOAPIFY API TEST COMPLETED")
    print("=" * 60)

    print("API Connection: Successful")
    print("Total Records:", len(features))
    print("API Provider: Geoapify")
    print("Attribution: https://www.geoapify.com/")

    if len(features) >= limit:
        print(
            "Warning: More matching places may exist."
        )


# --------------------------------------------------
# 10. Error handling
# --------------------------------------------------

except requests.Timeout:

    print("Geoapify API request timed out")

except requests.RequestException:

    print("Unable to connect to Geoapify API")

except ValueError as error:

    print("Data processing error:", error)