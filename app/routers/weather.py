from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_current_user
from app.exceptions import AppException, ErrorType
from app.models.user import User
from app.schemas.weather import LocationWeatherResponse, UnifiedWeatherResponse
from app.services.weather_service import WeatherService

router = APIRouter(prefix="/weather", tags=["weather"])


def location_weather_to_unified(
    response: LocationWeatherResponse,
    latitude: float,
    longitude: float,
) -> UnifiedWeatherResponse:
    """Convert LocationWeatherResponse to UnifiedWeatherResponse format."""
    return UnifiedWeatherResponse(
        location_name=f"{response.city}, {response.country}",
        latitude=latitude,
        longitude=longitude,
        temperature_c=response.weather.temperature_c,
        condition=response.weather.condition,
        icon_code=response.weather.icon_code,
        humidity_percent=None,  # Not available from current API response
        pressure_hpa=None,
        wind_speed_kmh=None,
        air_quality_index=response.air_quality.aqi,
        uv_index=None,
        pollen_count=None,
        recorded_at=datetime.now(timezone.utc),
    )


@router.get("", response_model=UnifiedWeatherResponse)
async def get_weather(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude coordinate"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude coordinate"),
    current_user: User = Depends(get_current_user),
):
    """
    Get current weather and air quality for a location.

    Returns:
        Unified weather information including temperature, condition, and air quality

    Raises:
        HTTPException 503: If API key is not configured
        HTTPException 502: If upstream API request fails
    """
    try:
        location_weather = await WeatherService.get_location_weather(
            latitude=latitude,
            longitude=longitude,
        )
        return location_weather_to_unified(location_weather, latitude, longitude)
    except ValueError as e:
        # API key not configured
        raise AppException(
            status_code=503,
            error_type=ErrorType.SERVICE_UNAVAILABLE,
            message=f"Weather service unavailable: {str(e)}",
        )
    except Exception as e:
        # Upstream API error
        raise AppException(
            status_code=502,
            error_type=ErrorType.BAD_GATEWAY,
            message=f"Failed to fetch weather data: {str(e)}",
        )
