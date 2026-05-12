from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

from src.bot.services.throttling_service import ThrottlingService


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, throttling_service: ThrottlingService):
        self.service = throttling_service
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,  # type: ignore
        data: Dict[str, Any],
    ) -> Any:
        if not event.from_user:
            return

        if await self.service.is_spaming(event.from_user.id):
            await event.reply(
                "⌛ Пожалуйста, не спамьте командами. Подождите немного перед повторной попыткой."
            )
            return

        return await handler(event, data)
