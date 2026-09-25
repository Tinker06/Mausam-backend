
import httpx

from app.services.weather_service import get_forecast_by_coordinates


async def get_beach_data(latitude: float, longitude: float):

    # Get weather forecast for the same location
    weather_forecast = await get_forecast_by_coordinates(
        latitude,
        longitude
    )

    weather = weather_forecast["forecast"][0]

    # Marine API
    url = "https://marine-api.open-meteo.com/v1/marine"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": (
            "wave_height,"
            "wave_direction,"
            "wave_period,"
            "sea_surface_temperature,"
            "sea_level_height_msl"
        ),
        "forecast_days": 1,
        "timezone": "auto"
    }

    async with httpx.AsyncClient() as client:

        response = await client.get(url, params=params)

        response.raise_for_status()

        data = response.json()

        hourly = data["hourly"]

        times = hourly["time"]
        wave_heights = hourly["wave_height"]
        wave_directions = hourly["wave_direction"]
        wave_periods = hourly["wave_period"]
        water_temperatures = hourly["sea_surface_temperature"]
        sea_levels = hourly["sea_level_height_msl"]

        forecast = []

        for i in range(len(times)):

            forecast.append({
                "time": times[i],
                "wave_height": wave_heights[i],
                "wave_direction": wave_directions[i],
                "wave_period": wave_periods[i],
                "water_temperature": water_temperatures[i],
                "sea_level": sea_levels[i]
            })

        current = forecast[0]

        # Marine conditions
        wave_height = current["wave_height"]

        # Weather conditions
        wind_speed = weather["wind_speed"]
        rain_probability = weather["rain_probability"]

        # Prototype beach-condition rules.
        # These are not official beach-safety standards.

        if wave_height is None:
            beach_status = "UNKNOWN"
            recommendation = "Beach conditions could not be determined"

        elif wave_height > 1.5 or wind_speed >= 15:
            beach_status = "ROUGH"
            recommendation = "Rough sea or strong wind conditions"

        elif wave_height >= 1.0 or wind_speed >= 10:
            beach_status = "CAUTION"
            recommendation = "Moderate sea or wind conditions; take care"

        elif rain_probability >= 0.60:
            beach_status = "CAUTION"
            recommendation = "Rain may affect beach activities"

        else:
            beach_status = "SUITABLE"
            recommendation = "Relatively calm conditions for beach activities"

        return {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": data["timezone"],
            "current": current,
            "forecast": forecast,
            "beach_status": beach_status,
            "recommendation": recommendation
        }

