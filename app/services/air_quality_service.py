import os

import httpx

from dotenv import load_dotenv

from app.services.cache_service import (
    get_cached,
    get_stale_cached,
    set_cached
)


load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")


async def get_air_quality(
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

    cache_key = f"air_quality_{latitude}_{longitude}"

    # Check fresh cache
    cached_data = get_cached(cache_key)

    if cached_data is not None:
        return cached_data

    url = "https://api.openweathermap.org/data/2.5/air_pollution"

    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": API_KEY
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
                        "FALLBACK → Using stale air quality data"
                    )

                    return stale_data

                raise ValueError(
                    "Air quality service is temporarily unavailable"
                )

            response.raise_for_status()

            data = response.json()

            air_data = data["list"][0]

            air_quality_data = {
                "latitude": latitude,
                "longitude": longitude,
                "aqi": air_data["main"]["aqi"],
                "pm2_5": air_data["components"]["pm2_5"],
                "pm10": air_data["components"]["pm10"],
                "co": air_data["components"]["co"],
                "no2": air_data["components"]["no2"],
                "o3": air_data["components"]["o3"]
            }

            # Save fresh data
            set_cached(
                cache_key,
                air_quality_data
            )

            return air_quality_data

    except httpx.RequestError:

        # Network / timeout failure
        stale_data = get_stale_cached(
            cache_key
        )

        if stale_data is not None:

            print(
                "FALLBACK → Using stale air quality data"
            )

            return stale_data

        raise ValueError(
            "Air quality service is temporarily unavailable"
        )