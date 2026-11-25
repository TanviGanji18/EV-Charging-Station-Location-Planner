
import logging
import math

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from concurrent.futures import ThreadPoolExecutor

from app.services.traffic_service import get_traffic
from app.services.ev_station_service import get_nearby_ev_stations
from app.services.infrastructure_service import get_infrastructure_summary


router = APIRouter(
    prefix="/api/v1",
    tags=["Planning"]
)

logger = logging.getLogger(__name__)

WEIGHTS = {
    "coverage_gap": 0.40,
    "commercial_facilities": 0.35,
    "road_proximity": 0.25
}

COMMERCIAL_CATEGORIES = [
    "shopping_malls",
    "supermarkets",
    "restaurants",
    "cafes",
    "hotels",
    "offices",
    "parking"
]

EV_SEARCH_RADIUS_KM = 10
COVERAGE_THRESHOLD_KM = 5
COMMERCIAL_THRESHOLD = 20


# Request schemas

class Site(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    name: str = Field(
        default="Candidate site",
        max_length=200
    )


class Comparison(BaseModel):
    sites: list[Site] = Field(
        min_length=2,
        max_length=4
    )


# Safe external API execution

def safe(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)

    except Exception as error:
        logger.warning(
            "%s failed: %s",
            fn.__name__,
            type(error).__name__
        )

        return {
            "status": "unavailable",
            "reason": "Provider or processing error"
        }


def valid_number(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value >= 0
    )


# Traffic endpoint

@router.get("/traffic")
def traffic(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180)
):
    return safe(
        get_traffic,
        latitude,
        longitude
    )


# Coverage gap calculation

def calculate_coverage(ev):

    stations = ev.get("stations")

    if not isinstance(stations, list):
        return None, None, "unavailable"

    distances = [
        station["distance_km"]
        for station in stations
        if valid_number(station.get("distance_km"))
    ]

    nearest = min(distances) if distances else None

    capped = ev.get("result_limit_reached", False)

    # Zero distance is a valid result.
    # No unreturned station can be closer than zero.

    if nearest == 0:
        return 0.0, nearest, "success"

    # A capped result may omit a closer station.

    if capped:
        return None, nearest, "limited"

    # Successful search with no reported stations.

    if not stations:
        return 100.0, None, "no_reported_stations"

    # Records exist but some distances are invalid.

    if len(distances) != len(stations):
        return None, nearest, "incomplete_distances"

    if nearest is None:
        return None, None, "unavailable"

    gap = min(
        100.0,
        nearest / COVERAGE_THRESHOLD_KM * 100
    )

    return gap, nearest, "success"


# Commercial facilities calculation

def calculate_commercial(categories):

    confirmed_count = 0
    complete = True

    for key in COMMERCIAL_CATEGORIES:

        category = categories.get(key, {})

        count = category.get("count")

        if (
            category.get("status") != "success"
            or not valid_number(count)
        ):
            complete = False
            continue

        confirmed_count += count

        if (
            category.get("result_limit_reached")
            or category.get("pagination_stalled")
        ):
            complete = False

    # The scoring formula reaches its maximum
    # once 20 facility records are confirmed.

    if confirmed_count >= COMMERCIAL_THRESHOLD:
        return 100.0, confirmed_count, "success"

    # Below the threshold, incomplete results
    # cannot establish an exact score.

    if not complete:
        return None, confirmed_count, "partial"

    score = min(
        100.0,
        confirmed_count * 5
    )

    return score, confirmed_count, "success"


# Road proximity calculation

def calculate_road(traffic_data):

    distance = traffic_data.get(
        "nearest_coordinate_metres"
    )

    road_class = traffic_data.get("road_class")

    closure = traffic_data.get("road_closure")

    valid_classes = [
        f"FRC{i}" for i in range(8)
    ]

    if (
        traffic_data.get("status") != "success"
        or not valid_number(distance)
        or road_class not in valid_classes
        or not isinstance(closure, bool)
    ):
        return None

    if closure:
        return 0.0

    road_score = (
        max(0, 100 - distance / 5)
        * (1 - int(road_class[-1]) * 0.08)
    )

    return round(
        max(0, min(100, road_score)),
        5
    )


# Main suitability analysis

