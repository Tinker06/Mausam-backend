
import httpx


async def get_uv_index(latitude: float, longitude: float):

    # Validate coordinates
    if not -90 <= latitude <= 90:
        raise ValueError("Latitude must be between -90 and 90")

    if not -180 <= longitude <= 180:
        raise ValueError("Longitude must be between -180 and 180")

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "uv_index",
        "forecast_days": 1,
        "timezone": "auto"
    }

    async with httpx.AsyncClient() as client:

        response = await client.get(
            url,
            params=params
        )

        response.raise_for_status()

        data = response.json()

        times = data["hourly"]["time"]
        uv_values = data["hourly"]["uv_index"]

        forecast = []

        for i in range(len(times)):

            uv_index = uv_values[i]

            if uv_index < 3:
                uv_level = "LOW"

            elif uv_index < 6:
                uv_level = "MODERATE"

            elif uv_index < 8:
                uv_level = "HIGH"

            elif uv_index < 11:
                uv_level = "VERY HIGH"

            else:
                uv_level = "EXTREME"

            forecast.append({
                "time": times[i],
                "uv_index": uv_index,
                "uv_level": uv_level
            })

        return {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": data["timezone"],
            "forecast": forecast
        }
