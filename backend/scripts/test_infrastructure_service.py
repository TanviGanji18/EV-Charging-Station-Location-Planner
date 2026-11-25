import sys

from pathlib import Path


# Add backend directory to Python path

BASE_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(BASE_DIR))


from app.services.infrastructure_service import (
    get_nearby_infrastructure
)


# --------------------------------------------------
# 1. Test location
# --------------------------------------------------

latitude = 17.3850

longitude = 78.4867

radius = 1000

category = "offices"


# --------------------------------------------------
# 2. Execute infrastructure service
# --------------------------------------------------

print("=" * 60)
print("INFRASTRUCTURE SERVICE TEST")
print("=" * 60)

try:

    result = get_nearby_infrastructure(
        latitude=latitude,
        longitude=longitude,
        category=category,
        radius=radius,
        limit=100
    )

    print("Location: Hyderabad, India")

    print("Category:", result["category"])

    print("Radius:", result["radius_metres"])

    print("Raw Records:", result["raw_records"])

    print("Processed Places:", result["total_places"])

    print(
        "Invalid Records:",
        result["invalid_records"]
    )

    print(
        "Duplicate Records:",
        result["duplicate_records"]
    )

    print(
        "Result Limit Reached:",
        result["result_limit_reached"]
    )


    # ----------------------------------------------
    # 3. Nearest infrastructure
    # ----------------------------------------------

    nearest = result["nearest_place"]

    print("\nNEAREST INFRASTRUCTURE")

    if nearest:

        print("Name:", nearest["name"])

        print("Address:", nearest["address"])

        print(
            "Distance:",
            nearest["distance_metres"],
            "metres"
        )

    else:

        print("No place with known distance returned")


    # ----------------------------------------------
    # 4. Display first five processed records
    # ----------------------------------------------

    print("\nFIRST 5 PROCESSED RECORDS")

    for index, place in enumerate(
        result["places"][:5],
        start=1
    ):

        print("\nRecord:", index)

        for key, value in place.items():

            print(f"{key}: {value}")

        print("-" * 50)


    print("\n" + "=" * 60)

    print("INFRASTRUCTURE SERVICE TEST SUCCESSFUL")

    print("=" * 60)


except Exception as error:

    # Avoid printing request URLs containing API keys.

    print(
        "Service test failed:",
        type(error).__name__
    )

    raise SystemExit(1)