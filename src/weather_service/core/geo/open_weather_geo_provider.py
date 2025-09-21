import json
import logging

import httpx

from weather_service.core.geo.base import GeoCodeLocationProvider, Location

DEFAULT_BASE_URL = "https://api.openweathermap.org/geo/1.0"

LOGGER = logging.getLogger(__name__)


class OpenWeatherGeoClient:
    """OpenWeather geo client implementation."""

    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url

    def _format_query(
        self, city: str, country_code: str | None = None, state: str | None = None
    ) -> str:
        if state and country_code:
            return f"{city},{state},{country_code}"
        elif country_code:
            return f"{city},{country_code}"
        else:
            return city

    async def resolve_locations(
        self, city: str, country_code: str | None = None, state: str | None = None
    ) -> list[Location]:
        """Resolve a location from a city name, country code and, optionally, state."""
        async with httpx.AsyncClient() as client:

            response = await client.get(
                f"{self.base_url}/direct",
                params={
                    "q": self._format_query(city, country_code, state),
                    "limit": 5,
                    "appid": self.api_key,
                },
            )
            response.raise_for_status()
            data = response.json()
            LOGGER.debug(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")

            return [
                Location(
                    name=location["name"],
                    local_names=location.get("local_names", {}),
                    country=location["country"],
                    state=location.get("state"),
                    latitude=location["lat"],
                    longitude=location["lon"],
                )
                for location in data
            ]


class OpenWeatherGeoProvider(GeoCodeLocationProvider):
    """OpenWeather geo provider implementation."""

    def __init__(self, api_key: str):
        self.api_client = OpenWeatherGeoClient(api_key)

    async def resolve_locations(
        self, city: str, country_code: str | None = None, state: str | None = None
    ) -> list[Location]:
        """Resolve a location from a city name and country code."""
        locations = await self.api_client.resolve_locations(city, country_code, state)

        # OpenWeatherMap API returns tends to return more than one location even though the city name doesn't exactly match.
        # Therefore, first we need to filter out the locations that don't exactly match the city name.
        locations = [
            location
            for location in locations
            if location.name.casefold() == city.casefold()
        ]

        return locations
