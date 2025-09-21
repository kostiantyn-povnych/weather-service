from fastapi import APIRouter, Depends
from pydantic import BaseModel

from weather_service.api.caching import cache_or_nop
from weather_service.core.weather.dependencies import get_weather_service
from weather_service.core.weather.service import WeatherService

router = APIRouter()


class WeatherResponse(BaseModel):
    temperature: float
    humidity: int
    pressure: float
    description: str
    wind_speed: float
    wind_direction: int
    visibility: int | None = None
    uv_index: float | None = None
    feels_like: float | None = None
    min_temp: float | None = None
    max_temp: float | None = None

    class Config:
        from_attributes = True


@router.get("/weather", response_model=WeatherResponse)
@cache_or_nop()
async def get_weather(
    city: str,
    country_code: str | None = None,
    state: str = "",
    service: WeatherService = Depends(get_weather_service),
) -> WeatherResponse:
    weather_data = await service.get_weather_by_city(city, country_code, state)
    return WeatherResponse.model_validate(weather_data)
