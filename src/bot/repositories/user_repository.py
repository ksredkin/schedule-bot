from sqlalchemy import func, select

from src.bot.database.connection import session
from src.bot.database.orm_models import User
from src.bot.interfaces.user_repository import UserRepositoryInterface
from src.bot.utils.logger import Logger

logger = Logger(__name__).get_logger()


class UserRepository(UserRepositoryInterface):
    @staticmethod
    async def get_users() -> list[User] | None:
        async with session() as conn:
            try:
                result = await conn.execute(select(User))
                users = list(result.scalars().all())
                return users
            except Exception as e:
                logger.critical(
                    f"Произошла ошибка при попытке получить всех пользователей из бд: {e}"
                )
                return None

    @staticmethod
    async def get_users_by_class(grade: str) -> list[User] | None:
        async with session() as conn:
            try:
                result = await conn.execute(
                    select(User).filter(User.grade == grade.lower())
                )
                users = list(result.scalars().all())
                return users
            except Exception as e:
                logger.critical(
                    f"Произошла ошибка при попытке получить пользователей по классу {grade} из бд: {e}"
                )
                return None

    @staticmethod
    async def get_total_users() -> int | None:
        async with session() as conn:
            try:
                result = await conn.execute(select(func.count(User.id)))
                users_total = result.scalar()
                return users_total
            except Exception as e:
                logger.critical(
                    f"Произошла ошибка при попытке получить количество всех пользователей из бд: {e}"
                )
                return None

    @staticmethod
    async def get_user_count_by_grades() -> dict[str, int | None]:
        async with session() as conn:
            try:
                result = await conn.execute(
                    select(func.coalesce(User.grade, "Не указан"), func.count(User.id))
                    .group_by(User.grade)
                    .order_by(User.grade)
                )
                users_total = result.all()
                return dict(users_total) if users_total else {}  # type: ignore
            except Exception as e:
                logger.critical(
                    f"Произошла ошибка при попытке получить количество пользователей по классам из бд: {e}"
                )
                return {}

    @staticmethod
    async def get_user_by_telegram_id(telegram_id: int) -> User | None:
        async with session() as conn:
            try:
                result = await conn.execute(
                    select(User).filter(User.telegram_id == telegram_id)
                )
                user = result.scalars().first()
                return user
            except Exception as e:
                logger.critical(
                    f"Произошла ошибка при попытке получить пользователя из бд по telegram_id: {e}"
                )
                return None

    @staticmethod
    async def create_user(telegram_id: int, grade: str | None) -> User | None:
        async with session() as conn:
            try:
                user = User(
                    telegram_id=telegram_id, grade=grade.lower() if grade else None
                )
                conn.add(user)

                await conn.commit()
                await conn.refresh(user)

                return user
            except Exception as e:
                logger.critical(
                    f"Произошла ошибка при попытке создать пользователя в бд: {e}"
                )
                return None

    @staticmethod
    async def update_user_grade(telegram_id: int, grade: str) -> User | None:
        async with session() as conn:
            try:
                result = await conn.execute(
                    select(User).filter(User.telegram_id == telegram_id)
                )
                user = result.scalars().first()

                if not user:
                    return None

                user.grade = grade.lower() if grade else None  # type: ignore

                await conn.commit()
                await conn.refresh(user)

                return user
            except Exception as e:
                logger.critical(
                    f"Произошла ошибка при попытке обновить класс пользователя в бд: {e}"
                )
                return None
