import os
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")


async def get_air_quality(latitude: float, longitude: float):

    url = "https://api.openweathermap.org/data/2.5/air_pollution"

    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": API_KEY
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

        if response.status_code == 401:
            raise ValueError("Invalid OpenWeather API key")

        response.raise_for_status()

        data = response.json()

        air_data = data["list"][0]

        return {
            "latitude": latitude,
            "longitude": longitude,
            "aqi": air_data["main"]["aqi"],
            "pm2_5": air_data["components"]["pm2_5"],
            "pm10": air_data["components"]["pm10"],
            "co": air_data["components"]["co"],
            "no2": air_data["components"]["no2"],
            "o3": air_data["components"]["o3"]
        }