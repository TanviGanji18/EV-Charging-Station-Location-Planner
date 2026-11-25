import os
import math
import requests

import time

from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed
)

from pathlib import Path
from dotenv import load_dotenv


# --------------------------------------------------
# 1. Load environment variables
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GEOAPIFY_API_KEY")

BASE_URL = "https://api.geoapify.com/v2/places"


# --------------------------------------------------
# 2. Infrastructure categories
# --------------------------------------------------

INFRASTRUCTURE_CATEGORIES = {
    "shopping_malls": "commercial.shopping_mall",
    "supermarkets": "commercial.supermarket",
    "parking": "parking.cars",
    "restaurants": "catering.restaurant",
    "cafes": "catering.cafe",
    "hotels": "accommodation.hotel",
    "fuel_stations": "service.vehicle.fuel",
    "hospitals": "healthcare.hospital",
    "offices": "office",
    "ev_charging_stations":
        "service.vehicle.charging_station"
}


# --------------------------------------------------
# 3. Clean text values
# --------------------------------------------------

def clean_text(value):

    if value is None:
        return None

    value = str(value).strip()

    return value if value else None


# --------------------------------------------------
# 4. Clean numeric values
# --------------------------------------------------

def clean_number(value):

    try:

        number = float(value)

        if not math.isfinite(number):
            return None

        return number

    except (TypeError, ValueError):

        return None


# --------------------------------------------------
# 5. Validate input coordinates
# --------------------------------------------------

def validate_coordinates(latitude, longitude):

    if not -90 <= latitude <= 90:

        raise ValueError("Invalid latitude")

    if not -180 <= longitude <= 180:

        raise ValueError("Invalid longitude")


# --------------------------------------------------
# 6. Fetch category-specific infrastructure
# --------------------------------------------------

def fetch_infrastructure(
    latitude,
    longitude,
    category,
    radius=1000,
    limit=100,
    offset=0
):

    if not API_KEY:

        raise ValueError(
            "Geoapify API key not found"
        )

    validate_coordinates(latitude, longitude)

    if not 1 <= radius <= 10000:

        raise ValueError(
            "Radius must be between 1 and 10000 metres"
        )

    if not 1 <= limit <= 100:

        raise ValueError(
            "Limit must be between 1 and 100"
        )

    if category not in INFRASTRUCTURE_CATEGORIES:

        raise ValueError(
            "Invalid infrastructure category"
        )
    if offset < 0:
        raise ValueError("Offset cannot be negative")

    params = {
        "categories":
            INFRASTRUCTURE_CATEGORIES[category],

        "filter":
            f"circle:{longitude},{latitude},{radius}",

        "bias":
            f"proximity:{longitude},{latitude}",

        "limit": limit,

        "offset": offset,

        "lang": "en",

        "apiKey": API_KEY
    }

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=(10, 45)
    )

    response.raise_for_status()

    data = response.json()

    features = data.get("features")

    if not isinstance(features, list):

        raise ValueError(
            "Invalid Geoapify response"
        )

    return features


# --------------------------------------------------
# 7. Process individual infrastructure records
# --------------------------------------------------

def process_infrastructure(feature):

    properties = feature.get("properties") or {}

    geometry = feature.get("geometry") or {}

    coordinates = geometry.get("coordinates") or []

    place_id = clean_text(
        properties.get("place_id")
    )

    if not place_id:

        return None

    latitude = clean_number(
        properties.get("lat")
    )

    longitude = clean_number(
        properties.get("lon")
    )

    if (
        geometry.get("type") == "Point"
        and len(coordinates) >= 2
    ):

        longitude = clean_number(coordinates[0])

        latitude = clean_number(coordinates[1])

    if latitude is None or longitude is None:

        return None

    if not -90 <= latitude <= 90:

        return None

    if not -180 <= longitude <= 180:

        return None

    datasource = properties.get("datasource") or {}

    raw = datasource.get("raw") or {}

    distance = clean_number(
        properties.get("distance")
    )

    if distance is not None and distance < 0:

        distance = None

    return {
        "place_id": place_id,

        "name": clean_text(
            properties.get("name")
        ),

        "address": clean_text(
            properties.get("formatted")
        ),

        "latitude": latitude,

        "longitude": longitude,

        "distance_metres": distance,

        "categories":
            properties.get("categories") or [],

        "city": clean_text(
            properties.get("city")
        ),

        "state": clean_text(
            properties.get("state")
        ),

        "country": clean_text(
            properties.get("country")
        ),

        "country_code": clean_text(
            properties.get("country_code")
        ),

        "postcode": clean_text(
            properties.get("postcode")
        ),

        "osm_id": clean_text(
            raw.get("osm_id")
        ),

        "osm_type": clean_text(
            raw.get("osm_type")
        ),

        "source": clean_text(
            datasource.get("sourcename")
        ),

        "attribution": clean_text(
            datasource.get("attribution")
        ),

        "license": clean_text(
            datasource.get("license")
        ),

        "source_url": clean_text(
            datasource.get("url")
        ),

        "provider": "Geoapify"
    }


