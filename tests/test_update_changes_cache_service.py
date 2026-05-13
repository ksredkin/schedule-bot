import os
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

os.environ["DB_USER"] = "test_user"
os.environ["DB_PASSWORD"] = "test_password"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_NAME"] = "test_db"
os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6379"

from src.bot.services.update_changes_cache_service import (
    start_update_changes_cache_service,
)


@pytest.mark.asyncio
async def test_start_update_changes_cache_service_no_change(mocker):
    """Если изменений нет, service должен пройти цикл и остановиться на sleep."""
    bot = SimpleNamespace(send_message=AsyncMock())

    first_raw_rows = ["row1"]
    mocker.patch(
        "src.bot.services.update_changes_cache_service.get_changes_table_rows",
        side_effect=[first_raw_rows, first_raw_rows],
    )
    mocker.patch(
        "src.bot.services.update_changes_cache_service.get_changes_url",
        return_value="https://example.com/changes",
    )
    current_parsed = {"2026-05-13": {"10a": [{"lesson": "math"}]}}
    mocker.patch(
        "src.bot.services.update_changes_cache_service.parse_changes_table_rows",
        return_value=current_parsed,
    )

    set_changes_in_cache = AsyncMock()
    set_changes_url_in_cache = AsyncMock()
    get_changes_from_cache = AsyncMock(return_value=current_parsed)
    mocker.patch(
        "src.bot.services.update_changes_cache_service.cache_service.set_changes_in_cache",
        set_changes_in_cache,
    )
    mocker.patch(
        "src.bot.services.update_changes_cache_service.cache_service.set_changes_url_in_cache",
        set_changes_url_in_cache,
    )
    mocker.patch(
        "src.bot.services.update_changes_cache_service.cache_service.get_changes_from_cache",
        get_changes_from_cache,
    )

    mocker.patch(
        "src.bot.services.update_changes_cache_service.UserRepository.get_users",
        return_value=[],
    )

    sleep_mock = AsyncMock(side_effect=StopAsyncIteration)
    mocker.patch(
        "src.bot.services.update_changes_cache_service.asyncio.sleep",
        sleep_mock,
    )

    with pytest.raises(StopAsyncIteration):
        await start_update_changes_cache_service(bot)

    set_changes_in_cache.assert_called_once_with(current_parsed)
    set_changes_url_in_cache.assert_called_once_with("https://example.com/changes")
    get_changes_from_cache.assert_called_once()
    bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_start_update_changes_cache_service_sends_notifications(mocker):
    """Если данные изменились, сервис должен отправить уведомление пользователю."""
    bot = SimpleNamespace(send_message=AsyncMock())

    first_raw_rows = ["row1"]
    second_raw_rows = ["row2"]
    mocker.patch(
        "src.bot.services.update_changes_cache_service.get_changes_table_rows",
        side_effect=[first_raw_rows, second_raw_rows],
    )

    mocker.patch(
        "src.bot.services.update_changes_cache_service.get_changes_url",
        side_effect=["https://example.com/changes", "https://example.com/changes2"],
    )

    old_parsed = {"2026-05-13": {"10a": [{"lesson": "math"}]}}
    new_parsed = {"2026-05-13": {"10a": [{"lesson": "physics"}]}}
    mocker.patch(
        "src.bot.services.update_changes_cache_service.parse_changes_table_rows",
        side_effect=[old_parsed, new_parsed],
    )

    set_changes_in_cache = AsyncMock()
    set_changes_url_in_cache = AsyncMock()
    get_changes_from_cache = AsyncMock(return_value=old_parsed)
    get_changes_url_from_cache = AsyncMock(return_value="https://example.com/changes")
    mocker.patch(
        "src.bot.services.update_changes_cache_service.cache_service.set_changes_in_cache",
        set_changes_in_cache,
    )
    mocker.patch(
        "src.bot.services.update_changes_cache_service.cache_service.set_changes_url_in_cache",
        set_changes_url_in_cache,
    )
    mocker.patch(
        "src.bot.services.update_changes_cache_service.cache_service.get_changes_from_cache",
        get_changes_from_cache,
    )
    mocker.patch(
        "src.bot.services.update_changes_cache_service.cache_service.get_changes_url_from_cache",
        get_changes_url_from_cache,
    )

    user = AsyncMock()
    user.telegram_id = 123
    user.grade = "10a"
    mocker.patch(
        "src.bot.services.update_changes_cache_service.UserRepository.get_users",
        return_value=[user],
    )

    mocker.patch(
        "src.bot.services.update_changes_cache_service.get_changes_message",
        return_value="<b>Обновления</b>",
    )

    sleep_mock = AsyncMock(side_effect=StopAsyncIteration)
    mocker.patch(
        "src.bot.services.update_changes_cache_service.asyncio.sleep",
        sleep_mock,
    )

    with pytest.raises(StopAsyncIteration):
        await start_update_changes_cache_service(bot)

    bot.send_message.assert_called_once_with(
        123,
        "🔄 <b>Обновились замены!</b>\n\n<b>Обновления</b>",
        disable_web_page_preview=True,
    )
    assert set_changes_url_in_cache.call_count == 2
    assert set_changes_url_in_cache.call_args_list[-1] == (
        ("https://example.com/changes2",),
    )
    assert set_changes_in_cache.call_args_list[-1] == ((new_parsed,),)
