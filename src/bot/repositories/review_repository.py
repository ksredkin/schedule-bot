from datetime import datetime

from sqlalchemy import func, select

from src.bot.database.connection import session
from src.bot.database.orm_models import Review
from src.bot.interfaces.review_repository import ReviewRepositoryInterface
from src.bot.utils.logger import Logger

logger = Logger(__name__).get_logger()


class ReviewRepository(ReviewRepositoryInterface):
    @staticmethod
    async def create(telegram_id: int, text: str) -> Review | None:
        async with session() as conn:
            try:
                new_review = Review(telegram_id=telegram_id, text=text)
                conn.add(new_review)
                await conn.commit()
                await conn.refresh(new_review)
                return new_review
            except Exception as e:
                logger.critical(f"Произошла ошибка при попытке создать отзыв в бд: {e}")
                return None

    @staticmethod
    async def get_by_id(review_id: int) -> Review | None:
        async with session() as conn:
            try:
                result = await conn.execute(
                    select(Review).filter(Review.id == review_id)
                )
                review = result.scalar_one_or_none()
                return review
            except Exception as e:
                logger.critical(
                    f"Произошла ошибка при попытке получить отзыв по id из бд: {e}"
                )
                return None

    @staticmethod
    async def get_all_reviews() -> list[Review] | None:
        async with session() as conn:
            try:
                result = await conn.execute(
                    select(Review).order_by(Review.created_at.desc())
                )
                reviews = result.scalars().all()
                return reviews or []  # type: ignore
            except Exception as e:
                logger.critical(
                    f"Произошла ошибка при попытке получить все отзывы из бд: {e}"
                )
                return None

    @staticmethod
    async def delete_by_id(review_id: int) -> None:
        async with session() as conn:
            try:
                result = await conn.execute(
                    select(Review).filter(Review.id == review_id)
                )
                review = result.scalar_one_or_none()
                if review:
                    await conn.delete(review)
                    await conn.commit()
            except Exception as e:
                logger.critical(
                    f"Произошла ошибка при попытке удалить отзыв из бд: {e}"
                )

    @staticmethod
    async def get_pending_reviews() -> list[Review] | None:
        async with session() as conn:
            try:
                result = await conn.execute(
                    select(Review)
                    .filter(Review.status == "pending")
                    .order_by(Review.created_at.asc())
                )
                reviews = result.scalars().all()
                return reviews or []  # type: ignore
            except Exception as e:
                logger.critical(
                    f"Произошла ошибка при попытке получить ожидающие отзывы из бд: {e}"
                )
                return None

    @staticmethod
    async def get_archived_reviews() -> list[Review] | None:
        async with session() as conn:
            try:
                result = await conn.execute(
                    select(Review)
                    .filter(Review.status == "reviewed")
                    .order_by(Review.created_at.desc())
                )
                reviews = result.scalars().all()
                return reviews or []  # type: ignore
            except Exception as e:
                logger.critical(
                    f"Произошла ошибка при попытке получить архивные отзывы из бд: {e}"
                )
                return None

    @staticmethod
    async def update_status(review_id: int, status: str) -> None:
        async with session() as conn:
            try:
                result = await conn.execute(
                    select(Review).filter(Review.id == review_id)
                )
                review = result.scalar_one_or_none()
                if review:
                    review.status = status  # type: ignore
                    await conn.commit()
            except Exception as e:
                logger.critical(
                    f"Произошла ошибка при попытке обновить статус отзыва в бд: {e}"
                )

    @staticmethod
    async def get_count_by_user_today(telegram_id: int) -> int:
        async with session() as conn:
            try:
                result = await conn.execute(
                    select(func.count(Review.id)).filter(
                        Review.telegram_id == telegram_id,
                        Review.created_at >= datetime.now().date(),
                    )
                )
                count = result.scalar()
                return count if count else 0
            except Exception as e:
                logger.critical(
                    f"Произошла ошибка при попытке получить количество отзывов пользователя за сегодня: {e}"
                )
                return 0
