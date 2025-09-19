"""OpenWeatherMap weather provider implementation."""

import logging
import httpx
from typing import Dict, Any
from .base import WeatherProvider, WeatherData, Location, WeatherProviderFactory

LOGGER = logging.getLogger(__name__)


class OpenWeatherMapProvider(WeatherProvider):
    """OpenWeatherMap weather provider implementation."""

    WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self, api_key: str):
        """Initialize OpenWeatherMap provider."""
        self._client: httpx.AsyncClient | None = None
        self.api_key = api_key

    async def __aenter__(self) -> WeatherProvider:
        """Async context manager entry."""
        self._client = httpx.AsyncClient()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    def httpx_client(self) -> httpx.AsyncClient:
        """Get the underlying HTTP client."""
        if not self._client:
            raise RuntimeError(
                "HTTP client not initialized. Use the async context manager"
            )
        return self._client

    async def _make_request(
        self, endpoint: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make HTTP request to OpenWeatherMap API."""

        url = f"{self.WEATHER_BASE_URL}/{endpoint}"
        params["appid"] = self.api_key

        response = await self.httpx_client().get(url, params=params)

        if response.is_error:
            LOGGER.error(f"Error response from OpenWeatherMap API: {response.text}")

        response.raise_for_status()
        return response.json()

    async def get_current_weather(self, location: Location) -> WeatherData:
        """Get current weather data for a location."""
        data = await self._make_request(
            "weather",
            {
                "lat": location.latitude,
                "lon": location.longitude,
                "units": "metric",
            },
        )

        return WeatherData(
            temperature=data["main"]["temp"],
            humidity=data["main"]["humidity"],
            pressure=data["main"]["pressure"],
            description=data["weather"][0]["description"],
            wind_speed=data["wind"]["speed"],
            wind_direction=data["wind"].get("deg", 0),
            visibility=data.get("visibility", None),
            feels_like=data["main"].get("feels_like"),
            min_temp=data["main"].get("temp_min"),
            max_temp=data["main"].get("temp_max"),
        )

    # async def resolve_location(
    #     self, city: str, country_code: str | None = None, state: str | None = None
    # ) -> List[Location]:
    #     """Search for locations by name using OpenWeatherMap Geocoding API."""

    #     def format_query(
    #         city: str, country_code: str | None = None, state: str | None = None
    #     ) -> str:
    #         if state and country_code:
    #             return f"{city},{state},{country_code}"
    #         elif country_code:
    #             return f"{city},{country_code}"
    #         else:
    #             return city

    #     url = f"{self.GEOCODING_BASE_URL}/direct"
    #     params: Dict[str, str | int] = {
    #         "q": format_query(city, country_code, state),
    #         "limit": 5,
    #         "appid": self.api_key,
    #     }

    #     response = await self.httpx_client().get(url, params=params)
    #     response.raise_for_status()

    #     data = response.json()

    #     LOGGER.info(f"Response: {response.json()}")

    #     locations = []
    #     for item in data:
    #         locations.append(
    #             Location(
    #                 local_names=item["local_names"],
    #                 latitude=item["lat"],
    #                 longitude=item["lon"],
    #                 name=item.get("name"),
    #                 country=item.get("country"),
    #                 state=item.get("state"),
    #             )
    #         )

    #     return locations

    async def get_weather_by_city(
        self, city_name: str, country_code: str | None = None
    ) -> WeatherData:
        """Get current weather by city name."""

        query = city_name
        if country_code:
            query = f"{city_name},{country_code}"

        url = f"{self.WEATHER_BASE_URL}/weather"
        params = {"q": query, "appid": self.api_key, "units": "metric"}

        response = await self.httpx_client().get(url, params=params)
        response.raise_for_status()
        data = await response.json()

        return WeatherData(
            temperature=data["main"]["temp"],
            humidity=data["main"]["humidity"],
            pressure=data["main"]["pressure"],
            description=data["weather"][0]["description"],
            wind_speed=data["wind"]["speed"],
            wind_direction=data["wind"].get("deg", 0),
            visibility=data.get("visibility", None),
            feels_like=data["main"].get("feels_like"),
            min_temp=data["main"].get("temp_min"),
            max_temp=data["main"].get("temp_max"),
        )


class OpenWeatherMapProviderFactory(WeatherProviderFactory):
    """OpenWeatherMap provider factory implementation."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def provider(self) -> WeatherProvider:
        """Get weather provider instance."""
        return OpenWeatherMapProvider(api_key=self.api_key)
