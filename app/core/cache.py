
import json
from redis.asyncio import Redis
from app.core.config import settings

_redis_client: Redis | None = None


async def get_redis() -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis.from_url(
            settings.REDIS_URL, decode_responses=True)
    return _redis_client


async def get(key: str) -> dict | list | None:
    redis = await get_redis()
    value = await redis.get(key)
    return json.loads(value) if value else None


async def cache_set(key: str, value: dict | list, ttl: int = 60) -> None:
    redis = await get_redis()
    await redis.setex(key, ttl, json.dumps(value))


async def cache_delete(key: str) -> None:
    redis = await get_redis()
    await redis.delete(key)


async def cache_delete_pattern(pattern: str) -> None:
    """Delete all keys matching a glob pattern e.g 'CAPSTONES_PROJECT:list:*'."""
    redis = await get_redis()
    keys = await redis.keys(pattern)
    if keys:
        await redis.delete(*keys)
