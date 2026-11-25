import os
import time
import math
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


BASE_URL = (
    "https://api.tomtom.com/traffic/services/4/"
    "flowSegmentData/absolute/15/json"
)


# --------------------------------------------------
# 2. Worldwide test locations
# --------------------------------------------------

cities = [
    ("Hyderabad", "India", 17.3850, 78.4867),

    ("London", "United Kingdom", 51.5074, -0.1278),

    ("New York", "USA", 40.7128, -74.0060),

    ("Tokyo", "Japan", 35.6762, 139.6503),

    ("Dubai", "UAE", 25.2048, 55.2708),

    ("Sydney", "Australia", -33.8688, 151.2093),

    ("Singapore", "Singapore", 1.2834, 103.8607),

    ("Paris", "France", 48.8566, 2.3522)
]


# --------------------------------------------------
# 3. Calculate geographical distance
# --------------------------------------------------

def haversine_distance(lat1, lon1, lat2, lon2):

    earth_radius = 6371000

    lat1 = math.radians(lat1)

    lat2 = math.radians(lat2)

    delta_lat = lat2 - lat1

    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    a = max(0, min(1, a))

    c = 2 * math.asin(math.sqrt(a))

    return earth_radius * c


# --------------------------------------------------
# 4. Initialize summary
# --------------------------------------------------

results = []

successful_cities = 0

failed_cities = 0


print("=" * 65)
print("WORLDWIDE TRAFFIC API TEST")
print("=" * 65)

print("Total Planned Cities:", len(cities))


# --------------------------------------------------
# 5. Test each international city
# --------------------------------------------------

for city, country, latitude, longitude in cities:

    print("\n" + "=" * 65)

    print("City:", city)

    print("Country:", country)

    print("Latitude:", latitude)

    print("Longitude:", longitude)

    print("=" * 65)

    params = {
        "key": API_KEY,

        "point": f"{latitude},{longitude}",

        "unit": "kmph"
    }

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


        # ------------------------------------------
        # Handle failed API responses
        # ------------------------------------------

        if response.status_code != 200:

            failed_cities += 1

            print("Traffic Data: Unavailable")

            print(
                "Error Response:",
                response.text.replace(
                    API_KEY, "[REDACTED]"
                )[:300]
            )

            results.append({
                "city": city,
                "status": "failed",
                "http_status": response.status_code
            })

            # Stop on authentication or quota errors

            if response.status_code in (
                401, 403, 429
            ):

                print("Stopping further API requests")

                break

            continue


        # ------------------------------------------
        # Extract traffic data
        # ------------------------------------------

        data = response.json()

        traffic = data.get("flowSegmentData")

        if not isinstance(traffic, dict):

            raise ValueError(
                "Traffic data unavailable"
            )

        current_speed = traffic.get("currentSpeed")

        free_flow_speed = traffic.get("freeFlowSpeed")

        current_time = traffic.get(
            "currentTravelTime"
        )

        free_flow_time = traffic.get(
            "freeFlowTravelTime"
        )

        confidence = traffic.get("confidence")

        road_class = traffic.get("frc")

        road_closure = traffic.get("roadClosure")

        coordinates = (
            traffic.get("coordinates") or {}
        ).get("coordinate", [])


        # ------------------------------------------
        # Calculate congestion percentage
        # ------------------------------------------

        congestion = None

        if (
            current_speed is not None
            and free_flow_speed is not None
            and current_speed >= 0
            and free_flow_speed > 0
        ):

            congestion = round(
                max(
                    0,
                    min(
                        100,
                        (
                            1
                            - current_speed
                            / free_flow_speed
                        ) * 100
                    )
                ),
                2
            )


        # ------------------------------------------
        # Calculate travel delay
        # ------------------------------------------

        travel_delay = None

        if (
            current_time is not None
            and free_flow_time is not None
        ):

            travel_delay = max(
                0,
                current_time - free_flow_time
            )


        # ------------------------------------------
        # Find nearest returned road coordinate
        # ------------------------------------------

        distances = []

        for coordinate in coordinates:

            road_lat = coordinate.get("latitude")

            road_lon = coordinate.get("longitude")

            if (
                isinstance(road_lat, (int, float))
                and isinstance(road_lon, (int, float))
                and -90 <= road_lat <= 90
                and -180 <= road_lon <= 180
            ):

                distance = haversine_distance(
                    latitude,
                    longitude,
                    road_lat,
                    road_lon
                )

                distances.append(distance)

        nearest_coordinate_distance = (
            round(min(distances), 2)
            if distances
            else None
        )


        # ------------------------------------------
        # Display processed traffic data
        # ------------------------------------------

        print("Road Classification:", road_class)

        print("Current Speed:", current_speed, "km/h")

        print(
            "Free Flow Speed:",
            free_flow_speed,
            "km/h"
        )

        print(
            "Current Travel Time:",
            current_time,
            "seconds"
        )

        print(
            "Free Flow Travel Time:",
            free_flow_time,
            "seconds"
        )

        print(
            "Travel Delay:",
            travel_delay,
            "seconds"
        )

        print("Confidence:", confidence)

        print("Road Closure:", road_closure)

        print("Congestion Percentage:", congestion)

        print("Road Coordinate Points:", len(coordinates))

        print(
            "Nearest Road Coordinate Distance:",
            nearest_coordinate_distance,
            "metres"
        )

        print("Test Status: SUCCESS")


        # ------------------------------------------
        # Store summary in memory
        # ------------------------------------------

        results.append({
            "city": city,

            "country": country,

            "status": "success",

            "road_class": road_class,

            "current_speed": current_speed,

            "free_flow_speed": free_flow_speed,

            "congestion": congestion,

            "travel_delay": travel_delay,

            "confidence": confidence,

            "road_closure": road_closure,

            "nearest_coordinate_distance":
                nearest_coordinate_distance,

            "response_time": elapsed_time
        })

        successful_cities += 1


    except (
        requests.RequestException,
        ValueError,
        TypeError
    ) as error:

        failed_cities += 1

        print("Test Status: FAILED")

        print("Error Type:", type(error).__name__)

        results.append({
            "city": city,
            "status": "failed",
            "error_type": type(error).__name__
        })


    finally:

        time.sleep(2)


# --------------------------------------------------
# 6. Worldwide test summary
# --------------------------------------------------

print("\n" + "=" * 65)

print("WORLDWIDE TRAFFIC TEST SUMMARY")

print("=" * 65)

print("Planned Cities:", len(cities))

print("Attempted Cities:", len(results))

print("Successful Cities:", successful_cities)

print("Failed Cities:", failed_cities)


print("\nCITY-WISE TRAFFIC SUMMARY")

for result in results:

    print("-" * 50)

    print("City:", result["city"])

    print("Status:", result["status"])

    if result["status"] == "success":

        print(
            "Road Classification:",
            result["road_class"]
        )

        print(
            "Current Speed:",
            result["current_speed"]
        )

        print(
            "Free Flow Speed:",
            result["free_flow_speed"]
        )

        print(
            "Congestion Percentage:",
            result["congestion"]
        )

        print(
            "Confidence:",
            result["confidence"]
        )

        print(
            "Nearest Road Coordinate Distance:",
            result["nearest_coordinate_distance"],
            "metres"
        )

        print(
            "Response Time:",
            result["response_time"],
            "seconds"
        )


print("\n" + "=" * 65)

print("WORLDWIDE TRAFFIC TEST COMPLETED")

print("Data Provider: TomTom")

print("=" * 65)