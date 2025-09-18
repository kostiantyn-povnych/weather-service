"""Base weather provider interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class WeatherData:
    """Weather data model."""

    temperature: float
    humidity: int
    pressure: float
    description: str
    wind_speed: float
    wind_direction: int
    visibility: Optional[int] = None
    uv_index: Optional[float] = None
    feels_like: Optional[float] = None
    min_temp: Optional[float] = None
    max_temp: Optional[float] = None


@dataclass
class Location:
    """Location data model."""

    latitude: float
    longitude: float
    city: Optional[str] = None
    country: Optional[str] = None


class WeatherProvider(ABC):
    """Abstract base class for weather providers."""

    def __init__(self, api_key: str):
        """Initialize the weather provider with API key."""
        self.api_key = api_key

    @abstractmethod
    async def get_current_weather(self, location: Location) -> WeatherData:
        """Get current weather data for a location."""
        pass

    @abstractmethod
    async def get_weather_forecast(
        self, location: Location, days: int = 5
    ) -> list[WeatherData]:
        """Get weather forecast for a location."""
        pass

    @abstractmethod
    async def search_location(self, query: str) -> list[Location]:
        """Search for locations by name."""
        pass

    def _validate_api_key(self) -> None:
        """Validate that API key is provided."""
        if not self.api_key:
            raise ValueError("API key is required")

    def _build_request_params(self, location: Location, **kwargs) -> Dict[str, Any]:
        """Build common request parameters."""
        return {"lat": location.latitude, "lon": location.longitude, **kwargs}
