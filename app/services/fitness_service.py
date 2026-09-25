from datetime import datetime, timedelta, timezone

from app.services.weather_service import get_weather, get_forecast


async def get_fitness(city: str):

    weather = await get_weather(city)
    forecast_data = await get_forecast(city)

    forecast = forecast_data["forecast"]

    suitable_hours = []
    alerts = []

    # OpenWeather timezone offset in seconds
    timezone_offset = forecast_data["timezone"]

    # Convert sunrise and sunset from UTC to the city's local time
    sunrise_utc = datetime.fromtimestamp(
        forecast_data["sunrise"],
        tz=timezone.utc
    )

    sunset_utc = datetime.fromtimestamp(
        forecast_data["sunset"],
        tz=timezone.utc
    )

    local_timezone = timezone(
        timedelta(seconds=timezone_offset)
    )

    sunrise_local = sunrise_utc.astimezone(local_timezone)
    sunset_local = sunset_utc.astimezone(local_timezone)

    for item in forecast:

        temperature = item["temperature"]
        wind_speed = item["wind_speed"]
        rain_probability = item["rain_probability"]

        # Forecast datetime returned by OpenWeather is local city time
        forecast_time = datetime.strptime(
            item["datetime"],
            "%Y-%m-%d %H:%M:%S"
        )

        # Add the city's timezone
        forecast_time = forecast_time.replace(
            tzinfo=local_timezone
        )

        # Check whether forecast time is between sunrise and sunset
        is_daytime = (
            sunrise_local <= forecast_time <= sunset_local
        )

        # Check suitable outdoor activity conditions
        if (
            is_daytime
            and temperature <= 32
            and wind_speed < 10
            and rain_probability < 0.40
        ):
            suitable_hours.append(
                item["datetime"]
            )

        # Heat alert
        if temperature >= 35:
            alerts.append(
                "High heat conditions"
            )

        # Wind alert
        if wind_speed >= 10:
            alerts.append(
                "Strong winds possible"
            )

        # Rain alert
        if rain_probability >= 0.40:
            alerts.append(
                "Rain may occur"
            )

    return {
        "city": weather["city"],
        "temperature": weather["temperature"],
        "feels_like": weather["feels_like"],
        "humidity": weather["humidity"],
        "wind_speed": weather["wind_speed"],
        "sunrise": forecast_data["sunrise"],
        "sunset": forecast_data["sunset"],
        "suitable_activity_hours": suitable_hours,
        "alerts": list(set(alerts))
    }