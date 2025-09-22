"""OpenWeatherMap weather provider implementation."""

import logging

from weather_service.core.retry import RetryConfig
from weather_service.core.third_party.openweather import OpenWeatherApiClient

from .base import (
    Location,
    WeatherData,
    WeatherForecastData,
    WeatherProvider,
    WeatherProviderFactory,
)

LOGGER = logging.getLogger(__name__)

PROVIDER_NAME = "OpenWeatherMap"


class OpenWeatherMapProvider(WeatherProvider):
    """OpenWeatherMap weather provider implementation."""

    def __init__(self, api_key: str, retry_config: RetryConfig | None = None):
        """Initialize OpenWeatherMap provider."""
        self.api_client = OpenWeatherApiClient(
            api_key=api_key, retry_config=retry_config
        )

    async def get_current_weather(self, location: Location) -> WeatherData:
        """Get current weather data for a location."""
        response = await self.api_client.get_current_weather_by_coords(
            location.latitude, location.longitude
        )
        return self._convert_to_weather_data(response)

    async def get_weather_forecast(
        self, location: Location, days: int = 3
    ) -> list[WeatherForecastData]:
        """Get weather forecast for a location."""
        response = await self.api_client.get_weather_forecast(
            location.latitude, location.longitude, days
        )
        return self._convert_to_forecast_data(response)

    def _convert_to_weather_data(self, response) -> WeatherData:
        """Convert OpenWeather API response to WeatherData."""
        return WeatherData(
            temperature=response.main.temp,
            humidity=response.main.humidity,
            pressure=response.main.pressure,
            description=response.weather[0].description,
            wind_speed=response.wind.speed,
            wind_direction=response.wind.deg or 0,
            visibility=response.visibility,
            feels_like=response.main.feels_like,
            min_temp=response.main.temp_min,
            max_temp=response.main.temp_max,
        )

    def _convert_to_forecast_data(self, response) -> list[WeatherForecastData]:
        """Convert OpenWeather forecast response to WeatherForecastData list."""
        forecast_list = []
        for item in response.list:
            weather_data = self._convert_to_weather_data(item)
            forecast_data = WeatherForecastData(
                date=item.dt_txt,
                weather=weather_data,
            )
            forecast_list.append(forecast_data)
        return forecast_list


class OpenWeatherMapProviderFactory(WeatherProviderFactory):
    """OpenWeatherMap provider factory implementation."""

    def __init__(self, api_key: str, retry_config: RetryConfig | None = None):
        self.api_key = api_key
        self.retry_config = retry_config

    def provider(self) -> WeatherProvider:
        """Get weather provider instance."""
        return OpenWeatherMapProvider(
            api_key=self.api_key, retry_config=self.retry_config
        )
