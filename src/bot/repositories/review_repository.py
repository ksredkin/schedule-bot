from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.database.orm_models import Review
from src.bot.interfaces.review_repository import ReviewRepositoryInterface
from src.bot.utils.logger import Logger

logger = Logger(__name__).get_logger()


class ReviewRepository(ReviewRepositoryInterface):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, telegram_id: int, text: str) -> Review | None:
        new_review = Review(telegram_id=telegram_id, text=text)
        self.session.add(new_review)
        await self.session.flush()
        await self.session.refresh(new_review)
        return new_review

    async def get_by_id(self, review_id: int) -> Review | None:
        result = await self.session.execute(
            select(Review).where(Review.id == review_id)
        )
        return result.scalar_one_or_none()

    async def get_all_reviews(self) -> list[Review]:
        result = await self.session.execute(
            select(Review).order_by(Review.created_at.desc())
        )
        return result.scalars().all()  # type: ignore

    async def delete_by_id(self, review_id: int) -> None:
        result = await self.session.execute(
            select(Review).where(Review.id == review_id)
        )
        review = result.scalar_one_or_none()
        if review:
            await self.session.delete(review)

    async def get_pending_reviews(self) -> list[Review]:
        result = await self.session.execute(
            select(Review)
            .filter(Review.status == "pending")
            .order_by(Review.created_at.asc())
        )
        return result.scalars().all()  # type: ignore

    async def get_archived_reviews(self) -> list[Review]:
        result = await self.session.execute(
            select(Review)
            .where(Review.status == "reviewed")
            .order_by(Review.created_at.desc())
        )
        return result.scalars().all()  # type: ignore

    async def update_status(self, review_id: int, status: str) -> None:
        result = await self.session.execute(
            select(Review).where(Review.id == review_id)
        )
        review = result.scalar_one_or_none()
        if review:
            review.status = status  # type: ignore

    async def get_count_by_user_today(self, telegram_id: int) -> int:
        result = await self.session.execute(
            select(func.count(Review.id)).where(
                Review.telegram_id == telegram_id,
                Review.created_at >= datetime.now().date(),
            )
        )
        count = result.scalar()
        return count if count else 0
