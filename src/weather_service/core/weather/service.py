import datetime
from datetime import datetime as dt

from weather_service.core.data_store.base import BaseDataStore
from weather_service.core.events.base import BaseEventStore, Event
from weather_service.core.exceptions import BaseServiceException
from weather_service.core.geo.base import GeoCodeLocationProvider
from weather_service.core.weather.providers.base import Location, WeatherProviderFactory


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
        self.data_store = data_store
        self.event_store = event_store

    def _format_file_name(
        self, city_name: str, country_code: str | None, state: str | None
    ) -> str:
        return f"{city_name}_{country_code}_{state}_{dt.now(datetime.UTC).strftime('%Y%m%d_%H%M%S')}.json"

    async def get_weather_by_city(
        self, city_name: str, country_code: str | None = None, state: str | None = None
    ):
        """Get weather data by city name using the provider."""

        city_name = city_name.lower().strip()
        country_code = country_code.lower().strip() if country_code else None
        state = state.lower().strip() if state else None

        locations = await self.geo_code_provider.resolve_locations(
            city_name, country_code, state
        )

        if len(locations) == 0:
            raise CityNotFoundException(city_name)
        elif len(locations) > 1:
            raise AmbiguousLocationException(city_name, country_code, state, locations)

        async with self.provider_factory.provider() as provider:
            location = locations[0]
            weather_info = await provider.get_current_weather(location)

            url = await self.data_store.upload_file(
                self._format_file_name(location.name, location.country, location.state),
                weather_info.to_json(indent=4).encode("utf-8"),
            )
            await self.event_store.store_event(
                Event(
                    timestamp=dt.now(datetime.UTC),
                    city=location.name,
                    country_code=location.country,
                    state=location.state,
                    url=url,
                )
            )

            return weather_info


class CityNotFoundException(BaseServiceException):
    def __init__(self, city_name: str):
        message = f"City '{city_name}' not found"
        super().__init__(message, 404)


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
