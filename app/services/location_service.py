from app.services.weather_service import get_weather


async def get_weather_by_location(latitude: float, longitude: float):
    return await get_weather_by_coordinates(latitude, longitude)


async def get_weather_by_coordinates(latitude: float, longitude: float):
    import os
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