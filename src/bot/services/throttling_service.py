from redis.asyncio import Redis

from src.bot.redis_client.client import r


class ThrottlingService:
    def __init__(self, redis: Redis = r):
        self.redis = redis
        self.limit = 1
        self.prefix = "throttle:"

    async def is_spaming(self, user_id: int, media_group_id: str | None = None) -> bool:
        if media_group_id:
            mg_key = f"mg:{media_group_id}"
            if await self.redis.exists(mg_key):
                return False
            await self.redis.set(mg_key, "1", ex=5)

        key = f"{self.prefix}{user_id}"

        exists = await self.redis.get(key)
        if exists:
            return True

        await self.redis.set(key, "1", ex=self.limit)
        return False
