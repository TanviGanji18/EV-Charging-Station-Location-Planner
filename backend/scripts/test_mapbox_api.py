import os
import requests

from pathlib import Path
from dotenv import load_dotenv


# Backend directory
BASE_DIR = Path(__file__).resolve().parents[1]

# Load environment variables
load_dotenv(BASE_DIR / ".env")

ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN")


if not ACCESS_TOKEN:
    raise ValueError("Mapbox access token not found")


# Mapbox API URLs
FORWARD_URL = (
    "https://api.mapbox.com/search/geocode/v6/forward"
)

REVERSE_URL = (
    "https://api.mapbox.com/search/geocode/v6/reverse"
)


# Forward geocoding function
def test_forward_geocoding(location):

    params = {
        "q": location,
        "access_token": ACCESS_TOKEN,
        "limit": 3,
        "language": "en"
    }

    response = requests.get(
        FORWARD_URL,
        params=params,
        timeout=30
    )

    print("\nSearching:", location)
    print("Status Code:", response.status_code)

    if response.status_code != 200:
        print("Mapbox request failed")
        return

    data = response.json()

    features = data.get("features", [])

    print("Results Found:", len(features))

    for feature in features:

        properties = feature.get("properties", {})

        geometry = feature.get("geometry", {})

        coordinates = geometry.get("coordinates", [])

        print("\nLocation Name:", properties.get("name"))

        print(
            "Full Address:",
            properties.get("full_address")
        )

        print(
            "Feature Type:",
            properties.get("feature_type")
        )

        if len(coordinates) >= 2:

            longitude = coordinates[0]
            latitude = coordinates[1]

            print("Latitude:", latitude)
            print("Longitude:", longitude)

        print("-" * 50)


# Reverse geocoding function
def test_reverse_geocoding(latitude, longitude):

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "access_token": ACCESS_TOKEN,
        "language": "en"
    }

    response = requests.get(
        REVERSE_URL,
        params=params,
        timeout=30
    )

    print("\nLatitude:", latitude)
    print("Longitude:", longitude)

    print("Status Code:", response.status_code)

    if response.status_code != 200:
        print("Mapbox request failed")
        return

    data = response.json()

    features = data.get("features", [])

    print("Results Found:", len(features))

    for feature in features[:3]:

        properties = feature.get("properties", {})

        print("\nLocation Name:", properties.get("name"))

        print(
            "Full Address:",
            properties.get("full_address")
        )

        print(
            "Feature Type:",
            properties.get("feature_type")
        )

        print("-" * 50)


# Forward geocoding testing
print("=" * 60)
print("MAPBOX FORWARD GEOCODING TEST")
print("=" * 60)


locations = [
    "Hyderabad, India",
    "London, United Kingdom",
    "New York, United States",
    "Tokyo, Japan",
    "Dubai, United Arab Emirates",
    "Sydney, Australia",
    "Singapore",
    "Paris, France"
]


for location in locations:

    test_forward_geocoding(location)


# Reverse geocoding testing
print("\n" + "=" * 60)
print("MAPBOX REVERSE GEOCODING TEST")
print("=" * 60)


test_reverse_geocoding(
    latitude=17.3850,
    longitude=78.4867
)


test_reverse_geocoding(
    latitude=48.8566,
    longitude=2.3522
)


print("\n" + "=" * 60)
print("MAPBOX API TEST COMPLETED")
print("=" * 60)