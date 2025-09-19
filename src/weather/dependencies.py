from functools import lru_cache
from fastapi import Depends

from geo.base import GeoCodeLocationProvider
from geo.open_weather_geo_provider import OpenWeatherGeoProvider
from weather.providers.base import WeatherProviderFactory
from weather.providers.openweathermap import (
    OpenWeatherMapProviderFactory,
)
from weather.service import WeatherService
from settings import settings


@lru_cache()
def get_weather_provider_factory() -> WeatherProviderFactory:
    """Get weather provider instance."""
    if settings.openweathermap_api_key is None:
        raise ValueError("OpenWeatherMap API key is not set")

    return OpenWeatherMapProviderFactory(api_key=settings.openweathermap_api_key)


@lru_cache()
def get_geo_code_provider() -> GeoCodeLocationProvider:
    """Get geo code provider instance."""
    if settings.openweathermap_api_key is None:
        raise ValueError("OpenWeatherMap API key is not set")

    return OpenWeatherGeoProvider(api_key=settings.openweathermap_api_key)


def get_weather_service(
    provider: WeatherProviderFactory = Depends(get_weather_provider_factory),
) -> WeatherService:
    """Get weather service instance with dependency injection."""
    return WeatherService(
        weather_provider_factory=provider, geo_code_provider=get_geo_code_provider()
    )
