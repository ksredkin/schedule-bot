import os

os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6379"


import pytest

from src.bot.services.cache_service import CacheService


@pytest.fixture
def cache_service(fake_redis):
    return CacheService(redis=fake_redis)


@pytest.mark.asyncio
async def test_set_and_get_basic(cache_service):
    """Проверка базовой записи и чтения из кэша."""
    await cache_service.set("test", "key", "value", expire=10)
    result = await cache_service.get("test", "key")
    assert result == "value"


@pytest.mark.asyncio
async def test_get_none_if_not_exists(cache_service):
    """Проверка возврата None, если ключа нет."""
    result = await cache_service.get("non", "existent")
    assert result is None


@pytest.mark.asyncio
async def test_sentinel_logic(cache_service):
    """Проверка логики NONE_SENTINEL (возврат False)."""
    # Эмулируем установку пустого значения для класса пользователя
    await cache_service.set_user_class_in_cache(12345, None)

    result = await cache_service.get_user_class_from_cache(12345)
    assert result is False


@pytest.mark.asyncio
async def test_image_cache(cache_service):
    """Тест кэширования ID изображений."""
    await cache_service.set_image_id_in_cache("bot_pic", "file_id_123")
    result = await cache_service.get_image_id_from_cache("bot_pic")
    assert result == "file_id_123"


@pytest.mark.asyncio
async def test_schedule_cache_json(cache_service):
    """Тест сериализации/десериализации расписания."""
    test_schedule = {"monday": {"1": {"subject": "Math", "room": "101"}}}
    await cache_service.set_schedule_in_cache("9А", test_schedule)

    result = await cache_service.get_schedule_from_cache("9а")  # Проверка upper()
    assert result == test_schedule


@pytest.mark.asyncio
async def test_changes_cache_json(cache_service):
    """Тест сериализации/десериализации замен."""
    test_changes = {"9А": {"lessons": [{"name": "Physics"}]}}
    await cache_service.set_changes_in_cache(test_changes)

    result = await cache_service.get_changes_from_cache()
    assert result == test_changes


@pytest.mark.asyncio
async def test_invalid_json_handling(cache_service, fake_redis):
    """Проверка поведения при битом JSON в Redis."""
    # Записываем невалидный JSON напрямую в Redis
    await fake_redis.set("schedule:10Б", "invalid_json{")

    result = await cache_service.get_schedule_from_cache("10Б")

    # Должен вернуть None и удалить ключ
    assert result is None
    exists = await fake_redis.get("schedule:10Б")
    assert exists is None


@pytest.mark.asyncio
async def test_set_user_class_real_value(cache_service):
    """Проверка сохранения реального класса (не None)."""
    await cache_service.set_user_class_in_cache(555, "11Б")
    result = await cache_service.get_user_class_from_cache(555)
    assert result == "11Б"
