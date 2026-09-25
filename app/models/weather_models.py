from pydantic import BaseModel


class WeatherResponse(BaseModel):
    city: str
    temperature: float
    feels_like: float
    humidity: int
    condition: str
    wind_speed: float


class ForecastItem(BaseModel):
    datetime: str
    temperature: float
    feels_like: float
    humidity: int
    condition: str
    wind_speed: float
    rain_probability: float


class ForecastResponse(BaseModel):
    city: str
    sunrise: int
    sunset: int
    forecast: list[ForecastItem]