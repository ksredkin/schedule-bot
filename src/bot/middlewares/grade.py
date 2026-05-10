from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message

from src.bot.core.exceptions import (
    GradeNotFoundError,
    GradeNotSelectedError,
    InvalidCommandError,
)
from src.bot.repositories.user_repository import UserRepository
from src.bot.services.user_service import resolve_grade


class GradeMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,  # type: ignore
        data: dict[str, Any],
    ) -> Any:
        if not event.from_user:
            return

        need_grade = get_flag(data, "need_grade")

        if not need_grade:
            return await handler(event, data)

        user_repo = UserRepository()
        cmd = get_flag(data, "cmd") or "cmd"

        try:
            grade = await resolve_grade(event, user_repo, cmd)
        except (GradeNotSelectedError, GradeNotFoundError, InvalidCommandError) as e:
            await event.answer(f"🚫 <b>Ошибка:</b> {str(e)}")
            return

        data["grade"] = grade
        return await handler(event, data)
