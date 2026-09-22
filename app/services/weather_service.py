
import os

import httpx
from dotenv import load_dotenv
from app.services.cache_service import get_cached, set_cached

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

async def get_weather(city: str):
    cache_key = f"weather_{city.lower()}"

    # Check cache first
    cached_data = get_cached(cache_key)

    if cached_data is not None:
        return cached_data

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

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

        # Save fresh data in cache
        set_cached(cache_key, weather_data)

        return weather_data

async def get_forecast(city: str):
    url = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

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

        return {
            "city": data["city"]["name"],
            "sunrise": data["city"]["sunrise"],
            "sunset": data["city"]["sunset"],
            "forecast": forecast
        }
