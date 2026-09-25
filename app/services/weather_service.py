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


async def get_weather(city: str):

    cache_key = f"weather_{city.lower()}"

    # Check fresh cache
    cached_data = get_cached(cache_key)

    if cached_data is not None:
        return cached_data

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    try:

        async with httpx.AsyncClient(timeout=10.0) as client:

            response = await client.get(
                url,
                params=params
            )

            # Invalid city
            if response.status_code == 404:
                raise ValueError("City not found")

            # Invalid API key
            if response.status_code == 401:
                raise ValueError("Invalid OpenWeather API key")

            # OpenWeather server problem
            if response.status_code >= 500:

                stale_data = get_stale_cached(cache_key)

                if stale_data is not None:
                    print("FALLBACK → Using stale weather data")
                    return stale_data

                raise ValueError(
                    "Weather service is temporarily unavailable"
                )

            response.raise_for_status()

            data = response.json()

            weather_data = {
                "city": data["name"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "condition": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"]
            }

            # Save fresh data
            set_cached(cache_key, weather_data)

            return weather_data

    except httpx.RequestError:

        # Network / timeout failure
        stale_data = get_stale_cached(cache_key)

        if stale_data is not None:
            print("FALLBACK → Using stale weather data")
            return stale_data

        raise ValueError(
            "Weather service is temporarily unavailable"
        )


async def get_forecast(city: str):

    cache_key = f"forecast_{city.lower()}"

    # Check fresh cache
    cached_data = get_cached(cache_key)

    if cached_data is not None:
        return cached_data

    url = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    try:

        async with httpx.AsyncClient(timeout=10.0) as client:

            response = await client.get(
                url,
                params=params
            )

            # Invalid city
            if response.status_code == 404:
                raise ValueError("City not found")

            # Invalid API key
            if response.status_code == 401:
                raise ValueError("Invalid OpenWeather API key")

            # OpenWeather server problem
            if response.status_code >= 500:

                stale_data = get_stale_cached(cache_key)

                if stale_data is not None:
                    print("FALLBACK → Using stale forecast data")
                    return stale_data

                raise ValueError(
                    "Weather service is temporarily unavailable"
                )

            response.raise_for_status()

            data = response.json()

            forecast = []

            for item in data["list"]:

                forecast.append({
                    "datetime": item["dt_txt"],
                    "temperature": item["main"]["temp"],
                    "feels_like": item["main"]["feels_like"],
                    "humidity": item["main"]["humidity"],
                    "condition": item["weather"][0]["description"],
                    "wind_speed": item["wind"]["speed"],
                    "rain_probability": item["pop"]
                })

            forecast_data = {
                "city": data["city"]["name"],
                "sunrise": data["city"]["sunrise"],
                "sunset": data["city"]["sunset"],
                "timezone": data["city"]["timezone"],
                "forecast": forecast
            }

            # Save fresh forecast
            set_cached(cache_key, forecast_data)

            return forecast_data

    except httpx.RequestError:

        # Network / timeout failure
        stale_data = get_stale_cached(cache_key)

        if stale_data is not None:
            print("FALLBACK → Using stale forecast data")
            return stale_data

        raise ValueError(
            "Weather service is temporarily unavailable"
        )


async def get_forecast_by_coordinates(
    latitude: float,
    longitude: float
):

    cache_key = f"forecast_{latitude}_{longitude}"

    # Check fresh cache
    cached_data = get_cached(cache_key)

    if cached_data is not None:
        return cached_data

    url = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": API_KEY,
        "units": "metric"
    }

    try:

        async with httpx.AsyncClient(timeout=10.0) as client:

            response = await client.get(
                url,
                params=params
            )

            # Invalid API key
            if response.status_code == 401:
                raise ValueError("Invalid OpenWeather API key")

            # OpenWeather server problem
            if response.status_code >= 500:

                stale_data = get_stale_cached(cache_key)

                if stale_data is not None:
                    print(
                        "FALLBACK → Using stale coordinate forecast data"
                    )
                    return stale_data

                raise ValueError(
                    "Weather service is temporarily unavailable"
                )

            response.raise_for_status()

            data = response.json()

            forecast = []

            for item in data["list"]:

                forecast.append({
                    "datetime": item["dt_txt"],
                    "temperature": item["main"]["temp"],
                    "feels_like": item["main"]["feels_like"],
                    "humidity": item["main"]["humidity"],
                    "condition": item["weather"][0]["description"],
                    "wind_speed": item["wind"]["speed"],
                    "rain_probability": item["pop"]
                })

            forecast_data = {
                "city": data["city"]["name"],
                "sunrise": data["city"]["sunrise"],
                "sunset": data["city"]["sunset"],
                "timezone": data["city"]["timezone"],
                "forecast": forecast
            }

            # Save fresh coordinate forecast
            set_cached(
                cache_key,
                forecast_data
            )

            return forecast_data

    except httpx.RequestError:

        # Network / timeout failure
        stale_data = get_stale_cached(cache_key)

        if stale_data is not None:
            print(
                "FALLBACK → Using stale coordinate forecast data"
            )
            return stale_data

        raise ValueError(
            "Weather service is temporarily unavailable"
        )