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


class LocalEventStoreSettings(BaseSettings):
    file_path: str = Field(default="events.log", alias="EVENT_STORE_LOCAL_FILE_PATH")


class AwsDynamoDBEventStoreSettings(BaseSettings):
    table_name: str = Field(
        default="weather-svc-events", alias="EVENT_STORE_AWS_DYNAMODB_TABLE_NAME"
    )


class EventStoreSettings(BaseSettings):
    type: EventStoreType = Field(default=EventStoreType.LOCAL, alias="EVENT_STORE_TYPE")
    local: LocalEventStoreSettings = LocalEventStoreSettings()
    aws_dynamodb: AwsDynamoDBEventStoreSettings = AwsDynamoDBEventStoreSettings()


class LocalFileDataStoreSettings(BaseSettings):
    directory: str = Field(default="data", alias="DATA_STORE_LOCAL_DIRECTORY")


class AwsS3DataStoreSettings(BaseSettings):
    bucket_name: str = Field(
        default="weather-svc-data", alias="DATA_STORE_S3_BUCKET_NAME"
    )
    folder_name: str = Field(default="weather", alias="DATA_STORE_S3_FOLDER_NAME")


class DataStoreSettings(BaseSettings):
    type: DataStoreType = Field(default=DataStoreType.LOCAL, alias="DATA_STORE_TYPE")
    local: LocalFileDataStoreSettings = LocalFileDataStoreSettings()
    aws_s3: AwsS3DataStoreSettings = AwsS3DataStoreSettings()


class Settings(BaseSettings):
    openweathermap_api_key: str | None = Field(
        default=None, alias="OPENWEATHERMAP_API_KEY", repr=False
    )

    event_store: EventStoreSettings = EventStoreSettings()
    data_store: DataStoreSettings = DataStoreSettings()
    cache: CacheSettings = CacheSettings()
    rate_limiting: RateLimitingSettings = RateLimitingSettings()

    rate_limiting: RateLimitingSettings = RateLimitingSettings()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
