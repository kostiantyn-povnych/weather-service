from fastapi import APIRouter, Depends, HTTPException, Query

from weather_service.api.caching import cache_or_nop
from weather_service.api.dependencies import get_city_query_params
from weather_service.api.docs import (
    FORECAST_DESCRIPTION,
    FORECAST_RESPONSES,
    FORECAST_SUMMARY,
    FORECAST_TAGS,
    ROUTER_RESPONSES,
    WEATHER_DESCRIPTION,
    WEATHER_RESPONSES,
    WEATHER_SUMMARY,
    WEATHER_TAGS,
)
from weather_service.api.models import (
    CityCurrentWeatherResponse,
    CityModel,
    CityQueryParams,
    CityWeatherForecastResponse,
    CurrentWeatherModel,
    WeatherForecastModel,
)
from weather_service.core.weather.dependencies import (
    WeatherServiceDependency,
)
from weather_service.core.weather.service import WeatherService

router = APIRouter(responses=ROUTER_RESPONSES)


@router.get(
    "/weather",
    response_model=list[CityCurrentWeatherResponse],
    summary=WEATHER_SUMMARY,
    description=WEATHER_DESCRIPTION,
    responses=WEATHER_RESPONSES,
    tags=WEATHER_TAGS,
)
@cache_or_nop()
async def get_weather(
    params: CityQueryParams = Depends(get_city_query_params),
    service: WeatherService = WeatherServiceDependency,
) -> list[CityCurrentWeatherResponse]:
    data = await service.get_weather_by_city(
        params.city, params.country_code, params.state
    )

    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No weather data found for the given parameters. City: {params.city}, Country: {params.country_code or 'Unspecified'}, State: {params.state or 'Unspecified'}",
        )

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


@router.get(
    "/weather-forecast",
    response_model=list[CityWeatherForecastResponse],
    summary=FORECAST_SUMMARY,
    description=FORECAST_DESCRIPTION,
    responses=FORECAST_RESPONSES,
    tags=FORECAST_TAGS,
)
@cache_or_nop()
async def get_weather_forecast_by_city(
    params: CityQueryParams = Depends(get_city_query_params),
    days: int = Query(
        3, description="Number of days to forecast (1-5 days)", example=3, ge=1, le=5
    ),
    service: WeatherService = WeatherServiceDependency,
) -> list[CityWeatherForecastResponse]:
    data = await service.get_weather_forecast_by_city(
        params.city, params.country_code, params.state, days
    )

    if not data:
        raise HTTPException(
            status_code=404, detail=f"No forecast data found for city: {params.city}"
        )

    response: list[CityWeatherForecastResponse] = list(
        map(
            lambda x: CityWeatherForecastResponse(
                city=CityModel(
                    name=x[0].name,
                    country_code=x[0].country,
                    state=x[0].state,
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
                    for forecast_item in x[1]
                ],
            ),
            data,
        )
    )

    return response
