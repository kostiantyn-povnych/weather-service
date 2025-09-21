from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from weather_service.api.caching import cache_or_nop
from weather_service.core.weather.dependencies import get_weather_service
from weather_service.core.weather.service import WeatherService

router = APIRouter()


class CityModel(BaseModel):
    name: str
    country_code: str | None = None
    state: str | None = None


class CurrentWeatherModel(BaseModel):
    temperature: float
    feels_like: float
    humidity: int
    pressure: float
    description: str
    wind_speed: float
    wind_direction: int


class CityCurrentWeatherResponse(BaseModel):
    city: CityModel
    weather: CurrentWeatherModel

    class Config:
        from_attributes = True


@router.get("/weather", response_model=list[CityCurrentWeatherResponse])
@cache_or_nop()
async def get_weather(
    city: str,
    country_code: str | None = None,
    state: str = "",
    service: WeatherService = Depends(get_weather_service),
) -> list[CityCurrentWeatherResponse]:
    data = await service.get_weather_by_city(city, country_code, state)

    response: list[CityCurrentWeatherResponse] = list(
        map(
            lambda x: CityCurrentWeatherResponse(
                city=CityModel(
                    name=x[0].name,
                    country_code=x[0].country,
                    state=x[0].state,
                ),
                weather=CurrentWeatherModel(
                    temperature=x[1].temperature,
                    feels_like=x[1].feels_like or x[1].temperature,
                    humidity=x[1].humidity,
                    pressure=x[1].pressure,
                    description=x[1].description,
                    wind_speed=x[1].wind_speed,
                    wind_direction=x[1].wind_direction,
                ),
            ),
            data,
        )
    )

    return response


class WeatherForecastModel(BaseModel):
    date: str
    weather: CurrentWeatherModel


class CityWeatherForecastResponse(BaseModel):
    city: CityModel
    forecast: list[WeatherForecastModel]


@router.get("/weather-forecast", response_model=CityWeatherForecastResponse)
@cache_or_nop()
async def get_weather_forecast_by_city(
    city: str,
    country_code: str | None = None,
    state: str | None = None,
    days: int = 3,
    service: WeatherService = Depends(get_weather_service),
) -> CityWeatherForecastResponse:
    data = await service.get_weather_forecast_by_city(city, country_code, state, days)

    if not data:
        raise HTTPException(
            status_code=404, detail=f"No forecast data found for city: {city}"
        )

    # Take the first location's forecast data
    location, forecast_data = data[0]

    response = CityWeatherForecastResponse(
        city=CityModel(
            name=location.name,
            country_code=location.country,
            state=location.state,
        ),
        forecast=[
            WeatherForecastModel(
                date=forecast_item.date,
                weather=CurrentWeatherModel(
                    temperature=forecast_item.weather.temperature,
                    feels_like=forecast_item.weather.feels_like
                    or forecast_item.weather.temperature,
                    humidity=forecast_item.weather.humidity,
                    pressure=forecast_item.weather.pressure,
                    description=forecast_item.weather.description,
                    wind_speed=forecast_item.weather.wind_speed,
                    wind_direction=forecast_item.weather.wind_direction,
                ),
            )
            for forecast_item in forecast_data
        ],
    )

    return response
