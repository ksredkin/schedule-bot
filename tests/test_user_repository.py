import os

os.environ["DB_USER"] = "test_user"
os.environ["DB_PASSWORD"] = "test_password"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_NAME"] = "test_db"

import pytest
from sqlalchemy.exc import IntegrityError

from src.bot.database.orm_models import User
from src.bot.repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_create_user(sessionmaker):
    async with sessionmaker() as session:
        user_repository = UserRepository(session)
        telegram_id = 123456789
        grade = "10A"

        user = await user_repository.create_user(telegram_id, grade)

        assert isinstance(user, User)
        assert user.telegram_id == telegram_id
        assert user.grade == grade.lower()


@pytest.mark.asyncio
async def test_create_existing_user(sessionmaker):
    async with sessionmaker() as session:
        user_repository = UserRepository(session)
        telegram_id = 123456789
        grade = "10A"

        user1 = await user_repository.create_user(telegram_id, grade)

        assert isinstance(user1, User)
        assert user1.telegram_id == telegram_id
        assert user1.grade == grade.lower()

        with pytest.raises(IntegrityError):
            await user_repository.create_user(telegram_id, grade)


@pytest.mark.asyncio
async def test_get_users(sessionmaker):
    async with sessionmaker() as session:
        user_repository = UserRepository(session)

        users1 = await user_repository.get_users()
        assert isinstance(users1, list)
        assert len(users1) == 0

        telegram_id = 123456789
        grade = "10A"

        user1 = await user_repository.create_user(telegram_id, grade)

        assert isinstance(user1, User)
        assert user1.telegram_id == telegram_id
        assert user1.grade == grade.lower()

        users2 = await user_repository.get_users()

        assert isinstance(users2, list)
        assert len(users2) == 1
        assert users2[0].telegram_id == user1.telegram_id
        assert users2[0].grade == user1.grade.lower()
        assert users2[0].id == user1.id


@pytest.mark.asyncio
async def test_get_user_by_telegram_id(sessionmaker):
    async with sessionmaker() as session:
        user_repository = UserRepository(session)

        telegram_id = 123456789
        grade = "10A"

        user1 = await user_repository.get_user_by_telegram_id(telegram_id)
        assert user1 is None

        user1 = await user_repository.create_user(telegram_id, grade)

        assert isinstance(user1, User)
        assert user1.telegram_id == telegram_id
        assert user1.grade == grade.lower()

        user2 = await user_repository.get_user_by_telegram_id(telegram_id)

        assert isinstance(user2, User)
        assert user2.telegram_id == user1.telegram_id
        assert user2.grade == user1.grade.lower()
        assert user2.id == user1.id


@pytest.mark.asyncio
async def test_update_user_grade(sessionmaker):
    async with sessionmaker() as session:
        user_repository = UserRepository(session)

        telegram_id = 123456789
        grade = "10A"

        user1 = await user_repository.create_user(telegram_id, grade)

        assert isinstance(user1, User)
        assert user1.telegram_id == telegram_id
        assert user1.grade == grade.lower()

        new_grade = "11А"

        user2 = await user_repository.update_user_grade(telegram_id, new_grade)

        assert isinstance(user2, User)
        assert user2.telegram_id == user1.telegram_id
        assert user2.grade == new_grade.lower()
        assert user2.id == user1.id


@pytest.mark.asyncio
async def test_update_invalid_user_grade(sessionmaker):
    async with sessionmaker() as session:
        user_repository = UserRepository(session)

        telegram_id = 123456789
        grade = "10A"

        user = await user_repository.update_user_grade(telegram_id, grade)

        assert user is None


@pytest.mark.asyncio
async def test_create_user_without_grade(sessionmaker):
    async with sessionmaker() as session:
        user_repository = UserRepository(session)
        telegram_id = 999

        user = await user_repository.create_user(telegram_id, None)

        assert isinstance(user, User)
        assert user.telegram_id == telegram_id
        assert user.grade is None


@pytest.mark.asyncio
async def test_get_total_users(sessionmaker):
    async with sessionmaker() as session:
        user_repository = UserRepository(session)

        no_users = await user_repository.get_total_users()

        assert no_users == 0

        telegram_id = 123
        user_grade = "11А"

        user = await user_repository.create_user(telegram_id, user_grade)

        assert user is not None
        assert isinstance(user, User)
        assert user.telegram_id == telegram_id
        assert user.grade == user_grade.lower()

        users = await user_repository.get_total_users()

        assert users == 1


@pytest.mark.asyncio
async def test_get_user_count_by_grades(sessionmaker):
    async with sessionmaker() as session:
        user_repository = UserRepository(session)

        no_users = await user_repository.get_user_count_by_grades()

        assert no_users == {}

        telegram_id = 123
        user_grade = "11А"

        user = await user_repository.create_user(telegram_id, user_grade)

        assert user is not None
        assert isinstance(user, User)
        assert user.telegram_id == telegram_id
        assert user.grade == user_grade.lower()

        users = await user_repository.get_user_count_by_grades()

        assert users == {"11а": 1}

        second_telegram_id = 456

        user = await user_repository.create_user(second_telegram_id, None)

        users = await user_repository.get_user_count_by_grades()

        assert users == {"11а": 1, "Не указан": 1}


@pytest.mark.asyncio
async def test_get_users_by_class(sessionmaker):
    async with sessionmaker() as session:
        user_repository = UserRepository(session)

        no_users = await user_repository.get_users_by_class("10A")

        assert no_users == []

        telegram_id = 123
        user_grade = "10A"

        user = await user_repository.create_user(telegram_id, user_grade)

        assert user is not None
        assert isinstance(user, User)
        assert user.telegram_id == telegram_id
        assert user.grade == user_grade.lower()

        users = await user_repository.get_users_by_class("10A")
        assert isinstance(users, list)
        assert len(users) == 1
        assert users[0].telegram_id == telegram_id
        assert users[0].grade == user_grade.lower()
