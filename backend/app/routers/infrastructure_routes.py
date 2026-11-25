import requests

from fastapi import APIRouter, Query, HTTPException

from app.services.infrastructure_service import (
    INFRASTRUCTURE_CATEGORIES,
    get_paginated_infrastructure,
    get_infrastructure_summary
)

from app.schemas.infrastructure_schema import (
    NearbyInfrastructureResponse,
    InfrastructureSummaryResponse,
    InfrastructureCategoriesResponse
)


# --------------------------------------------------
# 1. Initialize router
# --------------------------------------------------

router = APIRouter(
    prefix="/api/v1/infrastructure",
    tags=["Infrastructure"]
)


# --------------------------------------------------
# 2. Provider error handling
# --------------------------------------------------

def handle_provider_error(error):

    if isinstance(error, requests.Timeout):

        raise HTTPException(
            status_code=504,
            detail="Infrastructure provider timed out"
        )

    if isinstance(error, requests.HTTPError):

        response = error.response

        status = (
            response.status_code
            if response is not None
            else None
        )

        if status == 429:

            raise HTTPException(
                status_code=503,
                detail="Infrastructure provider rate limit reached"
            )

    if isinstance(error, requests.RequestException):

        raise HTTPException(
            status_code=502,
            detail="Infrastructure provider request failed"
        )

    raise HTTPException(
        status_code=500,
        detail="Infrastructure processing failed"
    )


# --------------------------------------------------
# 3. Get supported infrastructure categories
# --------------------------------------------------

@router.get(
    "/categories",
    response_model=InfrastructureCategoriesResponse
)
def get_categories():

    return {
        "total_categories":
            len(INFRASTRUCTURE_CATEGORIES),

        "categories":
            INFRASTRUCTURE_CATEGORIES
    }


# --------------------------------------------------
# 4. Get nearby category-specific infrastructure
# --------------------------------------------------

@router.get(
    "/nearby",
    response_model=NearbyInfrastructureResponse
)
def nearby_infrastructure(

    latitude: float = Query(
        ...,
        ge=-90,
        le=90
    ),

    longitude: float = Query(
        ...,
        ge=-180,
        le=180
    ),

    category: str = Query(...),

    radius: int = Query(
        1000,
        ge=1,
        le=10000
    ),

    page_size: int = Query(
        100,
        ge=1,
        le=100
    ),

    max_pages: int = Query(
        1,
        ge=1,
        le=3
    )

):

    if category not in INFRASTRUCTURE_CATEGORIES:

        raise HTTPException(
            status_code=422,
            detail={
                "message":
                    "Invalid infrastructure category",

                "supported_categories":
                    list(INFRASTRUCTURE_CATEGORIES)
            }
        )

    try:

        return get_paginated_infrastructure(
            latitude=latitude,
            longitude=longitude,
            category=category,
            radius=radius,
            page_size=page_size,
            max_pages=max_pages
        )

    except Exception as error:

        handle_provider_error(error)


# --------------------------------------------------
# 5. Get combined infrastructure summary
# --------------------------------------------------

@router.get(
    "/summary",
    response_model=InfrastructureSummaryResponse
)
def infrastructure_summary(

    latitude: float = Query(
        ...,
        ge=-90,
        le=90
    ),

    longitude: float = Query(
        ...,
        ge=-180,
        le=180
    ),

    radius: int = Query(
        1000,
        ge=1,
        le=5000
    ),

    page_size: int = Query(
        100,
        ge=1,
        le=100
    ),

    max_pages: int = Query(
        1,
        ge=1,
        le=3
    )

):

    try:

        result = get_infrastructure_summary(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            page_size=page_size,
            max_pages=max_pages,
            max_workers=2
        )

    except Exception as error:

        handle_provider_error(error)

    if result["status"] == "failed":

        raise HTTPException(
            status_code=503,
            detail="Infrastructure data currently unavailable"
        )

    return result