from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openweathermap_api_key: str

    class Config:
        env_file = ".env"


settings = Settings(openweathermap_api_key="")
