from typing import Optional

from pydantic import BaseModel, Field


# --------------------------------------------------
# 1. Search location schema
# --------------------------------------------------

class InfrastructureLocationSchema(BaseModel):

    latitude: float = Field(ge=-90, le=90)

    longitude: float = Field(ge=-180, le=180)


# --------------------------------------------------
# 2. Individual infrastructure record
# --------------------------------------------------

class InfrastructurePlaceSchema(BaseModel):

    place_id: str

    name: Optional[str] = None

    address: Optional[str] = None

    latitude: float = Field(ge=-90, le=90)

    longitude: float = Field(ge=-180, le=180)

    distance_metres: Optional[float] = None

    categories: list[str] = Field(
        default_factory=list
    )

    matched_categories: list[str] = Field(
        default_factory=list
    )

    city: Optional[str] = None

    state: Optional[str] = None

    country: Optional[str] = None

    country_code: Optional[str] = None

    postcode: Optional[str] = None

    osm_id: Optional[str] = None

    osm_type: Optional[str] = None

    source: Optional[str] = None

    attribution: Optional[str] = None

    license: Optional[str] = None

    source_url: Optional[str] = None

    provider: str


# --------------------------------------------------
# 3. Category-specific response
# --------------------------------------------------

class NearbyInfrastructureResponse(BaseModel):

    category: str

    search_location: InfrastructureLocationSchema

    radius_metres: int

    pages_fetched: int

    raw_records: int

    total_places: int

    invalid_records: int

    duplicate_records: int

    result_limit_reached: bool

    pagination_stalled: bool

    nearest_place: Optional[
        InfrastructurePlaceSchema
    ] = None

    places: list[InfrastructurePlaceSchema]

    provider: str

    provider_attribution: str


# --------------------------------------------------
# 4. Individual category summary
# --------------------------------------------------

class CategorySummarySchema(BaseModel):

    status: str

    count: Optional[int] = None

    pages_fetched: Optional[int] = None

    result_limit_reached: Optional[bool] = None

    pagination_stalled: Optional[bool] = None

    nearest_place: Optional[str] = None

    nearest_distance_metres: Optional[float] = None

    error_type: Optional[str] = None


# --------------------------------------------------
# 5. Combined infrastructure response
# --------------------------------------------------

class InfrastructureSummaryResponse(BaseModel):

    status: str

    search_location: InfrastructureLocationSchema

    radius_metres: int

    total_categories: int

    successful_categories: int

    failed_categories: list[str]

    truncated_categories: list[str]

    total_pages_fetched: int

    total_raw_records: int

    total_invalid_records: int

    total_duplicate_records: int

    total_unique_places: int

    category_summary: dict[
        str, CategorySummarySchema
    ]

    places: list[InfrastructurePlaceSchema]

    response_time_seconds: float

    provider: str

    provider_attribution: str


# --------------------------------------------------
# 6. Supported categories response
# --------------------------------------------------

class InfrastructureCategoriesResponse(BaseModel):

    total_categories: int

    categories: dict[str, str]