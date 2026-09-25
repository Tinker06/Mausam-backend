from pydantic import BaseModel


class FitnessResponse(BaseModel):
    city: str
    temperature: float
    feels_like: float
    humidity: int
    wind_speed: float
    sunrise: int
    sunset: int
    suitable_activity_hours: list[str]
    alerts: list[str]