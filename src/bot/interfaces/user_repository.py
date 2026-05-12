from src.bot.database.orm_models import User


class UserRepositoryInterface:
    @staticmethod
    async def get_users() -> list[User] | None:
        pass

    @staticmethod
    async def get_users_by_class(grade: str) -> list[User] | None:
        pass

    @staticmethod
    async def get_total_users() -> int | None:
        pass

    @staticmethod
    async def get_user_count_by_grades() -> dict[str, int | None]:
        pass

    @staticmethod
    async def get_user_by_telegram_id(telegram_id: int) -> User | None:
        pass

    @staticmethod
    async def create_user(telegram_id: int, grade: str | None) -> User | None:
        pass

    @staticmethod
    async def update_user_grade(telegram_id: int, grade: str) -> User | None:
        pass
