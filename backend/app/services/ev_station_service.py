import os
import requests

from pathlib import Path
from dotenv import load_dotenv

# Backend directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Load environment variables
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("OPEN_CHARGE_MAP_API_KEY")

BASE_URL = "https://api.openchargemap.io/v3/poi/"


# Clean text values
def clean_text(value, default=None):

    if value is None:
        return default

    value = str(value).strip()

    return value if value else default


# Retrieve charging stations from API
def fetch_ev_stations(
    latitude,
    longitude,
    radius_km=10,
    max_results=100
):

    if not API_KEY:
        raise ValueError("Open Charge Map API key not found")

    # Validate geographical coordinates
    if not -90 <= latitude <= 90:
        raise ValueError("Invalid latitude")

    if not -180 <= longitude <= 180:
        raise ValueError("Invalid longitude")

    # Application-level search limits
    if not 0 < radius_km <= 100:
        raise ValueError("Radius must be between 0 and 100 km")

    if not 1 <= max_results <= 500:
        raise ValueError("Invalid maximum results")

    params = {
        "output": "json",
        "latitude": latitude,
        "longitude": longitude,
        "distance": radius_km,
        "distanceunit": "KM",
        "maxresults": max_results
    }

    headers = {
        "X-API-Key": API_KEY
    }

    response = requests.get(
        BASE_URL,
        params=params,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list):
        raise ValueError("Unexpected API response")

    return data


# Process individual connection
def process_connection(connection):

    connection_type = (
        connection.get("ConnectionType") or {}
    )

    level = connection.get("Level") or {}

    current_type = (
        connection.get("CurrentType") or {}
    )

    status = connection.get("StatusType") or {}

    return {
        "connection_id": connection.get("ID"),

        "connector_type": clean_text(
            connection_type.get("Title"),
            "Unknown"
        ),

        "charging_level": clean_text(
            level.get("Title"),
            "Unknown"
        ),

        "power_kw": connection.get("PowerKW"),

        "voltage": connection.get("Voltage"),

        "amps": connection.get("Amps"),

        "current_type": clean_text(
            current_type.get("Title"),
            "Unknown"
        ),

        "quantity": connection.get("Quantity"),

        "operational_status": clean_text(
            status.get("Title"),
            "Unknown"
        ),

        "is_operational": status.get(
            "IsOperational"
        )
    }


# Process individual station
def process_station(station):

    address = station.get("AddressInfo") or {}
    country = address.get("Country") or {}
    operator = station.get("OperatorInfo") or {}
    usage = station.get("UsageType") or {}
    status = station.get("StatusType") or {}
    provider = station.get("DataProvider") or {}

    station_id = station.get("ID")

    if station_id is None:
        return None

    # Validate coordinates
    try:

        latitude = float(address.get("Latitude"))

        longitude = float(address.get("Longitude"))

    except (TypeError, ValueError):

        return None

    if not (
        -90 <= latitude <= 90
        and -180 <= longitude <= 180
    ):

        return None

    # Combine address fields
    address_parts = [
        clean_text(address.get("AddressLine1")),
        clean_text(address.get("AddressLine2"))
    ]

    full_address = ", ".join(
        part for part in address_parts if part
    )

    # Process connection records
    connections = []

    seen_connection_ids = set()

    for connection in station.get("Connections") or []:

        connection_id = connection.get("ID")

        if connection_id is None:
            continue

        if connection_id in seen_connection_ids:
            continue

        seen_connection_ids.add(connection_id)

        connections.append(
            process_connection(connection)
        )

    # Unique connector types
    connector_types = sorted({
        connection["connector_type"]
        for connection in connections
    })

    # Maximum reported charging power
    power_values = [
        connection["power_kw"]
        for connection in connections
        if isinstance(
            connection["power_kw"], (int, float)
        )
        and connection["power_kw"] >= 0
    ]

    max_power_kw = (
        max(power_values)
        if power_values else None
    )

    # Structured station response
    return {
        "station_id": station_id,

        "station_name": clean_text(
            address.get("Title"), "Unknown"
        ),

        "address": full_address or None,

        "city": clean_text(
            address.get("Town"), "Unknown"
        ),

        "state": clean_text(
            address.get("StateOrProvince"), "Unknown"
        ),

        "postcode": address.get("Postcode"),

        "country": country.get("Title"),

        "country_code": country.get("ISOCode"),

        "continent_code": country.get("ContinentCode"),

        "latitude": latitude,

        "longitude": longitude,

        "distance_km": address.get("Distance"),

        "operator": clean_text(
            operator.get("Title"), "Unknown"
        ),

        "charging_points": station.get(
            "NumberOfPoints"
        ),

        "usage_type": clean_text(
            usage.get("Title"), "Unknown"
        ),

        "usage_cost": station.get("UsageCost"),

        "operational_status": clean_text(
            status.get("Title"), "Unknown"
        ),

        "is_operational": status.get(
            "IsOperational"
        ),

        "connector_types": connector_types,

        "max_power_kw": max_power_kw,

        "connections": connections,

        "last_verified": station.get(
            "DateLastVerified"
        ),

        "last_status_update": station.get(
            "DateLastStatusUpdate"
        ),

        "recently_verified": station.get(
            "IsRecentlyVerified"
        ),

        "data_quality_level": station.get(
            "DataQualityLevel"
        ),

        "data_provider": provider.get("Title"),

        "data_license": provider.get("License"),

        "is_open_data_licensed": provider.get(
            "IsOpenDataLicensed"
        ),

        "data_source": "Open Charge Map"
    }


# Main reusable service function
def get_nearby_ev_stations(
    latitude,
    longitude,
    radius_km=10,
    max_results=100
):

    raw_stations = fetch_ev_stations(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        max_results=max_results
    )

    processed_stations = []

    seen_station_ids = set()

    for station in raw_stations:

        processed = process_station(station)

        if processed is None:
            continue

        station_id = processed["station_id"]

        if station_id in seen_station_ids:
            continue

        seen_station_ids.add(station_id)

        processed_stations.append(processed)

    # Sort stations by distance
    processed_stations.sort(
        key=lambda station: (
            station["distance_km"]
            if station["distance_km"] is not None
            else float("inf")
        )
    )

    return {
        "search_location": {
            "latitude": latitude,
            "longitude": longitude
        },

        "radius_km": radius_km,

        "max_results": max_results,

        "total_stations": len(processed_stations),

        "result_limit_reached": (
            len(raw_stations) >= max_results
        ),

        "stations": processed_stations
    }