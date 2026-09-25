from pydantic import BaseModel


class PollenData(BaseModel):
    time: str
    alder: float | None
    birch: float | None
    grass: float | None
    mugwort: float | None
    olive: float | None
    ragweed: float | None


class PollenResponse(BaseModel):
    latitude: float
    longitude: float
    timezone: str
    available: bool
    message: str
    forecast: list[PollenData]