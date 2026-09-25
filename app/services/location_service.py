import os

import httpx

from app.services.weather_service import (
    get_weather,
    get_forecast_by_coordinates
)

from app.services.warning_service import get_warning_by_coordinates

from app.services.cache_service import (
    get_cached,
    get_stale_cached,
    set_cached
)

from app.services.firebase_service import db


async def get_weather_by_location(
    latitude: float,
    longitude: float
):
    return await get_weather_by_coordinates(
        latitude,
        longitude
    )


async def get_weather_by_coordinates(
    latitude: float,
    longitude: float
):

    if not -90 <= latitude <= 90:
        raise ValueError(
            "Latitude must be between -90 and 90"
        )

    if not -180 <= longitude <= 180:
        raise ValueError(
            "Longitude must be between -180 and 180"
        )

    cache_key = f"weather_{latitude}_{longitude}"

    # Check fresh cache
    cached_data = get_cached(cache_key)

    if cached_data is not None:
        return cached_data

    api_key = os.getenv("OPENWEATHER_API_KEY")

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": api_key,
        "units": "metric"
    }

    try:

        async with httpx.AsyncClient(
            timeout=10.0
        ) as client:

            response = await client.get(
                url,
                params=params
            )

            # Invalid API key
            if response.status_code == 401:
                raise ValueError(
                    "Invalid OpenWeather API key"
                )

            # OpenWeather server problem
            if response.status_code >= 500:

                stale_data = get_stale_cached(
                    cache_key
                )

                if stale_data is not None:

                    print(
                        "FALLBACK → Using stale coordinate weather data"
                    )

                    return stale_data

                raise ValueError(
                    "Weather service is temporarily unavailable"
                )

            response.raise_for_status()

            data = response.json()

            weather_data = {
                "city": data["name"],
                "latitude": latitude,
                "longitude": longitude,
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "condition": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"]
            }

            # Save fresh data
            set_cached(
                cache_key,
                weather_data
            )

            return weather_data

    except httpx.RequestError:

        # Network / timeout failure
        stale_data = get_stale_cached(
            cache_key
        )

        if stale_data is not None:

            print(
                "FALLBACK → Using stale coordinate weather data"
            )

            return stale_data

        raise ValueError(
            "Weather service is temporarily unavailable"
        )


async def get_saved_location(
    location_id: str
):

    location_ref = (
        db
        .collection("saved_locations")
        .document(location_id)
    )

    location_doc = location_ref.get()

    if not location_doc.exists:
        return None

    location_data = location_doc.to_dict()

    return {
        "id": location_doc.id,
        **location_data
    }


async def get_weather_for_saved_location(
    location_id: str
):

    location = await get_saved_location(
        location_id
    )

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


async def get_forecast_for_saved_location(
    location_id: str
):

    location = await get_saved_location(
        location_id
    )

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


async def get_warning_for_saved_location(
    location_id: str
):

    location = await get_saved_location(
        location_id
    )

    if location is None:
        return None

    warning = await get_warning_by_coordinates(
        location["latitude"],
        location["longitude"]
    )

    return {
        "location": location,
        "warning": {
            "city": location["city"],
            "severity": warning["warning"]["severity"],
            "message": warning["warning"]["message"],
            "reason": warning["warning"]["reason"],
            "conditions": warning["warning"]["conditions"]
        }
    }