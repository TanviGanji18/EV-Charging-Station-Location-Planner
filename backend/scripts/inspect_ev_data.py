import json
import pandas as pd

from pathlib import Path

# Backend directory
BASE_DIR = Path(__file__).resolve().parents[1]

# Raw dataset path
DATA_PATH = (
    BASE_DIR / "data" / "raw"
    / "global_ev_stations_sample.json"
)

# Load JSON data
with open(DATA_PATH, "r", encoding="utf-8") as file:
    stations = json.load(file)

print("=" * 60)
print("EV CHARGING STATION DATA INSPECTION")
print("=" * 60)

# Total records
print("\nTotal Records:", len(stations))

# Check empty dataset
if not stations:
    raise ValueError("Dataset is empty")

# Display top-level fields
print("\nAVAILABLE TOP-LEVEL FIELDS:")

all_fields = set()

for station in stations:
    all_fields.update(station.keys())

for field in sorted(all_fields):
    print(field)

# Convert nested JSON into DataFrame
df = pd.json_normalize(stations)

# Dataset shape
print("\nDATASET SHAPE:")
print(df.shape)

# Display all columns
print("\nAVAILABLE COLUMNS:")

for column in df.columns:
    print(column)

# Data types
print("\nDATA TYPES:")
print(df.dtypes.to_string())

# Missing values
print("\nMISSING VALUES:")

missing = pd.DataFrame({
    "Missing_Count": df.isnull().sum(),
    "Missing_Percentage": (
        df.isnull().mean() * 100
    ).round(2)
})

missing = missing.sort_values(
    by="Missing_Percentage",
    ascending=False
)

print(missing.to_string())

# Duplicate station IDs
print("\nDUPLICATE STATION IDs:")

if "ID" in df.columns:
    print(df["ID"].duplicated().sum())

# Country-wise distribution
print("\nCOUNTRY-WISE DISTRIBUTION:")

country_column = "AddressInfo.Country.Title"

if country_column in df.columns:
    print(df[country_column].value_counts(
        dropna=False
    ))

# Sample station information
print("\nFIRST STATION DETAILS:")

print(json.dumps(
    stations[0],
    indent=4,
    ensure_ascii=False
))

print("\nDATA INSPECTION COMPLETED")