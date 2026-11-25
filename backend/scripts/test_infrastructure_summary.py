import sys

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(BASE_DIR))


from app.services.infrastructure_service import (
    get_infrastructure_summary
)


print("=" * 65)
print("INFRASTRUCTURE AGGREGATION TEST")
print("=" * 65)


try:

    result = get_infrastructure_summary(
        latitude=17.3850,
        longitude=78.4867,
        radius=1000,
        page_size=100,
        max_pages=3,
        max_workers=2
    )

    print("Location: Hyderabad, India")

    print("Overall Status:", result["status"])

    print("Radius:", result["radius_metres"])

    print(
        "Total Categories:",
        result["total_categories"]
    )

    print(
        "Successful Categories:",
        result["successful_categories"]
    )

    print(
        "Failed Categories:",
        result["failed_categories"]
    )

    print(
        "Truncated Categories:",
        result["truncated_categories"]
    )

    print(
        "Total Pages Fetched:",
        result["total_pages_fetched"]
    )

    print(
        "Total Raw Records:",
        result["total_raw_records"]
    )

    print(
        "Total Invalid Records:",
        result["total_invalid_records"]
    )

    print(
        "Total Duplicate Records:",
        result["total_duplicate_records"]
    )

    print(
        "Total Unique Places:",
        result["total_unique_places"]
    )

    print(
        "Response Time:",
        result["response_time_seconds"],
        "seconds"
    )


    # ----------------------------------------------
    # Display category summaries
    # ----------------------------------------------

    print("\n" + "=" * 65)

    print("INFRASTRUCTURE CATEGORY SUMMARY")

    print("=" * 65)

    for category, details in (
        result["category_summary"].items()
    ):

        print("\nCategory:", category)

        print("Status:", details["status"])

        print("Count:", details["count"])

        print(
            "Nearest Place:",
            details["nearest_place"]
        )

        print(
            "Nearest Distance:",
            details["nearest_distance_metres"],
            "metres"
        )

        if details["status"] == "success":

            print(
                "Pages Fetched:",
                details["pages_fetched"]
            )

            print(
                "Limit Reached:",
                details["result_limit_reached"]
            )

        else:

            print(
                "Error Type:",
                details["error_type"]
            )

        print("-" * 50)


    # ----------------------------------------------
    # Display nearest five unique places
    # ----------------------------------------------

    print("\nFIRST 5 UNIQUE INFRASTRUCTURE PLACES")

    for index, place in enumerate(
        result["places"][:5],
        start=1
    ):

        print("\nRecord:", index)

        print(
            "Name:",
            place["name"] or "Unknown"
        )

        print(
            "Distance:",
            place["distance_metres"],
            "metres"
        )

        print(
            "Matched Categories:",
            place["matched_categories"]
        )


    print("\n" + "=" * 65)

    print("AGGREGATION TEST STATUS:", result["status"])

    print("=" * 65)

    if result["status"] == "failed":

        raise SystemExit(1)


except Exception as error:

    print("Aggregation test failed")

    print("Error Type:", type(error).__name__)

    raise SystemExit(1)