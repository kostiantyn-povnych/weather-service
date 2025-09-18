"""OpenWeatherMap weather provider implementation."""

import aiohttp
from typing import Dict, Any, List
from .base import WeatherProvider, WeatherData, Location


class OpenWeatherMapProvider(WeatherProvider):
    """OpenWeatherMap weather provider implementation."""

    BASE_URL = "https://api.openweathermap.org/data/3.0"

    def __init__(self, api_key: str):
        """Initialize OpenWeatherMap provider."""
        super().__init__(api_key)
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def _make_request(
        self, endpoint: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make HTTP request to OpenWeatherMap API."""
        self._validate_api_key()

        if not self.session:
            self.session = aiohttp.ClientSession()

        url = f"{self.BASE_URL}/{endpoint}"
        params["appid"] = self.api_key
        params["units"] = "metric"  # Use metric units

        async with self.session.get(url, params=params) as response:
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

    async def search_location(self, query: str) -> List[Location]:
        """Search for locations by name using OpenWeatherMap Geocoding API."""
        self._validate_api_key()

        if not self.session:
            self.session = aiohttp.ClientSession()

        url = "http://api.openweathermap.org/geo/1.0/direct"
        params = {"q": query, "limit": 5, "appid": self.api_key}

        async with self.session.get(url, params=params) as response:
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

    async def get_weather_by_city(
        self, city_name: str, country_code: str | None = None
    ) -> WeatherData:
        """Get current weather by city name."""
        self._validate_api_key()

        if not self.session:
            self.session = aiohttp.ClientSession()

        query = city_name
        if country_code:
            query = f"{city_name},{country_code}"

        url = f"{self.BASE_URL}/weather"
        params = {"q": query, "appid": self.api_key, "units": "metric"}

        async with self.session.get(url, params=params) as response:
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
