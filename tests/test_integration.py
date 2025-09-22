"""End-to-end integration test for the weather service.

This test performs actual API calls to OpenWeatherMap to verify the complete
weather service functionality with minimal setup.
"""

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from weather_service.api.app import fastApiApp


class TestWeatherServiceIntegration:
    """End-to-end integration tests for the weather service."""

    @pytest.fixture(scope="class")
    def client(self) -> TestClient:
        """Create a test client for the FastAPI application."""
        app = fastApiApp()
        return TestClient(app)

    @pytest.fixture(scope="class")
    def api_key(self) -> str:
        """Get OpenWeatherMap API key from environment."""
        api_key = os.getenv("OPENWEATHERMAP_API_KEY")
        if not api_key or api_key.strip() == "":
            pytest.skip("OPENWEATHERMAP_API_KEY environment variable not set or empty")
        return api_key.strip()

    def test_weather_service_end_to_end(self, client: TestClient, api_key: str):
        """Test complete weather service functionality with real API calls.

        This test:
        1. Sets up the service with minimal configuration
        2. Makes actual API calls to OpenWeatherMap
        3. Verifies the complete request/response cycle
        4. Validates data structure and content
        """
        # Set environment variables for minimal setup
        os.environ["OPENWEATHERMAP_API_KEY"] = api_key
        os.environ["CACHE_ENABLED"] = "false"  # Disable caching for consistent testing
        os.environ["RATE_LIMIT_ENABLED"] = "false"  # Disable rate limiting
        os.environ["DATA_STORE_TYPE"] = "local"  # Use local storage
        os.environ["EVENT_STORE_TYPE"] = "local"  # Use local event logging

        # Verify API key is valid by testing with a simple request first
        print(
            f"Testing with API key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '****'}"
        )

        # Test weather retrieval for London, UK
        response = client.get(
            "/api/v1/weather", params={"city": "London", "country_code": "GB"}
        )

        # Verify successful response
        if response.status_code == 401:
            pytest.fail(
                "API key is invalid or expired. Please check OPENWEATHERMAP_API_KEY."
            )
        elif response.status_code == 403:
            pytest.fail("API key access forbidden. Please check API key permissions.")
        elif response.status_code != 200:
            pytest.fail(
                f"Unexpected response: {response.status_code} - {response.text}"
            )

        assert response.status_code == 200

        # Parse and validate response data
        data = response.json()

        # Verify response is a list
        assert isinstance(data, list), "Response should be a list"
        assert len(data) > 0, "Response should contain at least one result"

        # Get the first result (should be London, UK)
        weather_result = data[0]

        # Verify response structure
        assert "city" in weather_result, "Missing city field"
        assert "weather" in weather_result, "Missing weather field"

        city_info = weather_result["city"]
        weather_data = weather_result["weather"]

        # Verify city information
        assert (
            city_info["name"] == "London"
        ), f"Expected London, got {city_info['name']}"
        assert (
            city_info["country_code"] == "GB"
        ), f"Expected GB, got {city_info['country_code']}"

        # Verify required weather fields are present
        required_fields = [
            "temperature",
            "humidity",
            "pressure",
            "description",
            "wind_speed",
            "wind_direction",
            "feels_like",
        ]

        for field in required_fields:
            assert field in weather_data, f"Missing required field: {field}"

        # Validate data types and reasonable ranges
        assert isinstance(
            weather_data["temperature"], (int, float)
        ), "Temperature should be numeric"
        assert isinstance(
            weather_data["humidity"], (int, float)
        ), "Humidity should be numeric"
        assert isinstance(
            weather_data["pressure"], (int, float)
        ), "Pressure should be numeric"
        assert isinstance(
            weather_data["description"], str
        ), "Description should be string"
        assert isinstance(
            weather_data["wind_speed"], (int, float)
        ), "Wind speed should be numeric"
        assert isinstance(
            weather_data["wind_direction"], (int, float)
        ), "Wind direction should be numeric"
        assert isinstance(
            weather_data["feels_like"], (int, float)
        ), "Feels like should be numeric"

        # Validate reasonable ranges for weather data
        assert (
            -50 <= weather_data["temperature"] <= 60
        ), f"Temperature {weather_data['temperature']} seems unreasonable"
        assert (
            0 <= weather_data["humidity"] <= 100
        ), f"Humidity {weather_data['humidity']} should be 0-100%"
        assert (
            800 <= weather_data["pressure"] <= 1200
        ), f"Pressure {weather_data['pressure']} seems unreasonable"
        assert weather_data["wind_speed"] >= 0, "Wind speed should be non-negative"
        assert (
            0 <= weather_data["wind_direction"] <= 360
        ), "Wind direction should be 0-360 degrees"

        # Verify description is not empty
        assert (
            len(weather_data["description"]) > 0
        ), "Weather description should not be empty"

        print("✅ Successfully retrieved weather for London, UK:")
        print(f"   Temperature: {weather_data['temperature']}°C")
        print(f"   Description: {weather_data['description']}")
        print(f"   Humidity: {weather_data['humidity']}%")
        print(f"   Pressure: {weather_data['pressure']} hPa")

    def test_weather_service_city_only(self, client: TestClient, api_key: str):
        """Test weather service with city name only (no country code)."""
        os.environ["OPENWEATHERMAP_API_KEY"] = api_key
        os.environ["CACHE_ENABLED"] = "false"
        os.environ["RATE_LIMIT_ENABLED"] = "false"
        os.environ["DATA_STORE_TYPE"] = "local"
        os.environ["EVENT_STORE_TYPE"] = "local"

        # Test with city name only
        response = client.get("/api/v1/weather", params={"city": "Paris"})

        assert (
            response.status_code == 200
        ), f"Expected 200, got {response.status_code}: {response.text}"

        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        assert len(data) > 0, "Response should contain at least one result"

        # Get the first result
        weather_result = data[0]
        assert "city" in weather_result
        assert "weather" in weather_result

        weather_data = weather_result["weather"]
        assert "temperature" in weather_data
        assert "description" in weather_data
        assert isinstance(weather_data["temperature"], (int, float))
        assert isinstance(weather_data["description"], str)

        print("✅ Successfully retrieved weather for Paris:")
        print(f"   Temperature: {weather_data['temperature']}°C")
        print(f"   Description: {weather_data['description']}")

    def test_weather_service_error_handling(self, client: TestClient, api_key: str):
        """Test error handling for invalid requests."""
        os.environ["OPENWEATHERMAP_API_KEY"] = api_key
        os.environ["CACHE_ENABLED"] = "false"
        os.environ["RATE_LIMIT_ENABLED"] = "false"
        os.environ["DATA_STORE_TYPE"] = "local"
        os.environ["EVENT_STORE_TYPE"] = "local"

        # Test missing city parameter
        response = client.get("/api/v1/weather")
        assert (
            response.status_code == 422
        ), "Should return validation error for missing city"

        # Test non-existent city
        response = client.get(
            "/api/v1/weather", params={"city": "NonExistentCity12345"}
        )
        assert response.status_code == 404, "Should return 404 for non-existent city"

        print("✅ Error handling tests passed")

    def test_weather_service_with_state(self, client: TestClient, api_key: str):
        """Test weather service with state parameter for disambiguation."""
        os.environ["OPENWEATHERMAP_API_KEY"] = api_key
        os.environ["CACHE_ENABLED"] = "false"
        os.environ["RATE_LIMIT_ENABLED"] = "false"
        os.environ["DATA_STORE_TYPE"] = "local"
        os.environ["EVENT_STORE_TYPE"] = "local"

        # Test with state parameter (London, Ontario, Canada)
        response = client.get(
            "/api/v1/weather",
            params={"city": "London", "country_code": "CA", "state": "Ontario"},
        )

        assert (
            response.status_code == 200
        ), f"Expected 200, got {response.status_code}: {response.text}"

        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        assert len(data) > 0, "Response should contain at least one result"

        # Get the first result
        weather_result = data[0]
        assert "city" in weather_result
        assert "weather" in weather_result

        city_info = weather_result["city"]
        weather_data = weather_result["weather"]

        # Verify it's the correct London (Ontario, Canada)
        assert city_info["name"] == "London"
        assert city_info["country_code"] == "CA"
        assert city_info["state"] == "Ontario"

        assert "temperature" in weather_data
        assert "description" in weather_data

        print("✅ Successfully retrieved weather for London, Ontario, Canada:")
        print(f"   Temperature: {weather_data['temperature']}°C")
        print(f"   Description: {weather_data['description']}")

    def test_api_documentation_endpoint(self, client: TestClient):
        """Test that API documentation endpoints are accessible."""
        # Test OpenAPI schema endpoint
        response = client.get("/openapi.json")
        assert response.status_code == 200, "OpenAPI schema should be accessible"

        # Test Swagger UI endpoint
        response = client.get("/docs")
        assert response.status_code == 200, "Swagger UI should be accessible"

        print("✅ API documentation endpoints are accessible")
