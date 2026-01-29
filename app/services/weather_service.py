import asyncio
import time
from typing import Optional

import httpx

from app.config import settings
from app.schemas.weather import (
    AirQualityInfo,
    LocationWeatherResponse,
    WeatherInfo,
)


class WeatherService:
    """Service for fetching weather and air quality data from OpenWeatherMap API."""

    BASE_URL = "https://api.openweathermap.org"
    CACHE_TTL_SECONDS = settings.weather_cache_ttl_seconds

    # Simple in-memory cache with timestamps
    _cache: dict[str, tuple[LocationWeatherResponse, float]] = {}

    # AQI category mapping
    AQI_CATEGORIES = {
        1: "Good",
        2: "Fair",
        3: "Moderate",
        4: "Poor",
        5: "Very Poor",
    }

    @classmethod
    def _get_cache_key(cls, latitude: float, longitude: float) -> str:
        """Generate cache key from coordinates (rounded to 2 decimal places)."""
        return f"{round(latitude, 2)},{round(longitude, 2)}"

    @classmethod
    def _get_from_cache(cls, latitude: float, longitude: float) -> Optional[LocationWeatherResponse]:
        """Get cached response if still valid."""
        cache_key = cls._get_cache_key(latitude, longitude)
        if cache_key in cls._cache:
            response, timestamp = cls._cache[cache_key]
            if time.time() - timestamp < cls.CACHE_TTL_SECONDS:
                return response
            else:
                # Remove expired cache entry
                del cls._cache[cache_key]
        return None

    @classmethod
    def _set_cache(cls, latitude: float, longitude: float, response: LocationWeatherResponse) -> None:
        """Store response in cache with current timestamp."""
        cache_key = cls._get_cache_key(latitude, longitude)
        cls._cache[cache_key] = (response, time.time())

    @classmethod
    async def get_location_weather(cls, latitude: float, longitude: float) -> LocationWeatherResponse:
        """
        Fetch weather, air quality, and location data for given coordinates.

        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)

        Returns:
            LocationWeatherResponse with weather, air quality, and location info

        Raises:
            ValueError: If API key is not configured
            httpx.HTTPError: If API requests fail
        """
        # Check cache first
        cached = cls._get_from_cache(latitude, longitude)
        if cached:
            return cached

        # Check API key
        if not settings.openweathermap_api_key:
            raise ValueError("OpenWeatherMap API key not configured")

        api_key = settings.openweathermap_api_key

        # Make parallel requests for weather, air quality, and reverse geocoding
        async with httpx.AsyncClient(timeout=10.0) as client:
            weather_task = client.get(
                f"{cls.BASE_URL}/data/2.5/weather",
                params={
                    "lat": latitude,
                    "lon": longitude,
                    "appid": api_key,
                    "units": "metric",
                },
            )
            air_quality_task = client.get(
                f"{cls.BASE_URL}/data/2.5/air_pollution",
                params={
                    "lat": latitude,
                    "lon": longitude,
                    "appid": api_key,
                },
            )
            geocoding_task = client.get(
                f"{cls.BASE_URL}/geo/1.0/reverse",
                params={
                    "lat": latitude,
                    "lon": longitude,
                    "appid": api_key,
                    "limit": 1,
                },
            )

            # Execute all requests in parallel
            weather_response, air_quality_response, geocoding_response = await asyncio.gather(
                weather_task,
                air_quality_task,
                geocoding_task,
            )

        # Raise for status on all responses
        weather_response.raise_for_status()
        air_quality_response.raise_for_status()
        geocoding_response.raise_for_status()

        # Parse responses
        weather_data = weather_response.json()
        air_quality_data = air_quality_response.json()
        geocoding_data = geocoding_response.json()

        # Extract city and country
        city = "Unknown"
        country = "Unknown"
        if geocoding_data and len(geocoding_data) > 0:
            location = geocoding_data[0]
            city = location.get("name", "Unknown")
            country = location.get("country", "Unknown")

        # Extract weather info
        weather_info = WeatherInfo(
            temperature_c=weather_data["main"]["temp"],
            condition=weather_data["weather"][0]["main"],
            icon_code=weather_data["weather"][0]["icon"],
        )

        # Extract air quality info
        aqi = air_quality_data["list"][0]["main"]["aqi"]
        air_quality_info = AirQualityInfo(
            aqi=aqi,
            category=cls.AQI_CATEGORIES[aqi],
        )

        # Build response
        response = LocationWeatherResponse(
            city=city,
            country=country,
            weather=weather_info,
            air_quality=air_quality_info,
        )

        # Cache the response
        cls._set_cache(latitude, longitude, response)

        return response
