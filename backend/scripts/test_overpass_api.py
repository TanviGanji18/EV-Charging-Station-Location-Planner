import requests
import json

from pathlib import Path
from collections import Counter


# Backend directory
BASE_DIR = Path(__file__).resolve().parents[1]


# Overpass API endpoint
OVERPASS_URL = (
    "https://overpass.kumi.systems/api/interpreter"
)


# Test location: Hyderabad
latitude = 17.3850
longitude = 78.4867

# Search radius in metres
radius = 1000


# Overpass query
query = f"""
[out:json][timeout:60];

(
    nwr["shop"="mall"]
        (around:{radius},{latitude},{longitude});

    nwr["shop"="supermarket"]
        (around:{radius},{latitude},{longitude});

    nwr["amenity"="parking"]
        (around:{radius},{latitude},{longitude});

    nwr["amenity"="restaurant"]
        (around:{radius},{latitude},{longitude});

    nwr["amenity"="cafe"]
        (around:{radius},{latitude},{longitude});

    nwr["amenity"="fuel"]
        (around:{radius},{latitude},{longitude});

    nwr["amenity"="hospital"]
        (around:{radius},{latitude},{longitude});

    nwr["tourism"="hotel"]
        (around:{radius},{latitude},{longitude});

    nwr["office"]
        (around:{radius},{latitude},{longitude});

    nwr["amenity"="charging_station"]
        (around:{radius},{latitude},{longitude});

    way["highway"~"^(motorway|trunk|primary|secondary|tertiary)$"]
        (around:{radius},{latitude},{longitude});
);

out center;
"""


print("=" * 60)
print("OPENSTREETMAP OVERPASS API TEST")
print("=" * 60)

print("Latitude:", latitude)
print("Longitude:", longitude)
print("Search Radius:", radius, "metres")


try:

    response = requests.post(
        OVERPASS_URL,
        data={"data": query},
        headers={
            "User-Agent": "EVChargingStationPlanner/1.0 (Academic Project)",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        timeout=90
    )

    print("\nStatus Code:", response.status_code)

    response.raise_for_status()

    data = response.json()

    if data.get("remark"):
        raise ValueError(
            "Overpass returned a warning or incomplete result"
        )

    elements = data.get("elements", [])

    print("Total Elements Found:", len(elements))


    # Count geographical categories
    category_counts = Counter()


    for element in elements:

        tags = element.get("tags", {})

        if "amenity" in tags:

            category = tags["amenity"]

        elif "shop" in tags:

            category = tags["shop"]

        elif "tourism" in tags:

            category = tags["tourism"]

        elif "office" in tags:

            category = "office"

        elif "highway" in tags:

            category = "road_" + tags["highway"]

        else:

            category = "unknown"

        category_counts[category] += 1


    # Print category distribution
    print("\n" + "=" * 60)
    print("INFRASTRUCTURE CATEGORY DISTRIBUTION")
    print("=" * 60)


    for category, count in category_counts.most_common():

        print(f"{category}: {count}")


    # Display sample records
    print("\n" + "=" * 60)
    print("FIRST 10 INFRASTRUCTURE RECORDS")
    print("=" * 60)


    for element in elements[:10]:

        tags = element.get("tags", {})

        center = element.get("center", {})

        lat = element.get("lat", center.get("lat"))

        lon = element.get("lon", center.get("lon"))


        print("\nOSM ID:", element.get("id"))

        print("Element Type:", element.get("type"))

        print("Name:", tags.get("name", "Unknown"))

        print("Latitude:", lat)

        print("Longitude:", lon)

        print("Tags:", tags)

        print("-" * 50)


    # Save raw OpenStreetMap data
    output_dir = BASE_DIR / "data" / "raw"

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        output_dir / "osm_infrastructure_hyderabad.json"
    )


    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )


    print("\nData saved successfully:")

    print(output_path)

    print("\nData Source: OpenStreetMap Contributors")

    print("License: Open Database License (ODbL)")

    print("Attribution: https://www.openstreetmap.org/copyright")


    print("\n" + "=" * 60)
    print("OVERPASS API TEST COMPLETED")
    print("=" * 60)


except requests.Timeout:

    print("Overpass API request timed out")


except requests.RequestException as error:

    print("Unable to retrieve Overpass API data")

    print("Error:", error)

    if error.response is not None:

        print("Status Code:", error.response.status_code)

        print("Response:", error.response.text[:2000])


except ValueError as error:

    print("Data processing error:", error)