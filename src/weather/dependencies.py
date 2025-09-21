from functools import lru_cache
from pathlib import Path

from data_store.aws_s3 import AwsS3DataStore
from events.aws_dynamodb import AwsDynamoDBEventStore
from fastapi import Depends

from data_store.base import BaseDataStore
from data_store.local import LocalFileDataStore
from events.base import BaseEventStore
from events.local import LocalEventStore
from geo.base import GeoCodeLocationProvider
from geo.open_weather_geo_provider import OpenWeatherGeoProvider
from settings import DataStoreType, EventStoreType, settings
from weather.providers.base import WeatherProviderFactory
from weather.providers.openweathermap import (
    OpenWeatherMapProviderFactory,
)
from weather.service import WeatherService


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


@lru_cache()
def get_event_store() -> BaseEventStore:
    """Get event store instance based on configuration."""
    if settings.event_store_type == EventStoreType.LOCAL:
        return LocalEventStore(file_path=Path(settings.event_store_local_file_path))
    elif settings.event_store_type == EventStoreType.AWS_DYNAMODB:
        return AwsDynamoDBEventStore(
            table_name=settings.event_store_dynamodb_table_name
        )
    else:
        raise ValueError(f"Unsupported event store type: {settings.event_store_type}")


@lru_cache()
def get_data_store() -> BaseDataStore:
    """Get data store instance based on configuration."""
    if settings.data_store_type == DataStoreType.LOCAL:
        return LocalFileDataStore(directory=settings.data_store_local_directory)
    elif settings.data_store_type == DataStoreType.AWS_S3:
        return AwsS3DataStore(
            bucket_name=settings.data_store_s3_bucket_name,
            folder_name=settings.data_store_s3_folder_name,
        )
    else:
        raise ValueError(f"Unsupported data store type: {settings.data_store_type}")


def get_weather_service(
    provider: WeatherProviderFactory = Depends(get_weather_provider_factory),
    event_store: BaseEventStore = Depends(get_event_store),
    data_store: BaseDataStore = Depends(get_data_store),
) -> WeatherService:
    """Get weather service instance with dependency injection."""
    return WeatherService(
        weather_provider_factory=provider,
        geo_code_provider=get_geo_code_provider(),
        event_store=event_store,
        data_store=data_store,
    )
