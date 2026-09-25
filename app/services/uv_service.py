import httpx

from app.services.cache_service import (
    get_cached,
    get_stale_cached,
    set_cached
)


async def get_uv_index(
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

    cache_key = f"uv_{latitude}_{longitude}"

    # Check fresh cache
    cached_data = get_cached(cache_key)

    if cached_data is not None:
        return cached_data

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "uv_index",
        "forecast_days": 1,
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

            uv_data = {
                "latitude": latitude,
                "longitude": longitude,
                "timezone": data["timezone"],
                "forecast": forecast
            }

            # Save fresh data
            set_cached(
                cache_key,
                uv_data
            )

            return uv_data

    except httpx.RequestError:

        # Network / timeout failure
        stale_data = get_stale_cached(cache_key)

        if stale_data is not None:

            print(
                "FALLBACK → Using stale UV data"
            )

            return stale_data

        raise ValueError(
            "UV service is temporarily unavailable"
        )

    except httpx.HTTPStatusError:

        # Open-Meteo server/API failure
        stale_data = get_stale_cached(cache_key)

        if stale_data is not None:

            print(
                "FALLBACK → Using stale UV data"
            )

            return stale_data

        raise ValueError(
            "UV service is temporarily unavailable"
        )