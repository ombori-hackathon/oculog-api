from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class WeatherDataBase(BaseModel):
    location_name: str | None = None
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)

    temperature_c: float | None = None
    humidity_percent: int | None = Field(None, ge=0, le=100)
    pressure_hpa: float | None = None
    wind_speed_kmh: float | None = Field(None, ge=0)
    conditions: str | None = None

    air_quality_index: int | None = Field(None, ge=0)
    uv_index: float | None = Field(None, ge=0)
    pollen_count: int | None = Field(None, ge=0)


class WeatherDataCreate(WeatherDataBase):
    condition_log_id: UUID


class WeatherDataResponse(WeatherDataBase):
    id: UUID
    condition_log_id: UUID
    recorded_at: datetime

    class Config:
        from_attributes = True
