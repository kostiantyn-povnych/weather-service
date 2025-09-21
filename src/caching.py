from typing import Any, Callable

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache as _cache
from redis.asyncio import from_url

from settings import settings


def cache_or_nop(
    *, expire: int, namespace: str
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


async def init_cache(app: FastAPI) -> None:
    """
    Initialize cache backend if caching is enabled.
    - redis backend if CACHE_BACKEND=redis
    - in-memory backend if CACHE_BACKEND=memory
    If caching is disabled, do nothing (decorators are already no-op).
    """
    if not settings.cache.enabled:
        return

    prefix = settings.cache.prefix

    if settings.cache.backend == "redis":
        redis = from_url(
            settings.cache.redis_url, encoding="utf-8", decode_responses=True
        )
        FastAPICache.init(RedisBackend(redis), prefix=prefix)
    elif settings.cache.backend == "memory":
        FastAPICache.init(InMemoryBackend(), prefix=prefix)
    else:
        raise RuntimeError(f"Unsupported CACHE_BACKEND={settings.cache.backend}")
