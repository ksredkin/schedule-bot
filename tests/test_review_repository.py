import os

os.environ["DB_USER"] = "test_user"
os.environ["DB_PASSWORD"] = "test_password"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_NAME"] = "test_db"

import pytest

from src.bot.database.orm_models import Review
from src.bot.repositories.review_repository import ReviewRepository


@pytest.mark.asyncio
async def test_create_review(sessionmaker):
    async with sessionmaker() as session:
        review_repository = ReviewRepository(session)
        telegram_id = 123456789
        text = "This is a test review."

        review = await review_repository.create(telegram_id, text)

        assert isinstance(review, Review)
        assert review.telegram_id == telegram_id
        assert review.text == text


@pytest.mark.asyncio
async def test_get_review_by_id(sessionmaker):
    async with sessionmaker() as session:
        review_repository = ReviewRepository(session)
        telegram_id = 123456789
        text = "This is a test review."

        review = await review_repository.create(telegram_id, text)
        retrieved_review = await review_repository.get_by_id(review.id)

        assert isinstance(retrieved_review, Review)
        assert retrieved_review.id == review.id
        assert retrieved_review.telegram_id == telegram_id
        assert retrieved_review.text == text


@pytest.mark.asyncio
async def test_get_pending_reviews(sessionmaker):
    async with sessionmaker() as session:
        review_repository = ReviewRepository(session)
        telegram_id = 123456789
        text = "This is a test review."

        await review_repository.create(telegram_id, text)
        pending_reviews = await review_repository.get_pending_reviews()

        assert isinstance(pending_reviews, list)
        assert len(pending_reviews) > 0
        assert all(review.status == "pending" for review in pending_reviews)


@pytest.mark.asyncio
async def test_update_review_status(sessionmaker):
    async with sessionmaker() as session:
        review_repository = ReviewRepository(session)
        telegram_id = 123456789
        text = "This is a test review."

        review = await review_repository.create(telegram_id, text)
        await review_repository.update_status(review.id, "approved")
        updated_review = await review_repository.get_by_id(review.id)

        assert isinstance(updated_review, Review)
        assert updated_review.id == review.id
        assert updated_review.status == "approved"


@pytest.mark.asyncio
async def test_get_count_by_user_today(sessionmaker):
    async with sessionmaker() as session:
        review_repository = ReviewRepository(session)
        telegram_id = 123456789
        text = "This is a test review."

        await review_repository.create(telegram_id, text)
        count = await review_repository.get_count_by_user_today(telegram_id)

        assert isinstance(count, int)
        assert count > 0


@pytest.mark.asyncio
async def test_delete_review_by_id(sessionmaker):
    async with sessionmaker() as session:
        review_repository = ReviewRepository(session)
        telegram_id = 123456789
        text = "This is a test review."

        review = await review_repository.create(telegram_id, text)
        await review_repository.delete_by_id(review.id)
        deleted_review = await review_repository.get_by_id(review.id)

        assert deleted_review is None


@pytest.mark.asyncio
async def test_create_review_empty_text(sessionmaker):
    async with sessionmaker() as session:
        review_repository = ReviewRepository(session)
        telegram_id = 123456789
        text = ""

        review = await review_repository.create(telegram_id, text)

        assert isinstance(review, Review)
        assert review.text == ""


@pytest.mark.asyncio
async def test_update_non_existent_review(sessionmaker):
    async with sessionmaker() as session:
        review_repository = ReviewRepository(session)

        result = await review_repository.update_status(9999, "approved")

        assert result is None or result is False


@pytest.mark.asyncio
async def test_get_count_by_user_today_empty(sessionmaker):
    async with sessionmaker() as session:
        review_repository = ReviewRepository(session)

        count = await review_repository.get_count_by_user_today(999)

        assert isinstance(count, int)
        assert count == 0


@pytest.mark.asyncio
async def test_get_all_reviews(sessionmaker):
    async with sessionmaker() as session:
        review_repository = ReviewRepository(session)
        telegram_id = 123456789
        text = "This is a test review."

        await review_repository.create(telegram_id, text)
        all_reviews = await review_repository.get_all_reviews()

        assert isinstance(all_reviews, list)
        assert len(all_reviews) > 0


@pytest.mark.asyncio
async def test_get_archived_reviews(sessionmaker):
    async with sessionmaker() as session:
        review_repository = ReviewRepository(session)
        telegram_id = 123456789
        text = "This is a test review."

        review = await review_repository.create(telegram_id, text)
        await review_repository.update_status(review.id, "reviewed")
        archived_reviews = await review_repository.get_archived_reviews()

        assert isinstance(archived_reviews, list)
        assert len(archived_reviews) > 0
        assert all(review.status == "reviewed" for review in archived_reviews)
