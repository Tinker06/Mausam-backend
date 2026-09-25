
from pydantic import BaseModel


class UVData(BaseModel):
    time: str
    uv_index: float
    uv_level: str


class UVResponse(BaseModel):
    latitude: float
    longitude: float
    timezone: str
    forecast: list[UVData]

