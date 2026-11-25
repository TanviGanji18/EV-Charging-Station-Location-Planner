from pydantic import BaseModel

from typing import Optional, List


# Individual location
class LocationSchema(BaseModel):

    location_id: Optional[str] = None

    name: Optional[str] = None

    full_address: Optional[str] = None

    feature_type: Optional[str] = None

    latitude: float

    longitude: float

    country: Optional[str] = None

    country_code: Optional[str] = None

    region: Optional[str] = None

    district: Optional[str] = None

    city: Optional[str] = None

    locality: Optional[str] = None

    neighborhood: Optional[str] = None

    postcode: Optional[str] = None

    bounding_box: Optional[List[float]] = None

    data_source: str


# Forward geocoding response
class LocationSearchResponse(BaseModel):

    query: str

    total_results: int

    locations: List[LocationSchema]

    attribution: Optional[str] = None


# Selected coordinates
class SelectedLocationSchema(BaseModel):

    latitude: float

    longitude: float


# Reverse geocoding response
class ReverseGeocodeResponse(BaseModel):

    selected_location: SelectedLocationSchema

    total_results: int

    best_match: Optional[LocationSchema] = None

    locations: List[LocationSchema]

    attribution: Optional[str] = None