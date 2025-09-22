import logging

from fastapi import FastAPI
from fastapi_redis_rate_limiter import RedisClient, RedisRateLimiterMiddleware

from weather_service.core.settings import settings

LOGGER = logging.getLogger(__name__)


def init_rate_limiting(app: FastAPI) -> None:
    """Initialize rate limiting.

    Args:
        app: FastAPI app instance
    """

    if not settings.rate_limiting.enabled:
        LOGGER.info("Rate limiting is disabled")
        return

    LOGGER.info(
        "Initializing rate limiting with configuration: %s", settings.rate_limiting
    )

    redis_client = RedisClient(
        host=settings.rate_limiting.redis_host,
        port=settings.rate_limiting.redis_port,
        db=settings.rate_limiting.redis_db,
    )

    app.add_middleware(
        RedisRateLimiterMiddleware,
        redis_client=redis_client,
        limit=settings.rate_limiting.limit,
        window=settings.rate_limiting.window,
    )
