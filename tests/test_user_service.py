import os

os.environ["REDIS_PORT"] = "6379"
os.environ["REDIS_HOST"] = "localhost"

from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest

from src.bot.core.exceptions import (
    GradeNotFoundError,
    GradeNotSelectedError,
    InvalidCommandError,
)


@pytest.mark.asyncio
async def test_resolve_grade_from_cache(mocker: Any) -> None:
    from src.bot.services.user_service import resolve_grade

    mock = AsyncMock()
    mock.get_user_class_from_cache.return_value = "10а"

    mocker.patch(
        "src.bot.services.user_service.cache_service",
        mock,
    )

    repo = AsyncMock()
    repo.get_user_by_telegram_id.return_value = "10А"

    message = AsyncMock()
    message.text = "/command"
    message.from_user.id = 12345

    result = await resolve_grade(message, repo, "command")

    assert result == "10а"


@pytest.mark.asyncio
async def test_resolve_grade_with_none_sentinel_cache(mocker: Any) -> None:
    from src.bot.services.user_service import resolve_grade

    mock = AsyncMock()
    mock.get_user_class_from_cache.return_value = None

    mocker.patch(
        "src.bot.services.user_service.cache_service",
        mock,
    )

    repo = AsyncMock()
    repo.get_user_by_telegram_id.return_value = None

    message = AsyncMock()
    message.text = "/command"
    message.from_user.id = 12345

    with pytest.raises(GradeNotSelectedError):
        await resolve_grade(message, repo, "command")


@pytest.mark.asyncio
async def test_resolve_grade_from_database(mocker: Any) -> None:
    from src.bot.services.user_service import resolve_grade

    mock = AsyncMock()
    mock.get_user_class_from_cache.return_value = None
    mock.set_user_class_in_cache.return_value = lambda telegram_id, grade: None

    mocker.patch(
        "src.bot.services.user_service.cache_service",
        mock,
    )

    repo = AsyncMock()
    user = Mock()
    user.grade = "10А"
    repo.get_user_by_telegram_id.return_value = user

    message = AsyncMock()
    message.text = "/command"
    message.from_user.id = 12345

    result = await resolve_grade(message, repo, "command")

    assert result == "10А"


@pytest.mark.asyncio
async def test_resolve_grade_with_no_message(mocker: Any) -> None:
    from src.bot.services.user_service import resolve_grade

    mock = AsyncMock()
    mock.get_user_class_from_cache.return_value = None
    mock.set_user_class_in_cache.return_value = lambda telegram_id, grade: None

    mocker.patch(
        "src.bot.services.user_service.cache_service",
        mock,
    )

    repo = AsyncMock()
    user = Mock()
    user.grade = "10А"
    repo.get_user_by_telegram_id.return_value = user

    result = await resolve_grade(None, repo, "command")

    assert result is None


@pytest.mark.asyncio
async def test_resolve_grade_with_no_message_text(mocker: Any) -> None:
    from src.bot.services.user_service import resolve_grade

    mock = AsyncMock()
    mock.get_user_class_from_cache.return_value = None
    mock.set_user_class_in_cache.return_value = lambda telegram_id, grade: None

    mocker.patch(
        "src.bot.services.user_service.cache_service",
        mock,
    )

    repo = AsyncMock()
    user = Mock()
    user.grade = "10А"
    repo.get_user_by_telegram_id.return_value = user

    message = AsyncMock()
    message.text = None
    message.from_user.id = 12345

    result = await resolve_grade(message, repo, "command")

    assert result is None


@pytest.mark.asyncio
async def test_resolve_grade_with_no_message_from_user(mocker: Any) -> None:
    from src.bot.services.user_service import resolve_grade

    mock = AsyncMock()
    mock.get_user_class_from_cache.return_value = None
    mock.set_user_class_in_cache.return_value = lambda telegram_id, grade: None

    mocker.patch(
        "src.bot.services.user_service.cache_service",
        mock,
    )

    repo = AsyncMock()
    user = Mock()
    user.grade = "10А"
    repo.get_user_by_telegram_id.return_value = user

    message = AsyncMock()
    message.text = "/command"
    message.from_user = None

    result = await resolve_grade(message, repo, "command")

    assert result is None


@pytest.mark.asyncio
async def test_resolve_grade_with_class_in_message(mocker: Any) -> None:
    from src.bot.services.user_service import resolve_grade

    mock = AsyncMock()
    mock.get_user_class_from_cache.return_value = None

    mocker.patch(
        "src.bot.services.user_service.cache_service",
        mock,
    )

    repo = AsyncMock()
    user = Mock()
    user.grade = "10А"
    repo.get_user_by_telegram_id.return_value = user

    message = AsyncMock()
    message.text = "/command 8 ТЕХ"
    message.from_user = 12345

    result = await resolve_grade(message, repo, "command")

    assert result == "8 ТЕХ"


@pytest.mark.asyncio
async def test_resolve_grade_with_invalid_class_in_message(mocker: Any) -> None:
    from src.bot.services.user_service import resolve_grade

    mock = AsyncMock()
    mock.get_user_class_from_cache.return_value = None

    mocker.patch(
        "src.bot.services.user_service.cache_service",
        mock,
    )

    repo = AsyncMock()
    user = Mock()
    user.grade = "10А"
    repo.get_user_by_telegram_id.return_value = user

    message = AsyncMock()
    message.text = "/command 9Ь"
    message.from_user = 12345

    with pytest.raises(GradeNotFoundError):
        await resolve_grade(message, repo, "command")


@pytest.mark.asyncio
async def test_resolve_grade_with_invalid_text_in_message(mocker: Any) -> None:
    from src.bot.services.user_service import resolve_grade

    mock = AsyncMock()
    mock.get_user_class_from_cache.return_value = None

    mocker.patch(
        "src.bot.services.user_service.cache_service",
        mock,
    )

    repo = AsyncMock()
    user = Mock()
    user.grade = "10А"
    repo.get_user_by_telegram_id.return_value = user

    message = AsyncMock()
    message.text = "/command информатика лучше музыки"
    message.from_user = 12345

    with pytest.raises(InvalidCommandError):
        await resolve_grade(message, repo, "command")
