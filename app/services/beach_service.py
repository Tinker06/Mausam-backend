import httpx

from app.services.weather_service import (
    get_forecast_by_coordinates
)

from app.services.cache_service import (
    get_cached,
    get_stale_cached,
    set_cached
)


async def get_beach_data(
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

    cache_key = f"beach_{latitude}_{longitude}"

    # Check fresh cache
    cached_data = get_cached(cache_key)

    if cached_data is not None:
        return cached_data

    # Get weather data
    weather_forecast = await get_forecast_by_coordinates(
        latitude,
        longitude
    )

    weather = weather_forecast["forecast"][0]

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
            wave_heights = hourly["wave_height"]
            wave_directions = hourly["wave_direction"]
            wave_periods = hourly["wave_period"]
            water_temperatures = hourly[
                "sea_surface_temperature"
            ]
            sea_levels = hourly[
                "sea_level_height_msl"
            ]

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

            wave_height = current["wave_height"]
            wind_speed = weather["wind_speed"]
            rain_probability = weather["rain_probability"]

            # Prototype beach-condition rules.
            # These are not official beach-safety standards.

            if wave_height is None:

                beach_status = "UNKNOWN"

                recommendation = (
                    "Beach conditions could not be determined"
                )

            elif wave_height > 1.5 or wind_speed >= 15:

                beach_status = "ROUGH"

                recommendation = (
                    "Rough sea or strong wind conditions"
                )

            elif wave_height >= 1.0 or wind_speed >= 10:

                beach_status = "CAUTION"

                recommendation = (
                    "Moderate sea or wind conditions; "
                    "take care"
                )

            elif rain_probability >= 0.60:

                beach_status = "CAUTION"

                recommendation = (
                    "Rain may affect beach activities"
                )

            else:

                beach_status = "SUITABLE"

                recommendation = (
                    "Relatively calm conditions "
                    "for beach activities"
                )

            beach_data = {
                "latitude": latitude,
                "longitude": longitude,
                "timezone": data["timezone"],
                "current": current,
                "forecast": forecast,
                "beach_status": beach_status,
                "recommendation": recommendation
            }

            # Save fresh data
            set_cached(
                cache_key,
                beach_data
            )

            return beach_data

    except httpx.RequestError:

        # Network / timeout failure
        stale_data = get_stale_cached(cache_key)

        if stale_data is not None:

            print(
                "FALLBACK → Using stale beach data"
            )

            return stale_data

        raise ValueError(
            "Beach service is temporarily unavailable"
        )

    except httpx.HTTPStatusError:

        # Open-Meteo server/API failure
        stale_data = get_stale_cached(cache_key)

        if stale_data is not None:

            print(
                "FALLBACK → Using stale beach data"
            )

            return stale_data

        raise ValueError(
            "Beach service is temporarily unavailable"
        )