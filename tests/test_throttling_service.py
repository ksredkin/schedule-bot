import os

os.environ["REDIS_PORT"] = "6379"
os.environ["REDIS_HOST"] = "localhost"

import asyncio

import pytest

from src.bot.services.throttling_service import ThrottlingService


@pytest.mark.asyncio
async def test_throttling_service_is_spaming(mocker, fake_redis):
    mocker.patch("src.bot.services.throttling_service.r", fake_redis)

    throttling_service = ThrottlingService(fake_redis)

    user_id = 123456789

    is_spam = await throttling_service.is_spaming(user_id)
    assert is_spam is False

    is_spam = await throttling_service.is_spaming(user_id)
    assert is_spam is True

    await asyncio.sleep(throttling_service.limit + 0.1)

    is_spam = await throttling_service.is_spaming(user_id)
    assert is_spam is False


@pytest.mark.asyncio
async def test_throttling_service_media_group_not_spam(mocker, fake_redis):
    mocker.patch("src.bot.services.throttling_service.r", fake_redis)

    throttling_service = ThrottlingService(fake_redis)

    user_id = 123456789
    media_group_id = "group123"

    is_spam = await throttling_service.is_spaming(user_id, media_group_id)
    assert is_spam is False

    is_spam = await throttling_service.is_spaming(user_id, media_group_id)
    assert is_spam is False

    is_spam = await throttling_service.is_spaming(user_id)
    assert is_spam is True
