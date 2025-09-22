"""OpenWeather geocoding provider implementation."""

import logging

from weather_service.core.geo.base import GeoCodeLocationProvider, Location
from weather_service.core.retry import RetryConfig
from weather_service.third_party.openweather import OpenWeatherApiClient

PROVIDER_NAME = "OpenWeatherGeo"

LOGGER = logging.getLogger(__name__)


class OpenWeatherGeoProvider(GeoCodeLocationProvider):
    """OpenWeather geo provider implementation."""

    def __init__(self, api_key: str, retry_config: RetryConfig | None = None):
        self.api_client = OpenWeatherApiClient(
            api_key=api_key, retry_config=retry_config
        )

    async def resolve_locations(
        self, city: str, country_code: str | None = None, state: str | None = None
    ) -> list[Location]:
        """Resolve a location from a city name and country code."""
        geo_locations = await self.api_client.get_geo_locations(
            city, country_code, state
        )

        # Convert OpenWeatherGeoLocation to Location
        locations = []
        for geo_location in geo_locations:
            location = Location(
                name=geo_location.name,
                local_names=geo_location.local_names or {},
                country=geo_location.country,
                state=geo_location.state,
                latitude=geo_location.lat,
                longitude=geo_location.lon,
            )
            locations.append(location)

        # OpenWeatherMap API returns tends to return more than one location even though the city name doesn't exactly match.
        # Therefore, first we need to filter out the locations that don't exactly match the city name.
        locations = [
            location
            for location in locations
            if location.name.casefold() == city.casefold()
        ]

        return locations
