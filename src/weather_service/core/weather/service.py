import asyncio
import datetime
from datetime import datetime as dt

from weather_service.core.data_store.base import BaseDataStore
from weather_service.core.events.base import BaseEventStore, Event
from weather_service.core.exceptions import BaseServiceException
from weather_service.core.geo.base import GeoCodeLocationProvider
from weather_service.core.weather.providers.base import (
    Location,
    WeatherData,
    WeatherForecastData,
    WeatherProviderFactory,
)


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

    # TODO: Move to storage layer?
    def _format_file_name(
        self, city_name: str, country_code: str | None, state: str | None
    ) -> str:
        return f"{city_name}_{country_code}_{state}_{dt.now(datetime.UTC).strftime('%Y%m%d_%H%M%S')}.json"

    async def get_weather_by_city(
        self, city_name: str, country_code: str | None = None, state: str | None = None
    ) -> list[tuple[Location, WeatherData]]:
        """Get weather data by city name using the provider."""

        city_name = city_name.lower().strip()
        country_code = country_code.lower().strip() if country_code else None
        state = state.lower().strip() if state else None

        locations = await self.geo_code_provider.resolve_locations(
            city_name, country_code, state
        )

        if len(locations) == 0:
            return []

        weather_infos_by_location = []
        for location in locations:
            weather_info = await self.provider_factory.provider().get_current_weather(
                location
            )
            weather_infos_by_location.append((location, weather_info))

        await asyncio.gather(
            *[
                self._store_weather_info(location, weather_info)
                for location, weather_info in weather_infos_by_location
            ]
        )

        return weather_infos_by_location

    async def get_weather_forecast_by_city(
        self,
        city_name: str,
        country_code: str | None = None,
        state: str | None = None,
        days: int = 3,
    ) -> list[tuple[Location, list[WeatherForecastData]]]:
        """Get weather forecast data by city name using the provider."""
        city_name = city_name.lower().strip()
        country_code = country_code.lower().strip() if country_code else None
        state = state.lower().strip() if state else None

        locations = await self.geo_code_provider.resolve_locations(
            city_name, country_code, state
        )

        if len(locations) == 0:
            return []

        weather_forecast_by_location = []

        for location in locations:
            weather_forecast = (
                await self.provider_factory.provider().get_weather_forecast(
                    location, days
                )
            )
            weather_forecast_by_location.append((location, weather_forecast))

        return weather_forecast_by_location

    async def _store_weather_info(
        self, location: Location, weather_info: WeatherData
    ) -> None:
        url = await self.data_store.put_object(
            self._format_file_name(location.name, location.country, location.state),
            weather_info.to_json(indent=4).encode("utf-8"),
        )
        await self.event_store.put_event(
            Event(
                timestamp=dt.now(datetime.UTC),
                city=location.name,
                country_code=location.country,
                state=location.state,
                url=url,
            )
        )


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
        message = f"Ambiguous city name {city_name}{f', country code {country_code}' if country_code else ''}"
        message += f". Candidates: {locations}"
        super().__init__(message, 400)
