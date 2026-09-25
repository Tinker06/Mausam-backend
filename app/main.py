from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.services.weather_service import get_weather, get_forecast
from app.services.warning_service import get_warning
from app.services.location_service import (
    get_weather_by_location,
    get_saved_location,
    get_weather_for_saved_location,
    get_forecast_for_saved_location,
    get_warning_for_saved_location
)
from app.services.saved_location_service import (
    save_location,
    get_saved_locations
)
from app.models.weather_models import WeatherResponse, ForecastResponse
from app.services.air_quality_service import get_air_quality
from app.services.fitness_service import get_fitness
from app.models.fitness_models import FitnessResponse
from app.services.beach_service import get_beach_data
from app.models.beach_models import BeachResponse
from app.models.uv_models import UVResponse
from app.services.uv_service import get_uv_index
from app.models.pollen_models import PollenResponse
from app.services.pollen_service import get_pollen

app = FastAPI(title="MAUSAM API")
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "MAUSAM Backend"
    }
@app.get("/air-quality")
async def air_quality(latitude: float, longitude: float):
    try:
        return await get_air_quality(latitude, longitude)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch air quality data"
        )
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "MAUSAM Backend is running!"
    }


@app.get("/weather", response_model=WeatherResponse)
async def weather(city: str):
    try:
        return await get_weather(city)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch weather data"
        )


@app.get("/forecast", response_model=ForecastResponse)
async def forecast(city: str):
    try:
        return await get_forecast(city)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch forecast data"
        )

@app.get("/warnings")
async def warnings(city: str):
    try:
        return await get_warning(city)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch warning data"
        )
@app.get("/fitness", response_model=FitnessResponse)
async def fitness(city: str):
    try:
        return await get_fitness(city)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch fitness data"
        )
@app.get("/weather/location")
async def weather_by_location(latitude: float, longitude: float):
    try:
        return await get_weather_by_location(latitude, longitude)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch weather data for location"
        )


@app.post("/locations")
async def create_location(
    city: str,
    latitude: float,
    longitude: float
):
    try:
        return save_location(
            city,
            latitude,
            longitude
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to save location"
        )


@app.get("/locations")
async def locations():
    try:
        return get_saved_locations()

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch saved locations"
        )


@app.get("/locations/{location_id}")
async def get_location(location_id: str):

    try:
        location = await get_saved_location(
            location_id
        )

        if location is None:
            raise HTTPException(
                status_code=404,
                detail="Location not found"
            )

        return location

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch location"
        )


@app.get("/locations/{location_id}/weather")
async def saved_location_weather(
    location_id: str
):

    try:
        result = await get_weather_for_saved_location(
            location_id
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Location not found"
            )

        return result

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch weather for saved location"
        )


@app.get("/locations/{location_id}/forecast")
async def saved_location_forecast(
    location_id: str
):

    try:
        result = await get_forecast_for_saved_location(
            location_id
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Location not found"
            )

        return result

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch forecast for saved location"
        )


@app.get("/locations/{location_id}/warnings")
async def saved_location_warnings(
    location_id: str
):

    try:
        result = await get_warning_for_saved_location(
            location_id
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Location not found"
            )

        return result

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch warning for saved location"
        )
@app.get("/beach", response_model=BeachResponse)
async def beach(latitude: float, longitude: float):
    try:
        if not -90 <= latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90")

        if not -180 <= longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180")

        return await get_beach_data(latitude, longitude)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch beach data"
        )
@app.get("/uv", response_model=UVResponse)
async def uv(latitude: float, longitude: float):

    try:
        return await get_uv_index(latitude, longitude)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch UV data"
        )
       
@app.get("/pollen", response_model=PollenResponse)
async def pollen(latitude: float, longitude: float):

    try:
        return await get_pollen(latitude, longitude)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch pollen data"
        )

