import json
import pandas as pd

from pathlib import Path

# Backend directory
BASE_DIR = Path(__file__).resolve().parents[1]

# Input file
INPUT_FILE = (
    BASE_DIR / "data" / "raw"
    / "global_ev_stations_sample.json"
)

# Output directory
OUTPUT_DIR = BASE_DIR / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load raw JSON data
with open(INPUT_FILE, "r", encoding="utf-8") as file:
    raw_stations = json.load(file)

# Lists for processed records
station_records = []
connection_records = []

# Track unique station IDs
seen_station_ids = set()

invalid_stations = 0
duplicate_stations = 0
invalid_connections = 0


# Clean text values
def clean_text(value, default=None):

    if value is None:
        return default

    value = str(value).strip()

    return value if value else default


# Process every charging station
for station in raw_stations:

    address = station.get("AddressInfo") or {}
    country = address.get("Country") or {}
    operator = station.get("OperatorInfo") or {}
    usage = station.get("UsageType") or {}
    status = station.get("StatusType") or {}
    provider = station.get("DataProvider") or {}

    station_id = station.get("ID")

    # Validate coordinates
    try:
        latitude = float(address.get("Latitude"))
        longitude = float(address.get("Longitude"))

    except (TypeError, ValueError):
        invalid_stations += 1
        continue

    if not (
        -90 <= latitude <= 90
        and -180 <= longitude <= 180
    ):
        invalid_stations += 1
        continue

    # Validate station ID
    if station_id is None:
        invalid_stations += 1
        continue

    # Remove duplicate stations
    if station_id in seen_station_ids:
        duplicate_stations += 1
        continue

    seen_station_ids.add(station_id)

    # Combine address fields
    address_parts = [
        clean_text(address.get("AddressLine1")),
        clean_text(address.get("AddressLine2"))
    ]

    full_address = ", ".join(
        part for part in address_parts if part
    )

    # Extract station information
    station_record = {
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

        "postcode": clean_text(
            address.get("Postcode")
        ),

        "country": clean_text(
            country.get("Title"), "Unknown"
        ),

        "country_code": country.get("ISOCode"),

        "continent_code": country.get("ContinentCode"),

        "latitude": latitude,

        "longitude": longitude,

        "operator": clean_text(
            operator.get("Title"), "Unknown"
        ),

        "charging_points": station.get(
            "NumberOfPoints"
        ),

        "usage_type": clean_text(
            usage.get("Title"), "Unknown"
        ),

        "usage_cost": clean_text(
            station.get("UsageCost")
        ),

        "operational_status": clean_text(
            status.get("Title"), "Unknown"
        ),

        "is_operational": status.get(
            "IsOperational"
        ),

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
        )
    }

    station_records.append(station_record)

    # Extract connection details
    connections = station.get("Connections") or []

    for connection in connections:

        connection_id = connection.get("ID")

        if connection_id is None:
            invalid_connections += 1
            continue

        connection_type = (
            connection.get("ConnectionType") or {}
        )

        charging_level = (
            connection.get("Level") or {}
        )

        current_type = (
            connection.get("CurrentType") or {}
        )

        connection_status = (
            connection.get("StatusType") or {}
        )

        connection_record = {
            "connection_id": connection_id,

            "station_id": station_id,

            "connector_type": clean_text(
                connection_type.get("Title"),
                "Unknown"
            ),

            "charging_level": clean_text(
                charging_level.get("Title"),
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
                connection_status.get("Title"),
                "Unknown"
            ),

            "is_operational": connection_status.get(
                "IsOperational"
            )
        }

        connection_records.append(connection_record)


# Convert into DataFrames
stations_df = pd.DataFrame(station_records)
connections_df = pd.DataFrame(connection_records)

if stations_df.empty:
    raise ValueError("No valid station records found")

if connections_df.empty:
    raise ValueError("No valid connection records found")


# Remove duplicate connections
duplicate_connections = connections_df[
    "connection_id"
].duplicated().sum()

connections_df = connections_df.drop_duplicates(
    subset=["connection_id"]
)


# Convert numerical columns
stations_df["charging_points"] = pd.to_numeric(
    stations_df["charging_points"],
    errors="coerce"
)

numeric_columns = [
    "power_kw",
    "voltage",
    "amps",
    "quantity"
]

for column in numeric_columns:

    connections_df[column] = pd.to_numeric(
        connections_df[column],
        errors="coerce"
    )


# Replace invalid negative values with null
stations_df["charging_points"] = (
    stations_df["charging_points"].where(
        stations_df["charging_points"] >= 0
    )
)

for column in numeric_columns:

    connections_df[column] = (
        connections_df[column].where(
            connections_df[column] >= 0
        )
    )


# Convert date columns
date_columns = [
    "last_verified",
    "last_status_update"
]

for column in date_columns:

    stations_df[column] = pd.to_datetime(
        stations_df[column],
        errors="coerce",
        utc=True
    )


# Sort records
stations_df = stations_df.sort_values(
    by="station_id"
)

connections_df = connections_df.sort_values(
    by=["station_id", "connection_id"]
)


# Validate foreign key relationship
orphan_connections = (
    ~connections_df["station_id"].isin(
        stations_df["station_id"]
    )
).sum()

if orphan_connections > 0:
    raise ValueError("Invalid station references found")


# Output file paths
stations_file = OUTPUT_DIR / "ev_stations.csv"

connections_file = OUTPUT_DIR / "ev_connections.csv"


# Save processed datasets
stations_df.to_csv(
    stations_file,
    index=False,
    encoding="utf-8"
)

connections_df.to_csv(
    connections_file,
    index=False,
    encoding="utf-8"
)


# Display preprocessing results
print("=" * 60)
print("EV DATA PREPROCESSING COMPLETED")
print("=" * 60)

print("\nRaw Stations:", len(raw_stations))

print("Invalid Stations Removed:", invalid_stations)

print("Duplicate Stations Removed:", duplicate_stations)

print("Invalid Connections Removed:", invalid_connections)

print("Duplicate Connections Removed:", duplicate_connections)

print("Orphan Connections:", orphan_connections)

print("\nSTATIONS DATASET SHAPE:")
print(stations_df.shape)

print("\nCONNECTIONS DATASET SHAPE:")
print(connections_df.shape)

print("\nCOUNTRY-WISE DISTRIBUTION:")
print(stations_df["country"].value_counts())

print("\nCONNECTOR TYPE DISTRIBUTION:")
print(connections_df["connector_type"].value_counts())

print("\nSTATION STATUS DISTRIBUTION:")
print(stations_df["operational_status"].value_counts())

print("\nSTATIONS MISSING VALUES:")
print(stations_df.isnull().sum())

print("\nCONNECTIONS MISSING VALUES:")
print(connections_df.isnull().sum())

print("\nSTATION SAMPLE:")
print(stations_df.head().to_string())

print("\nCONNECTION SAMPLE:")
print(connections_df.head().to_string())

print("\nFILES SAVED SUCCESSFULLY:")

print(stations_file)
print(connections_file)
