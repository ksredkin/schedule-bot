import json

from redis.asyncio import Redis

from src.bot.core.config import (
    IMAGE_CACHE_EXPIRATION_SECONDS,
    USER_CLASS_CACHE_EXPIRATION_SECONDS,
)
from src.bot.redis_client.client import r
from src.bot.utils.logger import Logger

logger = Logger(__name__).get_logger()
NONE_SENTINEL = "__none__"


class CacheService:
    def __init__(self, redis: Redis = r) -> None:
        self.redis = redis

    async def get(self, prefix: str, key: str) -> str | bool | None:
        full_key = f"{prefix}:{key}"
        data: str | bool | None = await self.redis.get(full_key)

        if not data:
            logger.info(f"Кэш не найден: {full_key}")
            return None

        if data == NONE_SENTINEL:
            logger.info(f"Кэш установлен как None: {full_key}")
            return False

        logger.info(f"Кэш найден: {full_key}")
        return data

    async def set(
        self, prefix: str, key: str, value: str, expire: int | None = None
    ) -> None:
        full_key = f"{prefix}:{key}"
        await self.redis.set(full_key, value, ex=expire)
        ttl_str = f" (истечет через {expire}с)" if expire else " (без лимита)"
        logger.info(f"Данные сохранены в кэш: {full_key}{ttl_str}")

    async def get_image_id_from_cache(self, image: str) -> str | bool | None:
        return await self.get("image", image)

    async def set_image_id_in_cache(self, image: str, image_id: str) -> None:
        await self.set("image", image, image_id, IMAGE_CACHE_EXPIRATION_SECONDS)

    async def get_user_class_from_cache(self, telegram_id: int) -> str | bool | None:
        return await self.get("user", f"{telegram_id}:class")

    async def set_user_class_in_cache(
        self, telegram_id: int, grade: str | None
    ) -> None:
        value = grade if grade is not None else NONE_SENTINEL
        await self.set(
            "user", f"{telegram_id}:class", value, USER_CLASS_CACHE_EXPIRATION_SECONDS
        )

    async def get_changes_from_cache(
        self,
    ) -> dict[str, dict[str, list[dict[str, str]]]] | None:
        changes = await self.get("changes", "all")
        if changes is None:
            return None
        try:
            return json.loads(changes)  # type: ignore
        except Exception:
            logger.warning("Не удалось распарсить кэш замен, очищаем")
            await self.redis.delete("changes:all")
            return None

    async def set_changes_in_cache(
        self,
        changes: dict[str, dict[str, list[dict[str, str]]]],
    ) -> None:
        await self.set("changes", "all", json.dumps(changes))

    async def get_schedule_from_cache(
        self, grade: str
    ) -> dict[str, dict[str, dict[str, str | None]]] | None:
        if not grade:
            return None
        schedule = await self.get("schedule", grade.upper())
        if schedule is None:
            return None
        if not isinstance(schedule, str) and not isinstance(schedule, bytes):
            logger.warning(
                f"Некорректный тип данных в кэше расписания для класса {grade}: {type(schedule)}"
            )
            await self.redis.delete(f"schedule:{grade.upper()}")
            return None
        try:
            return json.loads(schedule)  # type: ignore
        except Exception:
            logger.warning("Не удалось распарсить кэш расписания, очищаем")
            await self.redis.delete(f"schedule:{grade.upper()}")
            return None

    async def set_schedule_in_cache(
        self, grade: str, schedule: dict[str, dict[str, dict[str, str | None]]]
    ) -> None:
        await self.set("schedule", grade.upper(), json.dumps(schedule))

    async def set_changes_url_in_cache(self, url: str) -> None:
        await self.set("url", "changes", url)

    async def get_changes_url_from_cache(self) -> str | bool | None:
        return await self.get("url", "changes")


cache_service = CacheService()
