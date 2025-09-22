from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

from weather_service.api.caching import cache_or_nop
from weather_service.core.weather.dependencies import (
    WeatherServiceDependency,
)
from weather_service.core.weather.service import WeatherService

router = APIRouter(
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)


class CityQueryParams(BaseModel):
    """Common query parameters for city-based weather endpoints."""

    city: str
    country_code: str | None = None
    state: str | None = None


def get_city_query_params(
    city: str = Query(
        ...,
        description="Name of the city to get weather for",
        example="London",
        min_length=1,
        max_length=100,
    ),
    country_code: str = Query(
        None,
        description="ISO 3166-1 alpha-2 country code to narrow down the search",
        example="GB",
        pattern=r"^[A-Z]{2}$",
        nullable=True,
    ),
    state: str = Query(
        None,
        description="State or province name to narrow down the search",
        example="England",
        nullable=True,
        max_length=100,
    ),
) -> CityQueryParams:
    """Dependency to extract common city query parameters."""
    return CityQueryParams(
        city=city,
        country_code=country_code,
        state=state,
    )


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


@router.get(
    "/weather",
    response_model=list[CityCurrentWeatherResponse],
    summary="Get current weather by city",
    description="""
    Retrieve current weather conditions for a specified city.
    
    This endpoint searches for cities matching the provided name and returns current weather data.
    If multiple cities match the search criteria, all matching cities will be returned.
    
    **Examples:**
    - `/weather?city=London` - Get weather for London
    - `/weather?city=London&country_code=GB` - Get weather for London, UK specifically
    - `/weather?city=Springfield&state=Illinois` - Get weather for Springfield, Illinois
    """,
    responses={
        200: {
            "description": "Successfully retrieved weather data",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "city": {
                                "name": "London",
                                "country_code": "GB",
                                "state": "England",
                            },
                            "weather": {
                                "temperature": 15.5,
                                "feels_like": 13.2,
                                "humidity": 75,
                                "pressure": 1013.25,
                                "description": "light rain",
                                "wind_speed": 3.2,
                                "wind_direction": 180,
                            },
                        }
                    ]
                }
            },
        },
        404: {
            "description": "City not found",
            "content": {
                "application/json": {
                    "example": {"detail": "No weather data found for city: InvalidCity"}
                }
            },
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {"example": {"detail": "Internal server error"}}
            },
        },
    },
    tags=["Weather"],
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


@router.get(
    "/weather-forecast",
    response_model=list[CityWeatherForecastResponse],
    summary="Get weather forecast by city",
    description="""
    Retrieve weather forecast data for a specified city.
    
    This endpoint searches for cities matching the provided name and returns weather forecast data.
    If multiple cities match the search criteria, all matching cities will be returned.
    Forecasts are provided in 3-hour intervals, giving you detailed weather predictions.

    
    **Forecast Intervals:**
    - Each day contains up to 8 forecast points (every 3 hours)
    - Times: 00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00
    
    **Examples:**
    - `/weather-forecast?city=London&days=3` - Get 3-day forecast for London
    - `/weather-forecast?city=Paris&country_code=FR&days=5` - Get 5-day forecast for Paris, France
    """,
    responses={
        200: {
            "description": "Successfully retrieved weather forecast data",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "city": {
                                "name": "London",
                                "country_code": "GB",
                                "state": "England",
                            },
                            "forecast": [
                                {
                                    "date": "2024-01-15 12:00:00",
                                    "weather": {
                                        "temperature": 15.5,
                                        "feels_like": 13.2,
                                        "humidity": 75,
                                        "pressure": 1013.25,
                                        "description": "light rain",
                                        "wind_speed": 3.2,
                                        "wind_direction": 180,
                                    },
                                },
                                {
                                    "date": "2024-01-15 15:00:00",
                                    "weather": {
                                        "temperature": 16.8,
                                        "feels_like": 14.5,
                                        "humidity": 70,
                                        "pressure": 1012.8,
                                        "description": "partly cloudy",
                                        "wind_speed": 2.8,
                                        "wind_direction": 195,
                                    },
                                },
                            ],
                        }
                    ]
                }
            },
        },
        404: {
            "description": "City not found or no forecast data available",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No forecast data found for city: InvalidCity"
                    }
                }
            },
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["query", "days"],
                                "msg": "ensure this value is greater than or equal to 1",
                                "type": "value_error.number.not_ge",
                            }
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {"example": {"detail": "Internal server error"}}
            },
        },
    },
    tags=["Weather Forecast"],
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
