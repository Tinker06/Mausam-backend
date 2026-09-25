
from pydantic import BaseModel


class BeachHourlyData(BaseModel):
    time: str
    wave_height: float | None
    wave_direction: float | None
    wave_period: float | None
    water_temperature: float | None
    sea_level: float | None


class BeachResponse(BaseModel):
    latitude: float
    longitude: float
    timezone: str

    current: BeachHourlyData
    forecast: list[BeachHourlyData]

    beach_status: str
    recommendation: str

