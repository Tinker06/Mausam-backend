from app.services.weather_service import (
    get_weather,
    get_forecast,
    get_forecast_by_coordinates
)


def analyze_warning(forecast):

    high_rain = any(
        item["rain_probability"] >= 0.70
        for item in forecast
    )

    strong_wind = any(
        item["wind_speed"] >= 15
        for item in forecast
    )

    heavy_rain = any(
        item["rain_probability"] >= 0.90
        for item in forecast
    )

    extreme_heat = any(
        item["temperature"] >= 38
        for item in forecast
    )

    # Highest severity condition
    if heavy_rain and strong_wind:

        return {
            "severity": "SEVERE",
            "message": "Heavy rain and strong winds may occur",
            "reason": "Very high rain probability combined with strong winds",
            "conditions": [
                "Heavy rain",
                "Strong winds"
            ]
        }

    elif heavy_rain:

        return {
            "severity": "SEVERE",
            "message": "Heavy rain may be possible",
            "reason": "Very high rain probability is expected",
            "conditions": [
                "Heavy rain"
            ]
        }

    elif strong_wind:

        return {
            "severity": "MODERATE",
            "message": "Strong winds may be possible",
            "reason": "High wind speeds are expected",
            "conditions": [
                "Strong winds"
            ]
        }

    elif high_rain:

        return {
            "severity": "MODERATE",
            "message": "Rain may be possible",
            "reason": "High rain probability is expected",
            "conditions": [
                "Rain"
            ]
        }

    elif extreme_heat:

        return {
            "severity": "MODERATE",
            "message": "High temperature conditions may occur",
            "reason": "Temperature may reach 38°C or above",
            "conditions": [
                "High temperature"
            ]
        }

    return {
        "severity": "NORMAL",
        "message": "No significant weather warning",
        "reason": "Forecast conditions are within the prototype's warning thresholds",
        "conditions": []
    }


async def get_warning(city: str):

    weather = await get_weather(city)
    forecast_data = await get_forecast(city)

    warning = analyze_warning(
        forecast_data["forecast"]
    )

    return {
        "city": weather["city"],
        "warning": warning
    }


async def get_warning_by_coordinates(
    latitude: float,
    longitude: float
):

    forecast_data = await get_forecast_by_coordinates(
        latitude,
        longitude
    )

    warning = analyze_warning(
        forecast_data["forecast"]
    )

    return {
        "city": forecast_data["city"],
        "warning": warning
    }