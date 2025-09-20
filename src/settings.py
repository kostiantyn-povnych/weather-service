from enum import Enum

from pydantic_settings import BaseSettings


class EventStoreType(str, Enum):
    LOCAL = "local"
    AWS_DYNAMODB = "aws_dynamodb"


class DataStoreType(str, Enum):
    LOCAL = "local"
    AWS_S3 = "aws_s3"


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

    # Cache configuration
    cache_enabled: bool = True
    cache_expiration_minutes: int = 5
    cache_max_memory_mb: int = 256

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
