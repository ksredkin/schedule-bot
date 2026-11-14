from typing import Any, Awaitable, Callable, Dict

from maxapi.enums.parse_mode import ParseMode
from maxapi.filters.middleware import BaseMiddleware
from maxapi.types import MessageCreated, UpdateUnion

from src.bot.core.exceptions import (
    GradeNotFoundError,
    GradeNotSelectedError,
    InvalidCommandError,
)
from src.bot.repositories.user_repository import UserRepository
from src.bot.services.user_service import resolve_grade


class GradeMiddleware(BaseMiddleware):
    def __init__(self, cmd: str):
        self.cmd = cmd

    async def __call__(
        self,
        handler: Callable[[UpdateUnion, Dict[str, Any]], Awaitable[Any]],
        event_object: UpdateUnion,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event_object, MessageCreated):
            return await handler(event_object, data)

        message = event_object.message
        if not message or not message.sender:
            return

        db_session = data.get("db_session")
        if not db_session:
            raise RuntimeError("GradeMiddleware требует db_session")

        user_repo = UserRepository(db_session)

        try:
            grade = await resolve_grade(message, user_repo, self.cmd)
        except (GradeNotSelectedError, GradeNotFoundError, InvalidCommandError) as e:
            await message.answer(
                text=f"🚫 <b>Ошибка:</b> {str(e)}",
                parse_mode=ParseMode.HTML,
            )
            return

        data["grade"] = grade
        return await handler(event_object, data)
