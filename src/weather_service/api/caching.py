import logging
from typing import Any, Callable

from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache as _cache
from redis.asyncio import from_url

from weather_service.core.settings import settings

LOGGER = logging.getLogger(__name__)


def cache_or_nop(
    *, expire: int = settings.cache.ttl_seconds, namespace: str = settings.cache.prefix
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Returns fastapi-cache2's @cache if enabled; otherwise a no-op decorator.
    """
    if settings.cache.enabled:
        return _cache(expire=expire, namespace=namespace)

    # no-op decorator
    def _passthrough(func: Callable[..., Any]) -> Callable[..., Any]:
        return func

    return _passthrough


def init_cache() -> None:
    """
    Initialize cache backend if caching is enabled.
    - redis backend if CACHE_BACKEND=redis
    - in-memory backend if CACHE_BACKEND=memory
    If caching is disabled, do nothing (decorators are already no-op).
    """
    if not settings.cache.enabled:
        LOGGER.info("Caching is disabled")
        return

    LOGGER.info("Initializing cache with configuration: %s", settings.cache)

    prefix = settings.cache.prefix

    if settings.cache.backend == "redis":
        redis = from_url(
            settings.cache.redis_url, encoding="utf-8", decode_responses=True
        )
        FastAPICache.init(RedisBackend(redis), prefix=prefix)
    elif settings.cache.backend == "memory":
        LOGGER.info("Initializing in-memory cache...")
        FastAPICache.init(InMemoryBackend(), prefix=prefix)
    else:
        raise RuntimeError(f"Unsupported CACHE_BACKEND={settings.cache.backend}")
