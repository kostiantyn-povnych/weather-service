"""Test configuration and fixtures for integration tests."""

import asyncio
import sys
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from weather_service.api.app import fastApiApp


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
