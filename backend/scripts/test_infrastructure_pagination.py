import sys
import time

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(BASE_DIR))


from app.services.infrastructure_service import (
    get_paginated_infrastructure
)


print("=" * 65)
print("INFRASTRUCTURE PAGINATION TEST")
print("=" * 65)


tests = [
    {
        "city": "London",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "category": "offices"
    },
    {
        "city": "Tokyo",
        "latitude": 35.6762,
        "longitude": 139.6503,
        "category": "parking"
    },
    {
        "city": "Hyderabad",
        "latitude": 17.3850,
        "longitude": 78.4867,
        "category": "offices"
    }
]


for test in tests:

    print("\n" + "=" * 65)

    print("City:", test["city"])

    print("Category:", test["category"])

    print("=" * 65)

    try:

        start_time = time.perf_counter()

        result = get_paginated_infrastructure(
            latitude=test["latitude"],
            longitude=test["longitude"],
            category=test["category"],
            radius=1000,
            page_size=100,
            max_pages=3
        )

        elapsed_time = (
            time.perf_counter() - start_time
        )

        print(
            "Pages Fetched:",
            result["pages_fetched"]
        )

        print(
            "Raw Records:",
            result["raw_records"]
        )

        print(
            "Unique Processed Places:",
            result["total_places"]
        )

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

        print(
            "Pagination Stalled:",
            result["pagination_stalled"]
        )

        print(
            "Response Time:",
            round(elapsed_time, 2),
            "seconds"
        )

        nearest = result["nearest_place"]

        if nearest:

            print(
                "Nearest Place:",
                nearest["name"] or "Unknown"
            )

            print(
                "Nearest Distance:",
                nearest["distance_metres"],
                "metres"
            )

        print("Test Status: SUCCESS")

    except Exception as error:

        print("Test Status: FAILED")

        print("Error Type:", type(error).__name__)

        if isinstance(error, TypeError):
            print("Error Details:", str(error))

    time.sleep(2)


print("\n" + "=" * 65)
print("PAGINATION TEST COMPLETED")
print("=" * 65)