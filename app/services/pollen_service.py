import httpx


async def get_pollen(latitude: float, longitude: float):

    if not -90 <= latitude <= 90:
        raise ValueError(
            "Latitude must be between -90 and 90"
        )

    if not -180 <= longitude <= 180:
        raise ValueError(
            "Longitude must be between -180 and 180"
        )

    url = "https://air-quality-api.open-meteo.com/v1/air-quality"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": (
            "alder_pollen,"
            "birch_pollen,"
            "grass_pollen,"
            "mugwort_pollen,"
            "olive_pollen,"
            "ragweed_pollen"
        ),
        "forecast_days": 4,
        "timezone": "auto"
    }

    async with httpx.AsyncClient() as client:

        response = await client.get(
            url,
            params=params
        )

        response.raise_for_status()

        data = response.json()

        hourly = data["hourly"]

        times = hourly["time"]

        pollen_forecast = []

        for i in range(len(times)):

            pollen_forecast.append({
                "time": times[i],
                "alder": hourly["alder_pollen"][i],
                "birch": hourly["birch_pollen"][i],
                "grass": hourly["grass_pollen"][i],
                "mugwort": hourly["mugwort_pollen"][i],
                "olive": hourly["olive_pollen"][i],
                "ragweed": hourly["ragweed_pollen"][i]
            })

        # Check whether pollen data is actually available
        pollen_values = []

        for item in pollen_forecast:
            pollen_values.extend([
                item["alder"],
                item["birch"],
                item["grass"],
                item["mugwort"],
                item["olive"],
                item["ragweed"]
            ])

        has_pollen_data = any(
            value is not None
            for value in pollen_values
        )

        # If pollen data is unavailable
        if not has_pollen_data:

            return {
                "latitude": latitude,
                "longitude": longitude,
                "timezone": data["timezone"],
                "available": False,
                "message": "Pollen data is not available for this location",
                "forecast": []
            }

        # If pollen data is available
        return {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": data["timezone"],
            "available": True,
            "message": "Pollen data available",
            "forecast": pollen_forecast
        }