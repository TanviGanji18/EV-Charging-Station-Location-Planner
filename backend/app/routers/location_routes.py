import requests

from typing import Optional

from fastapi import APIRouter, Query, HTTPException

from app.services.mapbox_service import (
    search_locations,
    reverse_geocode
)

from app.schemas.location_schema import (
    LocationSearchResponse,
    ReverseGeocodeResponse
)


# Location router
router = APIRouter(

    prefix="/api/v1/locations",

    tags=["Location Search"]
)


# Common provider error handler
def handle_provider_error(error):

    if isinstance(error, requests.Timeout):

        return HTTPException(
            status_code=504,
            detail="Mapbox request timed out"
        )

    if isinstance(error, requests.HTTPError):

        if (
            error.response is not None
            and error.response.status_code == 429
        ):

            return HTTPException(
                status_code=503,
                detail="Mapbox request limit reached"
            )

        return HTTPException(
            status_code=502,
            detail="Mapbox returned an error"
        )

    return HTTPException(
        status_code=502,
        detail="Unable to connect to Mapbox"
    )


# Forward geocoding endpoint
@router.get(
    "/search",
    response_model=LocationSearchResponse
)
def location_search(

    query: str = Query(
        ...,
        min_length=2,
        max_length=200,
        description="Location name or address"
    ),

    limit: int = Query(
        5,
        ge=1,
        le=10,
        description="Maximum search results"
    ),

    country: Optional[str] = Query(
        None,
        pattern=r"^[A-Za-z]{2}$",
        description="Optional ISO country code"
    )
):

    if len(query.strip()) < 2:

        raise HTTPException(
            status_code=422,
            detail="Enter a valid location name"
        )

    try:

        return search_locations(
            query=query,
            limit=limit,
            country=country
        )

    except requests.RequestException as error:

        raise handle_provider_error(error)

    except ValueError:

        raise HTTPException(
            status_code=500,
            detail="Unable to process location data"
        )


# Reverse geocoding endpoint
@router.get(
    "/reverse",
    response_model=ReverseGeocodeResponse
)
def location_reverse(

    latitude: float = Query(
        ...,
        ge=-90,
        le=90,
        description="Selected latitude"
    ),

    longitude: float = Query(
        ...,
        ge=-180,
        le=180,
        description="Selected longitude"
    )
):

    try:

        return reverse_geocode(
            latitude=latitude,
            longitude=longitude
        )

    except requests.RequestException as error:

        raise handle_provider_error(error)

    except ValueError:

        raise HTTPException(
            status_code=500,
            detail="Unable to process location data"
        )