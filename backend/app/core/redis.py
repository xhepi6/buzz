import aioredis
from typing import Optional
from .config import settings

class RedisClient:
    redis: Optional[aioredis.Redis] = None

    @classmethod
    async def init_redis(cls):
        if not cls.redis:
            cls.redis = await aioredis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                encoding="utf-8",
                decode_responses=True
            )

    @classmethod
    async def close_redis(cls):
        if cls.redis:
            await cls.redis.close()

redis_client = RedisClient()
