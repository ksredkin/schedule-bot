from maxapi.types import Message

from src.bot.core.exceptions import (
    GradeNotFoundError,
    GradeNotSelectedError,
    InvalidCommandError,
)
from src.bot.repositories.user_repository import UserRepository
from src.bot.services.cache_service import cache_service
from src.bot.utils.constants import classes


async def resolve_grade(
    message: Message,
    user_repo: UserRepository,
    command_name: str = "cmd",
) -> str | None:
    if not message or not message.body or not message.body.text:
        return None

    if not message.sender or not message.sender.user_id:
        return None

    user_id = message.sender.user_id
    parts = message.body.text.split()

    if len(parts) == 1:
        user_class = await cache_service.get_user_class_from_cache(user_id)

        if user_class is not None:
            if user_class is False:
                raise GradeNotSelectedError(
                    f"не выбран класс. Используйте /set_my_class или /{command_name} {{class}}."
                )

            return str(user_class)

        user = await user_repo.get_user_by_max_id(user_id)

        if not user or not user.grade:
            raise GradeNotSelectedError(
                f"не выбран класс. Используйте /set_my_class или /{command_name} {{class}}."
            )

        grade = str(user.grade)
        await cache_service.set_user_class_in_cache(user_id, grade)

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
