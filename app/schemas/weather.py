from datetime import datetime

from pydantic import BaseModel, Field


class UnifiedWeatherResponse(BaseModel):
    """Unified weather format for all endpoints"""

    # Location
    location_name: str | None = None
    latitude: float | None = None
    longitude: float | None = None

    # Core weather
    temperature_c: float | None = None
    condition: str | None = None
    icon_code: str | None = None

    # Extended data
    humidity_percent: int | None = None
    pressure_hpa: float | None = None
    wind_speed_kmh: float | None = None

    # Health factors
    air_quality_index: int | None = None
    uv_index: float | None = None
    pollen_count: int | None = None

    # Timestamp
    recorded_at: datetime | None = None

    class Config:
        from_attributes = True


class LocationRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class WeatherInfo(BaseModel):
    temperature_c: float
    condition: str
    icon_code: str


class AirQualityInfo(BaseModel):
    aqi: int = Field(..., ge=1, le=5)
    category: str  # Good, Fair, Moderate, Poor, Very Poor


class LocationWeatherResponse(BaseModel):
    city: str
    country: str
    weather: WeatherInfo
    air_quality: AirQualityInfo
