import os
from unittest.mock import AsyncMock, patch

os.environ["REDIS_PORT"] = "6379"
os.environ["REDIS_HOST"] = "localhost"

import pytest

from src.bot.middlewares.admin import AdminMiddleware


@pytest.mark.asyncio
async def test_admin_middleware_allows_admin_user(monkeypatch):
    monkeypatch.setenv("ADMIN_ID", "123")

    middleware = AdminMiddleware()

    handler = AsyncMock(return_value="success")
    message = AsyncMock()
    message.from_user.id = 123
    message.from_user.username = "admin_user"

    data = {}

    with patch("src.bot.middlewares.admin.get_flag", return_value=True):
        result = await middleware(handler, message, data)

    handler.assert_called_once()
    assert result == "success"


@pytest.mark.asyncio
async def test_admin_middleware_blocks_non_admin_user(monkeypatch):
    monkeypatch.setenv("ADMIN_ID", "123")

    middleware = AdminMiddleware()

    handler = AsyncMock()
    message = AsyncMock()
    message.from_user.id = 456
    message.from_user.username = "regular_user"

    data = {}

    with patch("src.bot.middlewares.admin.get_flag", return_value=True):
        result = await middleware(handler, message, data)

    handler.assert_not_called()
    assert result is None


@pytest.mark.asyncio
async def test_admin_middleware_no_admin_id_env(monkeypatch):
    monkeypatch.delenv("ADMIN_ID", raising=False)

    middleware = AdminMiddleware()

    handler = AsyncMock()
    message = AsyncMock()
    message.from_user.id = 123

    data = {}

    with patch("src.bot.middlewares.admin.get_flag", return_value=True):
        result = await middleware(handler, message, data)

    handler.assert_not_called()
    assert result is None


@pytest.mark.asyncio
async def test_admin_middleware_skips_non_admin_commands(monkeypatch):
    monkeypatch.setenv("ADMIN_ID", "123")

    middleware = AdminMiddleware()

    handler = AsyncMock(return_value="ok")
    message = AsyncMock()
    message.from_user.id = 456

    data = {}

    with patch("src.bot.middlewares.admin.get_flag", return_value=False):
        result = await middleware(handler, message, data)

    handler.assert_called_once()
    assert result == "ok"
