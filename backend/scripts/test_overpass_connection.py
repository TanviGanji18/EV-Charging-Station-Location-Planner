import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Small query: retrieve fuel stations within 500 metres
query = """
[out:json][timeout:25];

node["amenity"="fuel"]
(around:500,17.3850,78.4867);

out body;
"""

print("=" * 60)
print("OVERPASS BASIC CONNECTION TEST")
print("=" * 60)

try:

    response = requests.get(
        OVERPASS_URL,
        params={"data": query},
        headers={
            "User-Agent": "EVChargingStationPlanner/1.0",
            "Accept": "application/json"
        },
        timeout=(10, 45)
    )

    print("Status Code:", response.status_code)

    response.raise_for_status()

    data = response.json()

    if data.get("remark"):
        print("Overpass Warning:", data["remark"])

    else:
        elements = data.get("elements", [])

        print("Total Elements:", len(elements))

        print("Response:", data)

        print("\nCONNECTION SUCCESSFUL")

except requests.ConnectTimeout:

    print("Connection Timeout: Unable to connect to server")

except requests.ReadTimeout:

    print("Read Timeout: Server did not respond in time")

except requests.RequestException as error:

    print("Request Error:", error)

    if error.response is not None:
        print("Response:", error.response.text[:1000])

except ValueError as error:

    print("Invalid JSON response:", error)