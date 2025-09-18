from fastapi import APIRouter
from pydantic import BaseModel

from weather.providers.base import WeatherData
from weather.service import WeatherService

router = APIRouter()


class WeatherResponse(BaseModel):
    temperature: float
    humidity: int
    pressure: float
    description: str
    wind_speed: float
    wind_direction: int

    class Config:
        from_attributes = True


@router.get("/weather")
async def get_weather(service: WeatherService, city: str) -> WeatherResponse:
    return await service.get_weather_by_city(city)
