import requests

from fastapi import APIRouter, Query, HTTPException

from app.services.ev_station_service import (
    get_nearby_ev_stations
)

from app.schemas.station_schema import (
    NearbyStationsResponse
)


# Create station router
router = APIRouter(
    prefix="/api/v1/stations",
    tags=["EV Charging Stations"]
)


# Retrieve nearby EV charging stations
@router.get(
    "/nearby",
    response_model=NearbyStationsResponse
)
def nearby_stations(

    latitude: float = Query(
        ...,
        ge=-90,
        le=90,
        description="Latitude of selected location"
    ),

    longitude: float = Query(
        ...,
        ge=-180,
        le=180,
        description="Longitude of selected location"
    ),

    radius_km: float = Query(
        10,
        gt=0,
        le=100,
        description="Search radius in kilometres"
    ),

    max_results: int = Query(
        100,
        ge=1,
        le=500,
        description="Maximum station records"
    )
):

    try:

        result = get_nearby_ev_stations(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            max_results=max_results
        )

        return result

    except requests.Timeout:

        raise HTTPException(
            status_code=504,
            detail="Charging station provider timed out"
        )

    except requests.HTTPError as error:

        if (
            error.response is not None
            and error.response.status_code == 429
        ):

            raise HTTPException(
                status_code=503,
                detail="Provider request limit reached"
            )

        raise HTTPException(
            status_code=502,
            detail="Charging station provider returned an error"
        )

    except requests.RequestException:

        raise HTTPException(
            status_code=502,
            detail="Unable to connect to charging station provider"
        )

    except ValueError:

        raise HTTPException(
            status_code=500,
            detail="Unable to process charging station data"
        )