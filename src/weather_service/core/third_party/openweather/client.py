"""Unified OpenWeather API client."""

import logging
from typing import Any, Dict, List, Optional

import httpx

from weather_service.core.exceptions import ThirdPartyProviderError
from weather_service.core.retry import RetryConfig, with_retry

from .models import (
    OpenWeatherCurrentWeatherResponse,
    OpenWeatherForecastResponse,
    OpenWeatherGeoLocation,
)

LOGGER = logging.getLogger(__name__)

PROVIDER_NAME = "OpenWeatherAPI"


class OpenWeatherApiClient:
    """Unified client for OpenWeather API endpoints."""

    def __init__(
        self,
        api_key: str,
        weather_base_url: str = "https://api.openweathermap.org/data/2.5",
        geo_base_url: str = "https://api.openweathermap.org/geo/1.0",
        retry_config: Optional[RetryConfig] = None,
    ):
        """Initialize OpenWeather API client."""
        self.api_key = api_key
        self.weather_base_url = weather_base_url
        self.geo_base_url = geo_base_url
        self.retry_config = retry_config or RetryConfig()

    @with_retry(provider_name=PROVIDER_NAME)
    async def _make_request(
        self, base_url: str, endpoint: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make HTTP request to OpenWeather API with retry logic."""
        url = f"{base_url}/{endpoint}"
        params["appid"] = self.api_key

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)

            # Handle specific HTTP errors
            if response.status_code == 401:
                raise ThirdPartyProviderError(
                    PROVIDER_NAME, "Invalid API key", status_code=401
                )
            elif response.status_code == 404:
                raise ThirdPartyProviderError(
                    PROVIDER_NAME, "Location not found", status_code=404
                )
            elif response.status_code == 429:
                raise ThirdPartyProviderError(
                    PROVIDER_NAME, "API rate limit exceeded", status_code=429
                )

            response.raise_for_status()
            return response.json()

    async def get_current_weather_by_coords(
        self, latitude: float, longitude: float, units: str = "metric"
    ) -> OpenWeatherCurrentWeatherResponse:
        """Get current weather by coordinates."""
        data = await self._make_request(
            self.weather_base_url,
            "weather",
            {
                "lat": latitude,
                "lon": longitude,
                "units": units,
            },
        )
        return OpenWeatherCurrentWeatherResponse.from_dict(data)

    async def get_weather_forecast(
        self, latitude: float, longitude: float, days: int = 3, units: str = "metric"
    ) -> OpenWeatherForecastResponse:
        """Get weather forecast by coordinates."""
        data = await self._make_request(
            self.weather_base_url,
            "forecast",
            {
                "lat": latitude,
                "lon": longitude,
                "units": units,
                "cnt": days * 8,
            },
        )
        return OpenWeatherForecastResponse.from_dict(data)

    async def get_geo_locations(
        self, city: str, country_code: Optional[str] = None, state: Optional[str] = None
    ) -> List[OpenWeatherGeoLocation]:
        """Get geocoding locations."""
        query = self._format_geo_query(city, country_code, state)

        data = await self._make_request(
            self.geo_base_url,
            "direct",
            {"q": query, "limit": 5},
        )

        LOGGER.debug(f"Geo response: {data}")
        return [OpenWeatherGeoLocation.from_dict(item) for item in data]

    def _format_geo_query(
        self, city: str, country_code: Optional[str] = None, state: Optional[str] = None
    ) -> str:
        """Format query string for geocoding API."""
        if state and country_code:
            return f"{city},{state},{country_code}"
        elif country_code:
            return f"{city},{country_code}"
        else:
            return city
