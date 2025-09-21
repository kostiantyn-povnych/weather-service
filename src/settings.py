from enum import Enum

from pydantic import Field
from pydantic_settings import BaseSettings


class EventStoreType(str, Enum):
    LOCAL = "local"
    AWS_DYNAMODB = "aws_dynamodb"


class DataStoreType(str, Enum):
    LOCAL = "local"
    AWS_S3 = "aws_s3"


class CacheSettings(BaseSettings):
    enabled: bool = Field(default=False, alias="CACHE_ENABLED")
    backend: str = Field(default="memory", alias="CACHE_BACKEND")  # "redis" | "memory"
    ttl_seconds: int = Field(default=300, alias="CACHE_TTL_SECONDS")
    prefix: str = Field(default="weather-cache", alias="CACHE_PREFIX")
    redis_url: str | None = Field(default=None, alias="REDIS_URL")


class Settings(BaseSettings):
    openweathermap_api_key: str | None = None

    # Event store configuration
    event_store_type: EventStoreType = EventStoreType.LOCAL
    event_store_local_file_path: str = "events.log"
    event_store_dynamodb_table_name: str = "weather-svc-events"

    # Data store configuration
    data_store_type: DataStoreType = DataStoreType.LOCAL
    data_store_local_directory: str = "data"
    data_store_s3_bucket_name: str = "weather-svc-data"
    data_store_s3_folder_name: str = "weather-svc-responses"

    # Caching configuration
    cache: CacheSettings = CacheSettings()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
