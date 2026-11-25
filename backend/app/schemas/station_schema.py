from pydantic import BaseModel
from typing import Optional, List


# Individual charging connection
class ConnectionSchema(BaseModel):

    connection_id: int

    connector_type: str

    charging_level: str

    power_kw: Optional[float] = None

    voltage: Optional[float] = None

    amps: Optional[float] = None

    current_type: str

    quantity: Optional[int] = None

    operational_status: str

    is_operational: Optional[bool] = None


# Individual charging station
class StationSchema(BaseModel):

    station_id: int

    station_name: str

    address: Optional[str] = None

    city: str

    state: str

    postcode: Optional[str] = None

    country: Optional[str] = None

    country_code: Optional[str] = None

    continent_code: Optional[str] = None

    latitude: float

    longitude: float

    distance_km: Optional[float] = None

    operator: str

    charging_points: Optional[int] = None

    usage_type: str

    usage_cost: Optional[str] = None

    operational_status: str

    is_operational: Optional[bool] = None

    connector_types: List[str]

    max_power_kw: Optional[float] = None

    connections: List[ConnectionSchema]

    last_verified: Optional[str] = None

    last_status_update: Optional[str] = None

    recently_verified: Optional[bool] = None

    data_quality_level: Optional[int] = None

    data_provider: Optional[str] = None

    data_license: Optional[str] = None

    is_open_data_licensed: Optional[bool] = None

    data_source: str


# Selected geographical location
class SearchLocationSchema(BaseModel):

    latitude: float

    longitude: float


# Complete nearby station response
class NearbyStationsResponse(BaseModel):

    search_location: SearchLocationSchema

    radius_km: float

    max_results: int

    total_stations: int

    result_limit_reached: bool

    stations: List[StationSchema]