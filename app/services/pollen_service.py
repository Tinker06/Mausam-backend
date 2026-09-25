import httpx

from app.services.cache_service import (
    get_cached,
    get_stale_cached,
    set_cached
)


async def get_pollen(
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

    cache_key = f"pollen_{latitude}_{longitude}"

    # Check fresh cache
    cached_data = get_cached(cache_key)

    if cached_data is not None:
        return cached_data

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

    try:

        async with httpx.AsyncClient(
            timeout=10.0
        ) as client:

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

            if not has_pollen_data:

                pollen_data = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "timezone": data["timezone"],
                    "available": False,
                    "message": (
                        "Pollen data is not available "
                        "for this location"
                    ),
                    "forecast": []
                }

                # Cache the unavailable-data response too
                set_cached(
                    cache_key,
                    pollen_data
                )

                return pollen_data

            pollen_data = {
                "latitude": latitude,
                "longitude": longitude,
                "timezone": data["timezone"],
                "available": True,
                "message": "Pollen data available",
                "forecast": pollen_forecast
            }

            # Save fresh data
            set_cached(
                cache_key,
                pollen_data
            )

            return pollen_data

    except httpx.RequestError:

        # Network / timeout failure
        stale_data = get_stale_cached(
            cache_key
        )

        if stale_data is not None:

            print(
                "FALLBACK → Using stale pollen data"
            )

            return stale_data

        raise ValueError(
            "Pollen service is temporarily unavailable"
        )

    except httpx.HTTPStatusError:

        # Open-Meteo server/API failure
        stale_data = get_stale_cached(
            cache_key
        )

        if stale_data is not None:

            print(
                "FALLBACK → Using stale pollen data"
            )

            return stale_data

        raise ValueError(
            "Pollen service is temporarily unavailable"
        )