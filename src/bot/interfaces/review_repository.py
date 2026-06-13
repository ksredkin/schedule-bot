from src.bot.database.orm_models import Review


class ReviewRepositoryInterface:
    async def create(self, telegram_id: int, text: str) -> Review | None:
        pass

    async def get_by_id(self, review_id: int) -> Review | None:
        pass

    async def get_all_reviews(self) -> list[Review] | None:
        pass

    async def delete_by_id(self, review_id: int) -> None:
        pass

    async def get_pending_reviews(self) -> list[Review] | None:
        pass

    async def get_archived_reviews(self) -> list[Review] | None:
        pass

    async def update_status(self, review_id: int, status: str) -> None:
        pass

    async def get_count_by_user_today(self, telegram_id: int) -> int:  # type: ignore
        pass
