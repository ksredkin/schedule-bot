from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.database.orm_models import User
from src.bot.interfaces.user_repository import UserRepositoryInterface
from src.bot.utils.logger import Logger

logger = Logger(__name__).get_logger()


class UserRepository(UserRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_users(self) -> list[User]:
        result = await self.session.execute(select(User))
        return result.scalars().all()  # type: ignore

    async def get_users_by_class(self, grade: str) -> list[User]:
        result = await self.session.execute(
            select(User).where(User.grade == grade.lower())
        )
        return result.scalars().all()  # type: ignore

    async def get_total_users(self) -> int | None:
        result = await self.session.execute(select(func.count(User.id)))
        return result.scalar()

    async def get_user_count_by_grades(self) -> dict[str, int | None]:
        result = await self.session.execute(
            select(func.coalesce(User.grade, "Не указан"), func.count(User.id))
            .group_by(User.grade)
            .order_by(User.grade)
        )
        return {row[0]: row[1] for row in result.all()}

    async def get_user_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def create_user(self, telegram_id: int, grade: str | None) -> User:
        user = User(telegram_id=telegram_id, grade=grade.lower() if grade else None)
        self.session.add(user)

        await self.session.flush()
        await self.session.refresh(user)

        return user

    async def update_user_grade(self, telegram_id: int, grade: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalars().first()

        if not user:
            return None

        user.grade = grade.lower() if grade else None  # type: ignore

        await self.session.flush()
        await self.session.refresh(user)

        return user
