from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openweathermap_api_key: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
