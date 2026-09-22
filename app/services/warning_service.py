from app.services.weather_service import get_weather, get_forecast


async def get_warning(city: str):
    # Get current weather
    weather = await get_weather(city)

    # Get forecast data
    forecast_data = await get_forecast(city)

    forecast = forecast_data["forecast"]

    # Default values
    severity = "NORMAL"
    message = "No significant weather warning"
    reason = "Current weather conditions are within normal range"

    # Check for possible weather risks
    high_rain = any(item["rain_probability"] >= 0.70 for item in forecast)
    strong_wind = any(item["wind_speed"] >= 15 for item in forecast)

    # Severity classification
    if high_rain and strong_wind:
        severity = "SEVERE"
        message = "Severe weather conditions possible"
        reason = "High rain probability and strong winds are expected"

    elif high_rain:
        severity = "MODERATE"
        message = "Heavy rain may be possible"
        reason = "High rain probability is expected"

    elif strong_wind:
        severity = "MODERATE"
        message = "Strong winds may be possible"
        reason = "High wind speeds are expected"

    return {
        "city": weather["city"],
        "warning": {
            "severity": severity,
            "message": message,
            "reason": reason
        }
    }