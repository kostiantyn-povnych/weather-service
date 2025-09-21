from common.exceptions import BaseServiceException
from data_store.base import BaseDataStore
from events.base import BaseEventStore
from geo.base import GeoCodeLocationProvider
from weather.providers.base import Location, WeatherProviderFactory


class WeatherService:
    def __init__(
        self,
        weather_provider_factory: WeatherProviderFactory,
        geo_code_provider: GeoCodeLocationProvider,
        event_store: BaseEventStore,
        data_store: BaseDataStore,
    ):
        self.provider_factory = weather_provider_factory
        self.geo_code_provider = geo_code_provider

    async def get_weather_by_city(
        self, city_name: str, country_code: str | None = None, state: str | None = None
    ):
        """Get weather data by city name using the provider."""

        locations = await self.geo_code_provider.resolve_locations(
            city_name, country_code, state
        )

        if len(locations) == 0:
            raise LocationNotFoundException(f"Location {city_name} not found")
        elif len(locations) > 1:
            raise AmbiguousLocationException(city_name, country_code, state, locations)

        async with self.provider_factory.provider() as provider:
            weather_info = await provider.get_current_weather(locations[0])
            return weather_info


class LocationNotFoundException(BaseServiceException):
    def __init__(self, message: str):
        # Not found returned by the Geocoding API indicates that the city was specified incorrectly.
        # Therefore, map a bad request status code.
        super().__init__(message, 400)


class AmbiguousLocationException(BaseServiceException):
    def __init__(
        self,
        city_name: str,
        country_code: str | None,
        state: str | None,
        locations: list[Location],
    ):
        message = f"Ambiguous location by city name {city_name}{f', country code {country_code}' if country_code else ''}"
        if country_code:
            message += f" and country code {country_code}."
        if state:
            message += f" and state {state}."
        message += f" Locations found: {locations}"
        super().__init__(message, 400)
