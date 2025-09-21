from enum import Enum, StrEnum

from pydantic import Field
from pydantic_settings import BaseSettings


class EventStoreType(str, Enum):
    LOCAL = "local"
    AWS_DYNAMODB = "aws_dynamodb"


class DataStoreType(str, Enum):
    LOCAL = "local"
    AWS_S3 = "aws_s3"


class CacheBackendType(StrEnum):
    REDIS = "redis"
    MEMORY = "memory"


class CacheSettings(BaseSettings):
    enabled: bool = Field(default=False, alias="CACHE_ENABLED")
    backend: CacheBackendType | None = Field(default=None, alias="CACHE_BACKEND")
    ttl_seconds: int = Field(default=300, alias="CACHE_TTL_SECONDS")
    prefix: str = Field(default="weather-cache", alias="CACHE_PREFIX")
    redis_url: str | None = Field(default=None, alias="REDIS_URL")


class RateLimitingSettings(BaseSettings):
    enabled: bool = Field(default=False, alias="RATE_LIMIT_ENABLED")
    redis_host: str = Field(default="localhost", alias="RATE_LIMIT_REDIS_HOST")
    redis_port: int = Field(default=6379, alias="RATE_LIMIT_REDIS_PORT")
    redis_db: int = Field(default=0, alias="RATE_LIMIT_REDIS_DB")
    limit: int = Field(default=100, alias="RATE_LIMIT_REQUESTS")
    window: int = Field(default=60, alias="RATE_LIMIT_WINDOW_SECONDS")


class Settings(BaseSettings):
    openweathermap_api_key: str | None = Field(
        default=None, alias="OPENWEATHERMAP_API_KEY", repr=False
    )

    # Event store configuration
    event_store_type: EventStoreType = EventStoreType.LOCAL
    event_store_local_file_path: str = "events.log"
    event_store_dynamodb_table_name: str = "weather-svc-events"

    # Data store configuration
    data_store_type: DataStoreType = DataStoreType.LOCAL
    data_store_local_directory: str = "data"
    data_store_s3_bucket_name: str = "weather-svc-data"
    data_store_s3_folder_name: str = "weather-svc-responses"

    cache: CacheSettings = CacheSettings()

    rate_limiting: RateLimitingSettings = RateLimitingSettings()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
