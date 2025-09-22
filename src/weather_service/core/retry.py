"""Retry configuration and decorators for HTTP requests."""

import asyncio
import logging
from functools import wraps
from typing import Callable, TypeVar

import httpx

from weather_service.core.exceptions import ThirdPartyProviderUnavailable

LOGGER = logging.getLogger(__name__)

T = TypeVar("T")


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 10.0,
        backoff_factor: float = 2.0,
        retriable_status_codes: set[int] | None = None,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.retriable_status_codes = retriable_status_codes or {
            500,
            502,
            503,
            504,  # Server errors
            429,  # Rate limiting
            408,  # Request timeout
        }


def is_retriable_error(error: Exception) -> bool:
    """Check if an error is retriable."""
    if isinstance(error, httpx.HTTPStatusError):
        return error.response.status_code in {
            500,
            502,
            503,
            504,  # Server errors
            429,  # Rate limiting
            408,  # Request timeout
        }
    elif isinstance(error, httpx.TimeoutException):
        return True
    elif isinstance(error, httpx.ConnectError):
        return True
    elif isinstance(error, httpx.NetworkError):
        return True
    return False


def calculate_delay(attempt: int, config: RetryConfig) -> float:
    """Calculate delay for exponential backoff."""
    delay = config.base_delay * (config.backoff_factor**attempt)
    return min(delay, config.max_delay)


def with_retry(
    config: RetryConfig | None = None,
    provider_name: str = "Unknown Provider",
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to add retry logic to async functions."""

    if config is None:
        config = RetryConfig()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_error = None

            for attempt in range(config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e

                    if not is_retriable_error(e):
                        LOGGER.error(
                            f"Non-retriable error from {provider_name} on attempt {attempt + 1}: {e}"
                        )
                        raise

                    if attempt < config.max_retries:
                        delay = calculate_delay(attempt, config)
                        LOGGER.warning(
                            f"Retriable error from {provider_name} on attempt {attempt + 1}: {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                        await asyncio.sleep(delay)
                    else:
                        LOGGER.error(
                            f"Max retries ({config.max_retries}) exceeded for {provider_name}. "
                            f"Last error: {e}"
                        )
                        raise ThirdPartyProviderUnavailable(provider_name, e)

            # This should never be reached, but just in case
            raise ThirdPartyProviderUnavailable(provider_name, last_error)

        return wrapper

    return decorator
