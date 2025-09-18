"""OpenWeatherMap weather provider implementation."""

import httpx
from typing import Dict, Any, List
from .base import GeoCodeLocationProvider, WeatherProvider, WeatherData, Location


class OpenWeatherMapProvider(WeatherProvider, GeoCodeLocationProvider):
    """OpenWeatherMap weather provider implementation."""

    BASE_URL = "https://api.openweathermap.org/data/3.0"

    def __init__(self, api_key: str):
        """Initialize OpenWeatherMap provider."""
        self._client: httpx.AsyncClient | None = None
        self.api_key = api_key

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    async def _make_request(
        self, endpoint: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make HTTP request to OpenWeatherMap API."""
        self._validate_api_key()

        if not self._client:
            self._client = httpx.AsyncClient()

        url = f"{self.BASE_URL}/{endpoint}"
        params["appid"] = self.api_key
        params["units"] = "metric"  # Use metric units

        response = await self._client.get(url, params=params)
        response.raise_for_status()
        return await response.json()

    async def get_current_weather(self, location: Location) -> WeatherData:
        """Get current weather data for a location."""
        params = self._build_request_params(location)
        data = await self._make_request("weather", params)

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

    async def get_weather_forecast(
        self, location: Location, days: int = 5
    ) -> List[WeatherData]:
        """Get weather forecast for a location."""
        params = self._build_request_params(
            location, cnt=days * 8
        )  # 8 forecasts per day (3-hour intervals)
        data = await self._make_request("forecast", params)

        forecasts = []
        for item in data["list"]:
            forecasts.append(
                WeatherData(
                    temperature=item["main"]["temp"],
                    humidity=item["main"]["humidity"],
                    pressure=item["main"]["pressure"],
                    description=item["weather"][0]["description"],
                    wind_speed=item["wind"]["speed"],
                    wind_direction=item["wind"].get("deg", 0),
                    visibility=item.get("visibility", None),
                    feels_like=item["main"].get("feels_like"),
                    min_temp=item["main"].get("temp_min"),
                    max_temp=item["main"].get("temp_max"),
                )
            )

        return forecasts

    async def resolve_location(self, city: str) -> List[Location]:
        """Search for locations by name using OpenWeatherMap Geocoding API."""
        self._validate_api_key()

        if not self._client:
            self._client = httpx.AsyncClient()

        url = "http://api.openweathermap.org/geo/1.0/direct"
        params: Dict[str, str | int] = {"q": city, "limit": 5, "appid": self.api_key}

        response = await self._client.get(url, params=params)
        response.raise_for_status()
        data = await response.json()

        locations = []
        for item in data:
            locations.append(
                Location(
                    latitude=item["lat"],
                    longitude=item["lon"],
                    city=item.get("name"),
                    country=item.get("country"),
                )
            )

        return locations

    async def search_location(self, query: str) -> List[Location]:
        """Search for locations by name using OpenWeatherMap Geocoding API."""
        return await self.resolve_location(query)

    async def get_weather_by_city(
        self, city_name: str, country_code: str | None = None
    ) -> WeatherData:
        """Get current weather by city name."""
        self._validate_api_key()

        if not self._client:
            self._client = httpx.AsyncClient()

        query = city_name
        if country_code:
            query = f"{city_name},{country_code}"

        url = f"{self.BASE_URL}/weather"
        params = {"q": query, "appid": self.api_key, "units": "metric"}

        response = await self._client.get(url, params=params)
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
