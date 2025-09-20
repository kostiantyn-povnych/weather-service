"""Test configuration and fixtures for integration tests."""

import asyncio
import sys
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import fastApiApp


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application."""
    app = fastApiApp()
    return TestClient(app)


@pytest.fixture
def mock_weather_data():
    """Mock weather data response."""
    return {
        "temperature": 22.5,
        "humidity": 65,
        "pressure": 1013.25,
        "description": "clear sky",
        "wind_speed": 3.2,
        "wind_direction": 180,
        "visibility": 10000,
        "feels_like": 24.1,
        "min_temp": 20.0,
        "max_temp": 25.0,
    }


@pytest.fixture
def mock_location_data():
    """Mock location data response."""
    return [
        {
            "name": "London",
            "local_names": {"en": "London"},
            "lat": 51.5074,
            "lon": -0.1278,
            "country": "GB",
            "state": "England",
        }
    ]


@pytest.fixture
def mock_openweather_weather_response():
    """Mock OpenWeatherMap weather API response."""
    return {
        "main": {
            "temp": 22.5,
            "humidity": 65,
            "pressure": 1013.25,
            "feels_like": 24.1,
            "temp_min": 20.0,
            "temp_max": 25.0,
        },
        "weather": [{"description": "clear sky"}],
        "wind": {"speed": 3.2, "deg": 180},
        "visibility": 10000,
    }


@pytest.fixture
def mock_openweather_geocoding_response():
    """Mock OpenWeatherMap geocoding API response."""
    return [
        {
            "name": "London",
            "local_names": {"en": "London"},
            "lat": 51.5074,
            "lon": -0.1278,
            "country": "GB",
            "state": "England",
        }
    ]
