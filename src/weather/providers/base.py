"""Base weather provider interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Self
from dataclasses import dataclass

from geo.base import Location


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


class WeatherProvider(ABC):
    """Abstract base class for weather providers."""

    @abstractmethod
    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        pass

    @abstractmethod
    async def get_current_weather(self, location: Location) -> WeatherData:
        """Get current weather data for a location."""
        pass

    # @abstractmethod
    # async def get_weather_forecast(
    #     self, location: Location, days: int = 5
    # ) -> list[WeatherData]:
    #     """Get weather forecast for a location."""
    #     pass


class WeatherProviderFactory(ABC):
    """Abstract base class for weather provider factories."""

    @abstractmethod
    def provider(self) -> WeatherProvider:
        """Get weather provider instance."""
        pass