# --------------------------------------------------
# 8. Retrieve and preprocess nearby infrastructure
# --------------------------------------------------

def get_nearby_infrastructure(
    latitude,
    longitude,
    category,
    radius=1000,
    limit=100
):

    features = fetch_infrastructure(
        latitude=latitude,
        longitude=longitude,
        category=category,
        radius=radius,
        limit=limit
    )

    processed_places = []

    seen_ids = set()

    invalid_records = 0

    duplicate_records = 0

    for feature in features:

        place = process_infrastructure(feature)

        if place is None:

            invalid_records += 1

            continue

        place_id = place["place_id"]

        if place_id in seen_ids:

            duplicate_records += 1

            continue

        seen_ids.add(place_id)

        processed_places.append(place)

    processed_places.sort(
        key=lambda place: (
            place["distance_metres"]
            if place["distance_metres"] is not None
            else float("inf")
        )
    )

    nearest_place = next(
        (
            place for place in processed_places
            if place["distance_metres"] is not None
        ),
        None
    )

    return {
        "search_location": {
            "latitude": latitude,
            "longitude": longitude
        },

        "category": category,

        "radius_metres": radius,

        "max_results": limit,

        "raw_records": len(features),

        "total_places": len(processed_places),

        "invalid_records": invalid_records,

        "duplicate_records": duplicate_records,

        "result_limit_reached":
            len(features) >= limit,

        "nearest_place": nearest_place,

        "places": processed_places,

        "provider": "Geoapify",

        "provider_attribution":
            "https://www.geoapify.com/"
    }
# --------------------------------------------------
# 9. Paginated infrastructure retrieval
# --------------------------------------------------

def get_paginated_infrastructure(
    latitude,
    longitude,
    category,
    radius=1000,
    page_size=100,
    max_pages=3
):

    if not 1 <= page_size <= 100:
        raise ValueError("Invalid page size")

    if not 1 <= max_pages <= 5:
        raise ValueError("Invalid maximum pages")

    places = []

    seen_ids = set()

    raw_records = 0

    invalid_records = 0

    duplicate_records = 0

    pages_fetched = 0

    limit_reached = False

    pagination_stalled = False

    for page in range(max_pages):

        offset = page * page_size

        features = fetch_infrastructure(
            latitude=latitude,
            longitude=longitude,
            category=category,
            radius=radius,
            limit=page_size,
            offset=offset
        )

        pages_fetched += 1

        raw_records += len(features)

        new_records = 0

        for feature in features:

            place = process_infrastructure(feature)

            if place is None:

                invalid_records += 1

                continue

            place_id = place["place_id"]

            if place_id in seen_ids:

                duplicate_records += 1

                continue

            seen_ids.add(place_id)

            places.append(place)

            new_records += 1

        limit_reached = len(features) >= page_size

        # Stop if no additional records are expected

        if not limit_reached:

            break

        # Protect against repeated pages

        if new_records == 0:

            pagination_stalled = True

            break

    places.sort(
        key=lambda place: (
            place["distance_metres"]
            if place["distance_metres"] is not None
            else float("inf")
        )
    )

    nearest_place = next(
        (
            place for place in places
            if place["distance_metres"] is not None
        ),
        None
    )

    return {
        "category": category,

        "search_location": {
            "latitude": latitude,
            "longitude": longitude
        },

        "radius_metres": radius,

        "pages_fetched": pages_fetched,

        "raw_records": raw_records,

        "total_places": len(places),

        "invalid_records": invalid_records,

        "duplicate_records": duplicate_records,

        "result_limit_reached": limit_reached,

        "pagination_stalled": pagination_stalled,

        "nearest_place": nearest_place,

        "places": places,

        "provider": "Geoapify",

        "provider_attribution":
            "https://www.geoapify.com/"
    }

# --------------------------------------------------
# 10. Infrastructure aggregation
# --------------------------------------------------