def analyze(site):

    latitude = site.latitude
    longitude = site.longitude

    # Fetch independent data concurrently.

    with ThreadPoolExecutor(max_workers=3) as pool:

        ev_future = pool.submit(
            safe,
            get_nearby_ev_stations,
            latitude,
            longitude,
            EV_SEARCH_RADIUS_KM,
            100
        )

        infra_future = pool.submit(
            safe,
            get_infrastructure_summary,
            latitude,
            longitude,
            radius=1000,
            max_pages=1,
            max_workers=2
        )

        traffic_future = pool.submit(
            safe,
            get_traffic,
            latitude,
            longitude
        )

        ev = ev_future.result()
        infra = infra_future.result()
        tr = traffic_future.result()

    # Factor 1: Charging coverage gap

    gap, nearest, coverage_status = (
        calculate_coverage(ev)
    )

    # Factor 2: Commercial facilities

    categories = infra.get(
        "category_summary", {}
    )

    commercial, facility_count, commercial_status = (
        calculate_commercial(categories)
    )

    # Factor 3: Road proximity

    road = calculate_road(tr)

    factors = {
        "coverage_gap": gap,
        "commercial_facilities": commercial,
        "road_proximity": road
    }

    missing_factors = [
        key
        for key, value in factors.items()
        if value is None
    ]

    score = None

    if not missing_factors:

        score = round(
            sum(
                factors[key] * WEIGHTS[key]
                for key in WEIGHTS
            ),
            2
        )

    # Suitability classification

    if score is None:
        suitability = "Insufficient data"

    elif score >= 80:
        suitability = "High"

    elif score >= 60:
        suitability = "Moderate"

    elif score >= 40:
        suitability = "Low"

    else:
        suitability = "Very Low"

    # Human-readable explanations

    reasons = []

    if gap is not None:

        if nearest is None:
            reasons.append(
                "No charging stations reported "
                "within the search radius."
            )

        elif nearest >= COVERAGE_THRESHOLD_KM:
            reasons.append(
                "The nearest reported charging "
                "station is at least 5 km away."
            )

        else:
            reasons.append(
                f"Nearest reported charging station "
                f"is {nearest:.2f} km away."
            )

    if commercial is not None:
        reasons.append(
            f"At least {facility_count} commercial "
            "facility records identified nearby."
        )

    if road is not None:

        if tr.get("road_closure"):
            reasons.append(
                "The reported road segment is closed."
            )

        else:
            reasons.append(
                "Road proximity evaluated using "
                "TomTom road segment information."
            )

    return {
        "site": site.model_dump(),
        "score": score,
        "status": (
            "success"
            if score is not None
            else "partial"
        ),
        "suitability": suitability,
        "factors": factors,
        "weights": WEIGHTS,
        "missing_factors": missing_factors,
        "nearest_charger_km": nearest,
        "coverage_status": coverage_status,
        "station_search_radius_km": EV_SEARCH_RADIUS_KM,
        "stations_found": ev.get("total_stations"),
        "station_result_limit_reached": ev.get(
            "result_limit_reached"
        ),
        "commercial_facility_count": facility_count,
        "commercial_status": commercial_status,
        "reasons": reasons,
        "traffic": {
            key: value
            for key, value in tr.items()
            if key != "coordinates"
        },
        "infrastructure": categories,
        "method": (
            "Provisional weighted heuristic. "
            "Uses reported charging stations, "
            "commercial facility records and "
            "road proximity. Provider coverage "
            "may be incomplete. Facility counts "
            "may include overlapping categories. "
            "Not validated demand, investment "
            "feasibility or actual road access."
        )
    }


# Individual location analysis endpoint

@router.post("/analysis")
def analysis(site: Site):
    return analyze(site)


# Compare between two and four locations

@router.post("/compare")
def compare(body: Comparison):

    # Sequential site analysis limits concurrent
    # external provider requests.

    results = [
        analyze(site)
        for site in body.sites
    ]

    results.sort(
        key=lambda result: (
            result["score"]
            if result["score"] is not None
            else -1
        ),
        reverse=True
    )

    scored_sites = [
        result
        for result in results
        if result["score"] is not None
    ]

    total_sites = len(results)
    completed_sites = len(scored_sites)

    recommended_site = None
    recommended_score = None

    if scored_sites:

        recommended_site = scored_sites[0]["site"]

        recommended_score = scored_sites[0]["score"]

    if completed_sites == total_sites:
        status = "success"

    elif completed_sites > 0:
        status = "partial"

    else:
        status = "unavailable"

    return {
        "status": status,
        "total_sites": total_sites,
        "successfully_scored_sites": completed_sites,
        "sites": results,
        "recommended_site": recommended_site,
        "recommended_score": recommended_score,
        "recommendation_scope": (
            "All compared sites"
            if status == "success"
            else "Successfully scored sites only"
            if scored_sites
            else "No recommendation available"
        )
    }
