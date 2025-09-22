"""Pydantic models for the weather service API."""

from pydantic import BaseModel, ConfigDict, Field


class CityQueryParams(BaseModel):
    """Common query parameters for city-based weather endpoints."""

    city: str
    country_code: str | None = None
    state: str | None = None


class CityModel(BaseModel):
    """City information model."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    country_code: str | None = None
    state: str | None = None


class CurrentWeatherModel(BaseModel):
    """Current weather conditions model."""

    temperature: float
    feels_like: float
    humidity: int
    pressure: float
    description: str
    wind_speed: float
    wind_direction: int


class CityCurrentWeatherResponse(BaseModel):
    """Response model for current weather data."""

    model_config = ConfigDict(from_attributes=True)

    city: CityModel = Field(..., description="City information")
    weather: CurrentWeatherModel = Field(..., description="Current weather conditions")


class WeatherForecastModel(BaseModel):
    """Weather forecast data for a specific date/time."""

    date: str
    weather: CurrentWeatherModel


class CityWeatherForecastResponse(BaseModel):
    """Response model for weather forecast data."""

    model_config = ConfigDict(from_attributes=True)

    city: CityModel = Field(..., description="City information")
    forecast: list[WeatherForecastModel] = Field(
        ..., description="List of weather forecasts for the specified number of days"
    )
