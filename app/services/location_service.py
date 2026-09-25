from app.services.weather_service import (
    get_weather,
    get_forecast_by_coordinates
)
from app.services.warning_service import get_warning_by_coordinates
from app.services.firebase_service import db


async def get_weather_by_location(latitude: float, longitude: float):
    return await get_weather_by_coordinates(latitude, longitude)


async def get_weather_by_coordinates(latitude: float, longitude: float):

    if not -90 <= latitude <= 90:
        raise ValueError("Latitude must be between -90 and 90")

    if not -180 <= longitude <= 180:
        raise ValueError("Longitude must be between -180 and 180")

    import os
    import httpx
    import httpx

    api_key = os.getenv("OPENWEATHER_API_KEY")

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": api_key,
        "units": "metric"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

        response.raise_for_status()

        data = response.json()

        return {
            "city": data["name"],
            "latitude": latitude,
            "longitude": longitude,
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "condition": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"]
        }


async def get_saved_location(location_id: str):
    location_ref = db.collection("saved_locations").document(location_id)

    location_doc = location_ref.get()

    if not location_doc.exists:
        return None

    location_data = location_doc.to_dict()

    return {
        "id": location_doc.id,
        **location_data
    }


async def get_weather_for_saved_location(location_id: str):

    location = await get_saved_location(location_id)

    if location is None:
        return None

    weather = await get_weather_by_coordinates(
        location["latitude"],
        location["longitude"]
    )

    return {
        "location": location,
        "weather": weather
    }


async def get_forecast_for_saved_location(location_id: str):

    location = await get_saved_location(location_id)

    if location is None:
        return None

    forecast = await get_forecast_by_coordinates(
        location["latitude"],
        location["longitude"]
    )

    return {
        "location": location,
        "forecast": forecast
    }


async def get_warning_for_saved_location(location_id: str):

    location = await get_saved_location(location_id)

    if location is None:
        return None

    warning = await get_warning_by_coordinates(
        location["latitude"],
        location["longitude"]
    )

    return {
        "location": location,
        "warning": {
            "city": warning["city"],
            **warning["warning"]
        }
    }