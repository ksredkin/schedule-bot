from aiogram import types

from src.bot.core.exceptions import (
    GradeNotFoundError,
    GradeNotSelectedError,
    InvalidCommandError,
)
from src.bot.interfaces.user_repository import UserRepositoryInterface
from src.bot.services.cache_service import cache_service
from src.bot.utils.constants import classes


async def resolve_grade(
    message: types.Message,
    user_repo: UserRepositoryInterface,
    command_name: str = "cmd",
) -> str | None:
    if not message:
        return None

    if not message.text or not message.from_user:
        return None

    parts = message.text.split()

    if len(parts) == 1:
        if not message.from_user:
            return None

        user_class = await cache_service.get_user_class_from_cache(message.from_user.id)

        if user_class is not None:
            if user_class is False:
                raise GradeNotSelectedError(
                    f"не выбран класс. Используйте /set_my_class или /{command_name} {{class}}."
                )

            return str(user_class)

        user = await user_repo.get_user_by_telegram_id(message.from_user.id)

        if not user or not user.grade:
            raise GradeNotSelectedError(
                f"не выбран класс. Используйте /set_my_class или /{command_name} {{class}}."
            )

        grade = str(user.grade)

        await cache_service.set_user_class_in_cache(message.from_user.id, grade)

        return grade

    elif len(parts) < 4:
        grade = " ".join(parts[1:]).upper()

        if grade not in classes:
            raise GradeNotFoundError("такого класса нет.")

        return grade

    else:
        raise InvalidCommandError(
            f"неверный формат. Используйте /{command_name} {{class}}."
        )
