from datetime import date, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.weather import UnifiedWeatherResponse


class SortField(str, Enum):
    date = "date"
    rating = "rating"
    city = "city"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

MAX_TEXT_LENGTH = 500
MAX_CITY_LENGTH = 50


class ConditionLogBase(BaseModel):
    log_date: date
    city: str = Field(..., min_length=1, max_length=MAX_CITY_LENGTH)

    # Symptoms - REQUIRED (0-10)
    overall_rating: int = Field(..., ge=0, le=10)
    burning: int = Field(..., ge=0, le=10)
    redness: int = Field(..., ge=0, le=10)
    itching: int = Field(..., ge=0, le=10)
    tearing: int = Field(..., ge=0, le=10)
    swelling: int = Field(..., ge=0, le=10)
    dryness: int = Field(..., ge=0, le=10)

    # Lifestyle - REQUIRED
    screen_time_hours: float = Field(..., ge=0, le=24)
    sleep_hours: float = Field(..., ge=0, le=24)
    sleep_quality: int = Field(..., ge=0, le=10)
    stress_level: int = Field(..., ge=0, le=10)
    outdoor_hours: float = Field(..., ge=0, le=24)

    # Lifestyle - OPTIONAL (Extra section)
    water_intake_liters: float | None = Field(None, ge=0)
    caffeine_cups: int | None = Field(None, ge=0)
    alcohol_units: int | None = Field(None, ge=0)

    # Treatments - defaults to false
    used_artificial_tears: bool = False
    used_warm_compress: bool = False
    used_lid_scrub: bool = False
    used_prescription_drops: bool = False
    used_omega3: bool = False
    used_humidifier: bool = False

    # Environment - defaults to false
    wore_contacts: bool = False
    ac_exposure: bool = False
    heating_exposure: bool = False

    # Notes - OPTIONAL with max_length
    comments: str | None = Field(None, max_length=MAX_TEXT_LENGTH)
    treatments_notes: str | None = Field(None, max_length=MAX_TEXT_LENGTH)


class ConditionLogCreate(ConditionLogBase):
    user_id: UUID | None = None  # Optional - server sets from authenticated user


class ConditionLogUpdate(BaseModel):
    """All fields optional for partial updates"""

    log_date: date | None = None
    city: str | None = Field(None, min_length=1, max_length=MAX_CITY_LENGTH)

    # Symptoms (0-10)
    overall_rating: int | None = Field(None, ge=0, le=10)
    burning: int | None = Field(None, ge=0, le=10)
    redness: int | None = Field(None, ge=0, le=10)
    itching: int | None = Field(None, ge=0, le=10)
    tearing: int | None = Field(None, ge=0, le=10)
    swelling: int | None = Field(None, ge=0, le=10)
    dryness: int | None = Field(None, ge=0, le=10)

    # Lifestyle
    screen_time_hours: float | None = Field(None, ge=0, le=24)
    sleep_hours: float | None = Field(None, ge=0, le=24)
    sleep_quality: int | None = Field(None, ge=0, le=10)
    stress_level: int | None = Field(None, ge=0, le=10)
    outdoor_hours: float | None = Field(None, ge=0, le=24)
    water_intake_liters: float | None = Field(None, ge=0)
    caffeine_cups: int | None = Field(None, ge=0)
    alcohol_units: int | None = Field(None, ge=0)

    # Treatments
    used_artificial_tears: bool | None = None
    used_warm_compress: bool | None = None
    used_lid_scrub: bool | None = None
    used_prescription_drops: bool | None = None
    used_omega3: bool | None = None
    used_humidifier: bool | None = None

    # Environment
    wore_contacts: bool | None = None
    ac_exposure: bool | None = None
    heating_exposure: bool | None = None

    # Notes - with max_length
    comments: str | None = Field(None, max_length=MAX_TEXT_LENGTH)
    treatments_notes: str | None = Field(None, max_length=MAX_TEXT_LENGTH)


class ConditionLogResponse(BaseModel):
    """Response schema - allows nullable fields that DB may have"""
    id: UUID
    user_id: UUID
    log_date: date
    city: str | None = None

    # Symptoms (0-10) - nullable in response
    overall_rating: int | None = None
    burning: int | None = None
    redness: int | None = None
    itching: int | None = None
    tearing: int | None = None
    swelling: int | None = None
    dryness: int | None = None

    # Lifestyle - nullable in response
    screen_time_hours: float | None = None
    sleep_hours: float | None = None
    sleep_quality: int | None = None
    stress_level: int | None = None
    outdoor_hours: float | None = None
    water_intake_liters: float | None = None
    caffeine_cups: int | None = None
    alcohol_units: int | None = None

    # Treatments
    used_artificial_tears: bool | None = None
    used_warm_compress: bool | None = None
    used_lid_scrub: bool | None = None
    used_prescription_drops: bool | None = None
    used_omega3: bool | None = None
    used_humidifier: bool | None = None

    # Environment
    wore_contacts: bool | None = None
    ac_exposure: bool | None = None
    heating_exposure: bool | None = None

    # Notes
    comments: str | None = None
    treatments_notes: str | None = None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConditionLogDetailResponse(ConditionLogResponse):
    """Response with weather data included"""

    weather: UnifiedWeatherResponse | None = None


class PaginatedLogsResponse(BaseModel):
    """Paginated response for condition logs"""

    items: list[ConditionLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
