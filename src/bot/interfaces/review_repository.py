from src.bot.database.orm_models import Review


class ReviewRepositoryInterface:
    @staticmethod
    async def create(telegram_id: int, text: str) -> Review | None:
        pass

    @staticmethod
    async def get_by_id(review_id: int) -> Review | None:
        pass

    @staticmethod
    async def get_all_reviews() -> list[Review] | None:
        pass

    @staticmethod
    async def delete_by_id(review_id: int) -> None:
        pass

    @staticmethod
    async def get_pending_reviews() -> list[Review] | None:
        pass

    @staticmethod
    async def get_archived_reviews() -> list[Review] | None:
        pass

    @staticmethod
    async def update_status(review_id: int, status: str) -> None:
        pass

    @staticmethod
    async def get_count_by_user_today(telegram_id: int) -> int:  # type: ignore
        pass
