import logging
from functools import lru_cache
from pathlib import Path

from fastapi import Depends, Request

from weather_service.core.data_store.aws_s3 import AwsS3DataStore
from weather_service.core.data_store.base import BaseDataStore
from weather_service.core.data_store.local import LocalFileDataStore
from weather_service.core.events.aws_dynamodb import AwsDynamoDBEventStore
from weather_service.core.events.base import BaseEventStore
from weather_service.core.events.local import LocalEventStore
from weather_service.core.geo.base import GeoCodeLocationProvider
from weather_service.core.geo.open_weather_geo_provider import OpenWeatherGeoProvider
from weather_service.core.settings import DataStoreType, EventStoreType, settings
from weather_service.core.weather.providers.base import WeatherProviderFactory
from weather_service.core.weather.providers.openweathermap import (
    OpenWeatherMapProviderFactory,
)
from weather_service.core.weather.service import WeatherService

LOGGER = logging.getLogger(__name__)


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


def create_event_store() -> BaseEventStore:
    """Create event store instance based on configuration."""
    if settings.event_store.type == EventStoreType.LOCAL:
        LOGGER.info(
            f"Creating local event store with file path: {settings.event_store.local.file_path}"
        )
        return LocalEventStore(file_path=Path(settings.event_store.local.file_path))
    elif settings.event_store.type == EventStoreType.AWS_DYNAMODB:
        LOGGER.info(
            f"Creating AWS DynamoDB event store with table name: {settings.event_store.aws_dynamodb.table_name}"
        )
        return AwsDynamoDBEventStore(table=settings.event_store.aws_dynamodb.table_name)
    else:
        raise ValueError(f"Unsupported event store type: {settings.event_store.type}")


def create_data_store() -> BaseDataStore:
    """Create data store instance based on configuration."""
    if settings.data_store.type == DataStoreType.LOCAL:
        LOGGER.info(
            f"Initializing local file data store with directory: {settings.data_store.local.directory}"
        )
        return LocalFileDataStore(directory=settings.data_store.local.directory)
    elif settings.data_store.type == DataStoreType.AWS_S3:
        LOGGER.info(
            f"Initializing AWS S3 data store with bucket name: {settings.data_store.aws_s3.bucket_name}"
        )
        return AwsS3DataStore(
            bucket_name=settings.data_store.aws_s3.bucket_name,
            folder_name=settings.data_store.aws_s3.folder_name,
        )
    else:
        raise ValueError(f"Unsupported data store type: {settings.data_store.type}")


# @lru_cache()
# def get_event_store() -> BaseEventStore:
#     """Get event store instance based on configuration."""
#     if settings.event_store.type == EventStoreType.LOCAL:
#         return LocalEventStore(file_path=Path(settings.event_store.local.file_path))
#     elif settings.event_store.type == EventStoreType.AWS_DYNAMODB:
#         return AwsDynamoDBEventStore(
#             table_name=settings.event_store.aws_dynamodb.table_name
#         )
#     else:
#         raise ValueError(f"Unsupported event store type: {settings.event_store.type}")


# @lru_cache()
# def get_data_store() -> BaseDataStore:
#     """Get data store instance based on configuration."""
#     if settings.data_store.type == DataStoreType.LOCAL:
#         return LocalFileDataStore(directory=settings.data_store.local.directory)
#     elif settings.data_store.type == DataStoreType.AWS_S3:
#         return AwsS3DataStore(
#             bucket_name=settings.data_store.aws_s3.bucket_name,
#             folder_name=settings.data_store.aws_s3.folder_name,
#         )
#     else:
#         raise ValueError(f"Unsupported data store type: {settings.data_store.type}")


def get_weather_service(
    request: Request,
    provider: WeatherProviderFactory = Depends(get_weather_provider_factory),
) -> WeatherService:
    """Get weather service instance with dependency injection."""
    return WeatherService(
        weather_provider_factory=provider,
        geo_code_provider=get_geo_code_provider(),
        event_store=request.app.state.event_store,
        data_store=request.app.state.data_store,
    )
