"""API documentation and examples for the weather service endpoints."""

# Router configuration
ROUTER_RESPONSES = {
    404: {"description": "Not found"},
    500: {"description": "Internal server error"},
}

# Weather endpoint documentation
WEATHER_SUMMARY = "Get current weather by city"
WEATHER_DESCRIPTION = """
Retrieve current weather conditions for a specified city.

This endpoint searches for cities matching the provided name and returns current weather data.
If multiple cities match the search criteria, all matching cities will be returned.

**Examples:**
- `/weather?city=London` - Get weather for London
- `/weather?city=London&country_code=GB` - Get weather for London, UK specifically
- `/weather?city=Springfield&state=Illinois` - Get weather for Springfield, Illinois
"""

WEATHER_RESPONSES = {
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
}

WEATHER_TAGS = ["Weather"]

# Weather forecast endpoint documentation
FORECAST_SUMMARY = "Get weather forecast by city"
FORECAST_DESCRIPTION = """
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
"""

FORECAST_RESPONSES = {
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
                "example": {"detail": "No forecast data found for city: InvalidCity"}
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
}

FORECAST_TAGS = ["Weather Forecast"]
