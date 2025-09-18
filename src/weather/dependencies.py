from functools import lru_cache
from fastapi import Depends

from weather.providers.openweathermap import OpenWeatherMapProvider
from weather.service import WeatherService
from settings import settings


@lru_cache()
def get_weather_provider() -> OpenWeatherMapProvider:
    """Get weather provider instance."""
    return OpenWeatherMapProvider(api_key=settings.openweathermap_api_key)


def get_weather_service(
    provider: OpenWeatherMapProvider = Depends(get_weather_provider),
) -> WeatherService:
    """Get weather service instance with dependency injection."""
    return WeatherService(provider=provider)
