from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from app.routers.station_routes import (
    router as station_router
)

from app.routers.location_routes import (
    router as location_router
)

from app.routers.infrastructure_routes import (
    router as infrastructure_router
)

# Initialize FastAPI application
app = FastAPI(

    title="EV Charging Station Location Planner",

    description=(
        "Worldwide EV charging station discovery, "
        "geospatial analysis and location suitability planning."
    ),

    version="1.0.0"
)


# Allowed frontend origins
origins = [

    "http://localhost:3000",

    "http://127.0.0.1:3000",

    "http://localhost:5173",

    "http://127.0.0.1:5173",
    "https://ev-charging-station-location-planner-1.onrender.com"
]


# Configure CORS
app.add_middleware(

    CORSMiddleware,

    allow_origins=origins,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# Register station router

app.include_router(station_router)

app.include_router(location_router)

app.include_router(infrastructure_router)


# Root endpoint
@app.get("/", tags=["General"])
def root():

    return {

        "project": "EV Charging Station Location Planner",

        "status": "Backend is running",

        "scope": "Worldwide",

        "version": "1.0.0"
    }


# Health check endpoint
@app.get("/health", tags=["General"])
def health():

    return {

        "status": "healthy"
    }
from app.routers.planning_routes import router as planning_router
app.include_router(planning_router)

from app.routers.account_routes import router as account_router
app.include_router(account_router)
