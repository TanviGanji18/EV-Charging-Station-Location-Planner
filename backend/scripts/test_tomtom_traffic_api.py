import os
import time
import requests

from pathlib import Path
from dotenv import load_dotenv


# --------------------------------------------------
# 1. Load environment variables
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("TOMTOM_API_KEY")

if not API_KEY:
    raise SystemExit("TomTom API key not found")


# --------------------------------------------------
# 2. Traffic Flow Segment API
# --------------------------------------------------

BASE_URL = (
    "https://api.tomtom.com/traffic/services/4/"
    "flowSegmentData/absolute/15/json"
)


# --------------------------------------------------
# 3. Test location
# --------------------------------------------------

latitude = 17.3850

longitude = 78.4867


params = {
    "key": API_KEY,
    "point": f"{latitude},{longitude}",
    "unit": "kmph"
}


# --------------------------------------------------
# 4. Execute API request
# --------------------------------------------------

print("=" * 65)
print("TOMTOM TRAFFIC API TEST")
print("=" * 65)

print("Location: Hyderabad, India")

print("Latitude:", latitude)

print("Longitude:", longitude)

try:

    start_time = time.perf_counter()

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=(10, 30)
    )

    elapsed_time = round(
        time.perf_counter() - start_time,
        2
    )

    print("Status Code:", response.status_code)

    print("Response Time:", elapsed_time, "seconds")


    # ----------------------------------------------
    # 5. Handle unsuccessful responses
    # ----------------------------------------------

    if response.status_code != 200:

        print("Traffic API request failed")

        print(
            "Error Response:",
            response.text.replace(API_KEY, "[REDACTED]")[:500]
        )

        raise SystemExit(1)


    # ----------------------------------------------
    # 6. Extract traffic information
    # ----------------------------------------------

    data = response.json()

    traffic = data.get("flowSegmentData")

    if not isinstance(traffic, dict):

        raise SystemExit(
            "Traffic segment data not available"
        )

    current_speed = traffic.get("currentSpeed")

    free_flow_speed = traffic.get("freeFlowSpeed")

    current_travel_time = traffic.get(
        "currentTravelTime"
    )

    free_flow_travel_time = traffic.get(
        "freeFlowTravelTime"
    )

    confidence = traffic.get("confidence")

    road_closure = traffic.get("roadClosure")

    road_class = traffic.get("frc")

    coordinates = (
        traffic.get("coordinates") or {}
    ).get("coordinate", [])


    # ----------------------------------------------
    # 7. Calculate traffic slowdown
    # ----------------------------------------------

    congestion_percentage = None

    if (
        current_speed is not None
        and free_flow_speed is not None
        and current_speed >= 0
        and free_flow_speed > 0
    ):

        congestion_percentage = round(
            max(
                0,
                min(
                    100,
                    (
                        1 - current_speed / free_flow_speed
                    ) * 100
                )
            ),
            2
        )


    # ----------------------------------------------
    # 8. Calculate additional travel delay
    # ----------------------------------------------

    travel_delay = None

    if (
        current_travel_time is not None
        and free_flow_travel_time is not None
    ):

        travel_delay = max(
            0,
            current_travel_time - free_flow_travel_time
        )


    # ----------------------------------------------
    # 9. Display traffic information
    # ----------------------------------------------

    print("\n" + "=" * 65)

    print("TRAFFIC INFORMATION")

    print("=" * 65)

    print("Road Classification:", road_class)

    print("Current Speed:", current_speed, "km/h")

    print("Free Flow Speed:", free_flow_speed, "km/h")

    print(
        "Current Travel Time:",
        current_travel_time,
        "seconds"
    )

    print(
        "Free Flow Travel Time:",
        free_flow_travel_time,
        "seconds"
    )

    print("Travel Delay:", travel_delay, "seconds")

    print("Confidence:", confidence)

    print("Road Closure:", road_closure)

    print("Congestion Percentage:", congestion_percentage)

    print("Road Coordinate Points:", len(coordinates))


    # ----------------------------------------------
    # 10. Display road coordinates
    # ----------------------------------------------

    print("\nFIRST 5 ROAD COORDINATES")

    for index, coordinate in enumerate(
        coordinates[:5],
        start=1
    ):

        print(
            f"Point {index}:",
            coordinate.get("latitude"),
            coordinate.get("longitude")
        )


    print("\n" + "=" * 65)

    print("TRAFFIC API CONNECTION SUCCESSFUL")

    print("Data Provider: TomTom")

    print("=" * 65)


except requests.Timeout:

    print("Traffic API request timed out")

    raise SystemExit(1)


except requests.RequestException as error:

    print("Request Failed:", type(error).__name__)

    raise SystemExit(1)


except ValueError:

    print("Invalid traffic API response")

    raise SystemExit(1)