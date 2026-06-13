from src.bot.database.orm_models import User


class UserRepositoryInterface:
    async def get_users(self) -> list[User] | None:
        pass

    async def get_users_by_class(self, grade: str) -> list[User] | None:
        pass

    async def get_total_users(self) -> int | None:
        pass

    async def get_user_count_by_grades(self) -> dict[str, int | None] | None:
        pass

    async def get_user_by_telegram_id(self, telegram_id: int) -> User | None:
        pass

    async def create_user(self, telegram_id: int, grade: str | None) -> User | None:
        pass

    async def update_user_grade(self, telegram_id: int, grade: str) -> User | None:
        pass
