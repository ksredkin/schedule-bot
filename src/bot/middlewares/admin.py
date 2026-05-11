import os
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message

from src.bot.utils.logger import Logger

logger = Logger(__name__).get_logger()


class AdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,  # type: ignore
        data: dict[str, Any],
    ) -> Any:
        user = event.from_user
        if not user:
            return

        need_admin = get_flag(data, "need_admin", default=False)
        if not need_admin:
            return await handler(event, data)

        admin_id = os.getenv("ADMIN_ID")
        if not admin_id:
            logger.warning("ADMIN_ID не установлен в переменных окружения")
            return

        if user.id != int(admin_id):
            logger.warning(
                f"Пользователь @{user.username} с id {user.id} не имеет доступа к админ-панели"
            )
            return

        return await handler(event, data)