def get_infrastructure_summary(
    latitude,
    longitude,
    radius=1000,
    page_size=100,
    max_pages=3,
    max_workers=2
):

    validate_coordinates(latitude, longitude)

    if not 1 <= radius <= 10000:
        raise ValueError("Invalid search radius")

    if not 1 <= page_size <= 100:
        raise ValueError("Invalid page size")

    if not 1 <= max_pages <= 5:
        raise ValueError("Invalid maximum pages")

    if not 1 <= max_workers <= 3:
        raise ValueError("Invalid worker count")

    start_time = time.perf_counter()

    category_results = {}

    unique_places = {}

    failed_categories = []

    truncated_categories = []

    total_pages = 0

    total_raw_records = 0

    total_invalid_records = 0

    total_duplicate_records = 0


    # ----------------------------------------------
    # Retrieve a single infrastructure category
    # ----------------------------------------------

    def retrieve_category(category):

        return get_paginated_infrastructure(
            latitude=latitude,
            longitude=longitude,
            category=category,
            radius=radius,
            page_size=page_size,
            max_pages=max_pages
        )


    # ----------------------------------------------
    # Execute category requests concurrently
    # ----------------------------------------------

    with ThreadPoolExecutor(
        max_workers=max_workers
    ) as executor:

        futures = {
            executor.submit(
                retrieve_category,
                category
            ): category

            for category in INFRASTRUCTURE_CATEGORIES
        }

        for future in as_completed(futures):

            category = futures[future]

            try:

                result = future.result()

                nearest = result["nearest_place"]

                truncated = (
                    result["result_limit_reached"]
                    or result["pagination_stalled"]
                )

                if truncated:

                    truncated_categories.append(category)

                total_pages += result["pages_fetched"]

                total_raw_records += result["raw_records"]

                total_invalid_records += (
                    result["invalid_records"]
                )

                total_duplicate_records += (
                    result["duplicate_records"]
                )


                # ----------------------------------
                # Store category-level summary
                # ----------------------------------

                category_results[category] = {
                    "status": "success",

                    "count": result["total_places"],

                    "pages_fetched":
                        result["pages_fetched"],

                    "result_limit_reached":
                        result["result_limit_reached"],

                    "pagination_stalled":
                        result["pagination_stalled"],

                    "nearest_place":
                        nearest["name"]
                        if nearest else None,

                    "nearest_distance_metres":
                        nearest["distance_metres"]
                        if nearest else None
                }


                # ----------------------------------
                # Cross-category duplicate handling
                # ----------------------------------

                for place in result["places"]:

                    place_id = place["place_id"]

                    if place_id not in unique_places:

                        unique_places[place_id] = {
                            **place,
                            "matched_categories": [category]
                        }

                    else:

                        matched = unique_places[
                            place_id
                        ]["matched_categories"]

                        if category not in matched:

                            matched.append(category)


            except Exception as error:

                failed_categories.append(category)

                category_results[category] = {
                    "status": "failed",

                    "count": None,

                    "nearest_place": None,

                    "nearest_distance_metres": None,

                    "error_type": type(error).__name__
                }


    # ----------------------------------------------
    # Arrange categories in consistent order
    # ----------------------------------------------

    ordered_results = {
        category: category_results[category]

        for category in INFRASTRUCTURE_CATEGORIES
    }


    # ----------------------------------------------
    # Sort infrastructure records by distance
    # ----------------------------------------------

    places = list(unique_places.values())

    places.sort(
        key=lambda place: (
            place["distance_metres"]
            if place["distance_metres"] is not None
            else float("inf")
        )
    )


    # ----------------------------------------------
    # Calculate total execution time
    # ----------------------------------------------

    elapsed_time = round(
        time.perf_counter() - start_time,
        2
    )


    # ----------------------------------------------
    # Determine overall retrieval status
    # ----------------------------------------------

    if len(failed_categories) == len(
        INFRASTRUCTURE_CATEGORIES
    ):

        status = "failed"

    elif failed_categories or truncated_categories:

        status = "partial"

    else:

        status = "success"


    # ----------------------------------------------
    # Return combined infrastructure response
    # ----------------------------------------------

    return {
        "status": status,

        "search_location": {
            "latitude": latitude,
            "longitude": longitude
        },

        "radius_metres": radius,

        "total_categories":
            len(INFRASTRUCTURE_CATEGORIES),

        "successful_categories":
            len(INFRASTRUCTURE_CATEGORIES)
            - len(failed_categories),

        "failed_categories":
            sorted(failed_categories),

        "truncated_categories":
            sorted(truncated_categories),

        "total_pages_fetched": total_pages,

        "total_raw_records": total_raw_records,

        "total_invalid_records": total_invalid_records,

        "total_duplicate_records":
            total_duplicate_records,

        "total_unique_places": len(places),

        "category_summary": ordered_results,

        "places": places,

        "response_time_seconds": elapsed_time,

        "provider": "Geoapify",

        "provider_attribution":
            "https://www.geoapify.com/"
    }