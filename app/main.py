from fastapi import FastAPI, HTTPException

from app.services.weather_service import get_weather, get_forecast
from app.services.warning_service import get_warning
from app.services.location_service import get_weather_by_location
app = FastAPI(title="MAUSAM API")


@app.get("/")
def root():
    return {"message": "MAUSAM Backend is running!"}


@app.get("/weather")
async def weather(city: str):
    try:
        return await get_weather(city)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch weather data"
        )

@app.get("/forecast")
async def forecast(city: str):
    try:
        return await get_forecast(city)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch forecast data"
        )
@app.get("/warnings")
async def warnings(city: str):
    try:
        return await get_warning(city)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch warning data"
        )
@app.get("/weather/location")
async def weather_by_location(latitude: float, longitude: float):
    try:
        return await get_weather_by_location(latitude, longitude)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch weather data for location"
        )