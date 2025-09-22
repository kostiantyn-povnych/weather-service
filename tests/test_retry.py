"""Unit tests for the retry module."""

import asyncio
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from weather_service.core.exceptions import ThirdPartyProviderUnavailable
from weather_service.core.retry import (
    RetryConfig,
    calculate_delay,
    is_retriable_error,
    with_retry,
)


class TestRetryConfig:
    """Test cases for RetryConfig class."""

    def test_default_initialization(self):
        """Test RetryConfig with default values."""
        config = RetryConfig()

        assert config.max_retries == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 10.0
        assert config.backoff_factor == 2.0
        assert config.retriable_status_codes == {500, 502, 503, 504, 429, 408}

    def test_custom_initialization(self):
        """Test RetryConfig with custom values."""
        custom_codes = {500, 503}
        config = RetryConfig(
            max_retries=5,
            base_delay=2.0,
            max_delay=20.0,
            backoff_factor=3.0,
            retriable_status_codes=custom_codes,
        )

        assert config.max_retries == 5
        assert config.base_delay == 2.0
        assert config.max_delay == 20.0
        assert config.backoff_factor == 3.0
        assert config.retriable_status_codes == custom_codes

    def test_none_retriable_status_codes(self):
        """Test RetryConfig with None retriable_status_codes."""
        config = RetryConfig(retriable_status_codes=None)
        assert config.retriable_status_codes == {500, 502, 503, 504, 429, 408}


class TestIsRetriableError:
    """Test cases for is_retriable_error function."""

    def test_http_status_error_retriable(self):
        """Test HTTPStatusError with retriable status codes."""
        retriable_codes = [500, 502, 503, 504, 429, 408]

        for code in retriable_codes:
            response = httpx.Response(status_code=code)
            error = httpx.HTTPStatusError("Error", request=None, response=response)
            assert is_retriable_error(error) is True

    def test_http_status_error_non_retriable(self):
        """Test HTTPStatusError with non-retriable status codes."""
        non_retriable_codes = [400, 401, 403, 404, 422]

        for code in non_retriable_codes:
            response = httpx.Response(status_code=code)
            error = httpx.HTTPStatusError("Error", request=None, response=response)
            assert is_retriable_error(error) is False

    def test_timeout_exception(self):
        """Test TimeoutException is retriable."""
        error = httpx.TimeoutException("Timeout")
        assert is_retriable_error(error) is True

    def test_connect_error(self):
        """Test ConnectError is retriable."""
        error = httpx.ConnectError("Connection failed")
        assert is_retriable_error(error) is True

    def test_network_error(self):
        """Test NetworkError is retriable."""
        error = httpx.NetworkError("Network error")
        assert is_retriable_error(error) is True

    def test_non_retriable_exception(self):
        """Test non-retriable exceptions."""
        error = ValueError("Some error")
        assert is_retriable_error(error) is False

    def test_generic_exception(self):
        """Test generic Exception is not retriable."""
        error = Exception("Generic error")
        assert is_retriable_error(error) is False


class TestCalculateDelay:
    """Test cases for calculate_delay function."""

    def test_basic_exponential_backoff(self):
        """Test basic exponential backoff calculation."""
        config = RetryConfig(base_delay=1.0, backoff_factor=2.0, max_delay=10.0)

        assert calculate_delay(0, config) == 1.0
        assert calculate_delay(1, config) == 2.0
        assert calculate_delay(2, config) == 4.0
        assert calculate_delay(3, config) == 8.0

    def test_max_delay_limit(self):
        """Test that delay is capped at max_delay."""
        config = RetryConfig(base_delay=1.0, backoff_factor=2.0, max_delay=5.0)

        assert calculate_delay(0, config) == 1.0
        assert calculate_delay(1, config) == 2.0
        assert calculate_delay(2, config) == 4.0
        assert calculate_delay(3, config) == 5.0  # Capped at max_delay
        assert calculate_delay(4, config) == 5.0  # Still capped

    def test_custom_backoff_factor(self):
        """Test with custom backoff factor."""
        config = RetryConfig(base_delay=2.0, backoff_factor=3.0, max_delay=100.0)

        assert calculate_delay(0, config) == 2.0
        assert calculate_delay(1, config) == 6.0
        assert calculate_delay(2, config) == 18.0
        assert calculate_delay(3, config) == 54.0

    def test_zero_base_delay(self):
        """Test with zero base delay."""
        config = RetryConfig(base_delay=0.0, backoff_factor=2.0, max_delay=10.0)

        assert calculate_delay(0, config) == 0.0
        assert calculate_delay(1, config) == 0.0
        assert calculate_delay(2, config) == 0.0


