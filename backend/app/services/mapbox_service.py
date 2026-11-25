import os
import requests

from pathlib import Path
from dotenv import load_dotenv


# Backend directory
BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")

ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN")


# Mapbox API endpoints
FORWARD_URL = (
    "https://api.mapbox.com/search/geocode/v6/forward"
)

REVERSE_URL = (
    "https://api.mapbox.com/search/geocode/v6/reverse"
)


# Common Mapbox request function
def make_mapbox_request(url, params):

    if not ACCESS_TOKEN:
        raise ValueError("Mapbox access token not found")

    params = {
        **params,
        "access_token": ACCESS_TOKEN,
        "language": "en",
        "permanent": "false"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if not isinstance(data.get("features"), list):
        raise ValueError("Invalid Mapbox response")

    return data


# Extract geographical context
def get_context_name(context, key):

    item = context.get(key) or {}

    return item.get("name")


# Process individual Mapbox feature
def process_location(feature):

    properties = feature.get("properties") or {}

    geometry = feature.get("geometry") or {}

    context = properties.get("context") or {}

    coordinates = geometry.get("coordinates") or []

    if len(coordinates) < 2:
        return None

    try:

        longitude = float(coordinates[0])

        latitude = float(coordinates[1])

    except (TypeError, ValueError):

        return None

    if not (
        -90 <= latitude <= 90
        and -180 <= longitude <= 180
    ):
        return None

    country = context.get("country") or {}

    return {

        "location_id": properties.get("mapbox_id"),

        "name": properties.get("name"),

        "full_address": properties.get("full_address"),

        "feature_type": properties.get("feature_type"),

        "latitude": latitude,

        "longitude": longitude,

        "country": country.get("name"),

        "country_code": country.get("country_code"),

        "region": get_context_name(context, "region"),

        "district": get_context_name(context, "district"),

        "city": get_context_name(context, "place"),

        "locality": get_context_name(context, "locality"),

        "neighborhood": get_context_name(
            context,
            "neighborhood"
        ),

        "postcode": get_context_name(context, "postcode"),

        "bounding_box": feature.get("bbox"),

        "data_source": "Mapbox"
    }


# Forward geocoding
def search_locations(query, limit=5, country=None):

    query = query.strip()

    if not query:
        raise ValueError("Location query cannot be empty")

    if not 1 <= limit <= 10:
        raise ValueError("Limit must be between 1 and 10")

    params = {

        "q": query,

        "limit": limit,

        "autocomplete": "false"
    }

    if country:

        params["country"] = country.lower()

    data = make_mapbox_request(
        FORWARD_URL,
        params
    )

    locations = []

    for feature in data["features"]:

        location = process_location(feature)

        if location is not None:

            locations.append(location)

    return {

        "query": query,

        "total_results": len(locations),

        "locations": locations,

        "attribution": data.get("attribution")
    }


# Reverse geocoding
def reverse_geocode(latitude, longitude):

    if not -90 <= latitude <= 90:
        raise ValueError("Invalid latitude")

    if not -180 <= longitude <= 180:
        raise ValueError("Invalid longitude")

    params = {

        "latitude": latitude,

        "longitude": longitude
    }

    data = make_mapbox_request(
        REVERSE_URL,
        params
    )

    locations = []

    for feature in data["features"]:

        location = process_location(feature)

        if location is not None:

            locations.append(location)

    return {

        "selected_location": {

            "latitude": latitude,

            "longitude": longitude
        },

        "total_results": len(locations),

        "best_match": (
            locations[0] if locations else None
        ),

        "locations": locations,

        "attribution": data.get("attribution")
    }