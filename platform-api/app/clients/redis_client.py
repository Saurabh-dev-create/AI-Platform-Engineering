from functools import lru_cache

from redis import Redis

from app.config.settings import settings


@lru_cache
def get_redis_client() -> Redis:
    """
    Return the shared synchronous Redis client.

    decode_responses=True keeps short-lived platform state as strings
    rather than raw bytes.
    """

    return Redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        health_check_interval=30,
    )