class TestWithRetryDecorator:
    """Test cases for with_retry decorator."""

    @pytest.mark.asyncio
    async def test_successful_first_attempt(self):
        """Test successful execution on first attempt."""

        @with_retry()
        async def mock_function():
            return "success"

        result = await mock_function()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_successful_after_retries(self):
        """Test successful execution after retries."""
        call_count = 0

        @with_retry(config=RetryConfig(max_retries=2, base_delay=0.01))
        async def mock_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.HTTPStatusError(
                    "Error", request=None, response=httpx.Response(status_code=500)
                )
            return "success"

        result = await mock_function()
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Test behavior when max retries are exceeded."""
        call_count = 0

        @with_retry(config=RetryConfig(max_retries=2, base_delay=0.01))
        async def mock_function():
            nonlocal call_count
            call_count += 1
            raise httpx.HTTPStatusError(
                "Error", request=None, response=httpx.Response(status_code=500)
            )

        with pytest.raises(ThirdPartyProviderUnavailable) as exc_info:
            await mock_function()

        assert call_count == 3  # Initial attempt + 2 retries
        assert "Unknown Provider" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_non_retriable_error_immediate_failure(self):
        """Test that non-retriable errors fail immediately."""
        call_count = 0

        @with_retry(config=RetryConfig(max_retries=3, base_delay=0.01))
        async def mock_function():
            nonlocal call_count
            call_count += 1
            raise httpx.HTTPStatusError(
                "Error", request=None, response=httpx.Response(status_code=400)
            )

        with pytest.raises(httpx.HTTPStatusError):
            await mock_function()

        assert call_count == 1  # Should not retry

    @pytest.mark.asyncio
    async def test_custom_provider_name(self):
        """Test decorator with custom provider name."""

        @with_retry(provider_name="TestProvider")
        async def mock_function():
            raise httpx.HTTPStatusError(
                "Error", request=None, response=httpx.Response(status_code=500)
            )

        with pytest.raises(ThirdPartyProviderUnavailable) as exc_info:
            await mock_function()

        assert "TestProvider" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_custom_retry_config(self):
        """Test decorator with custom retry configuration."""
        call_count = 0

        config = RetryConfig(max_retries=1, base_delay=0.01)

        @with_retry(config=config)
        async def mock_function():
            nonlocal call_count
            call_count += 1
            raise httpx.HTTPStatusError(
                "Error", request=None, response=httpx.Response(status_code=500)
            )

        with pytest.raises(ThirdPartyProviderUnavailable):
            await mock_function()

        assert call_count == 2  # Initial attempt + 1 retry

    @pytest.mark.asyncio
    async def test_timeout_exception_retry(self):
        """Test retry behavior with TimeoutException."""
        call_count = 0

        @with_retry(config=RetryConfig(max_retries=1, base_delay=0.01))
        async def mock_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise httpx.TimeoutException("Timeout")
            return "success"

        result = await mock_function()
        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_connect_error_retry(self):
        """Test retry behavior with ConnectError."""
        call_count = 0

        @with_retry(config=RetryConfig(max_retries=1, base_delay=0.01))
        async def mock_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise httpx.ConnectError("Connection failed")
            return "success"

        result = await mock_function()
        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_network_error_retry(self):
        """Test retry behavior with NetworkError."""
        call_count = 0

        @with_retry(config=RetryConfig(max_retries=1, base_delay=0.01))
        async def mock_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise httpx.NetworkError("Network error")
            return "success"

        result = await mock_function()
        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_function_preserves_signature(self):
        """Test that the decorator preserves function signature."""

        @with_retry()
        async def mock_function(arg1: str, arg2: int = 42, *, kwarg: bool = True):
            return f"{arg1}-{arg2}-{kwarg}"

        result = await mock_function("test", kwarg=False)
        assert result == "test-42-False"

    @pytest.mark.asyncio
    async def test_zero_max_retries(self):
        """Test behavior with zero max retries."""
        call_count = 0

        @with_retry(config=RetryConfig(max_retries=0))
        async def mock_function():
            nonlocal call_count
            call_count += 1
            raise httpx.HTTPStatusError(
                "Error", request=None, response=httpx.Response(status_code=500)
            )

        with pytest.raises(ThirdPartyProviderUnavailable):
            await mock_function()

        assert call_count == 1  # Only initial attempt, no retries

    @pytest.mark.asyncio
    async def test_multiple_different_errors(self):
        """Test retry with different types of errors."""
        call_count = 0

        @with_retry(config=RetryConfig(max_retries=3, base_delay=0.01))
        async def mock_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise httpx.HTTPStatusError(
                    "Error", request=None, response=httpx.Response(status_code=500)
                )
            elif call_count == 2:
                raise httpx.TimeoutException("Timeout")
            elif call_count == 3:
                raise httpx.ConnectError("Connection failed")
            return "success"

        result = await mock_function()
        assert result == "success"
        assert call_count == 4

    @pytest.mark.asyncio
    async def test_mixed_retriable_and_non_retriable_errors(self):
        """Test behavior with mixed retriable and non-retriable errors."""
        call_count = 0

        @with_retry(config=RetryConfig(max_retries=3, base_delay=0.01))
        async def mock_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise httpx.HTTPStatusError(
                    "Error", request=None, response=httpx.Response(status_code=500)
                )
            elif call_count == 2:
                raise httpx.HTTPStatusError(
                    "Error", request=None, response=httpx.Response(status_code=400)
                )  # Non-retriable
            return "success"

        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await mock_function()

        assert call_count == 2  # Should stop after non-retriable error
        assert exc_info.value.response.status_code == 400
