import asyncio
import os

import sentry_sdk
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import BotCommand
from aiohttp_socks._errors import ProxyTimeoutError
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from singbox2proxy import SingBoxProxy

from src.bot.core.config import BOT_PHOTO_PATH
from src.bot.database.connection import sessionmaker
from src.bot.handlers.callback import callback_router
from src.bot.handlers.command import command_router
from src.bot.handlers.message import message_router
from src.bot.messages.common import before_start_description, profile_description
from src.bot.middlewares.admin import AdminMiddleware
from src.bot.middlewares.album import AlbumMiddleware
from src.bot.middlewares.database import DatabaseSessionMiddleware
from src.bot.middlewares.grade import GradeMiddleware
from src.bot.middlewares.throttling import ThrottlingMiddleware
from src.bot.redis_client.client import r
from src.bot.services.throttling_service import ThrottlingService
from src.bot.services.update_changes_cache_service import (
    start_update_changes_cache_service,
)
from src.bot.utils.logger import Logger

logger = Logger(__name__).get_logger()

bot_commands = [
    BotCommand(command="start", description="👋 Приветственное сообщение"),
    BotCommand(command="schedule", description="📆 Расписание на неделю"),
    BotCommand(command="schedule_today", description="📅 Расписание на сегодня"),
    BotCommand(command="schedule_tomorrow", description="📅 Расписание на завтра"),
    BotCommand(command="bell", description="🔔 Время до звонка"),
    BotCommand(command="changes", description="🔄 Замены"),
    BotCommand(command="lesson", description="ℹ️ Информация о текущем уроке"),
    BotCommand(command="set_my_class", description="⚙️ Выбрать класс по умолчанию"),
    BotCommand(command="review", description="✍️ Оставить отзыв или идею"),
]


def init_sentry() -> None:
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        logger.info("SENTRY_DSN не найден. Запуск без мониторинга ошибок.")
        return

    sentry_sdk.init(
        dsn=dsn,
        integrations=[AioHttpIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True,
    )
    logger.info("Мониторинг Sentry успешно запущен")


async def setup_bot(bot: Bot) -> None:
    logger.info("Начата настройка бота")

    photo = types.InputProfilePhotoStatic(photo=types.FSInputFile(BOT_PHOTO_PATH))

    results = await asyncio.gather(
        bot.set_my_name("Расписание"),
        bot.set_my_description(before_start_description),
        bot.set_my_short_description(profile_description),
        bot.set_my_commands(bot_commands),
        bot.set_my_profile_photo(photo=photo),
        return_exceptions=True,
    )

    for result in results:
        if isinstance(result, Exception):
            logger.warning(result)

    logger.info("Настройка бота завершена")


async def start_bot(bot: Bot) -> None:
    logger.info("Бот запущен")
    dp = Dispatcher()

    dp.message.middleware(ThrottlingMiddleware(ThrottlingService(r)))
    dp.message.middleware(AdminMiddleware())

    database_session_middleware = DatabaseSessionMiddleware(sessionmaker)
    dp.message.middleware(database_session_middleware)
    dp.callback_query.middleware(database_session_middleware)

    dp.message.middleware(GradeMiddleware())
    dp.message.middleware(AlbumMiddleware())

    dp.include_router(command_router)
    dp.include_router(callback_router)
    dp.include_router(message_router)

    logger.info("Начата работа бота")
    await dp.start_polling(bot)


async def main() -> None:
    init_sentry()
    bot = None
    sing_box = None
    try:
        token = os.getenv("TOKEN")
        if not token:
            raise ValueError("Не найден токен бота в переменных окружения.")

        proxy = os.getenv("PROXY")
        vless_proxy = os.getenv("VLESS_PROXY")

        if proxy:
            logger.info("Запуск с иcпользованием proxy")
            session = AiohttpSession(proxy=proxy)

        elif vless_proxy:
            logger.info("Запуск с иcпользованием VLESS proxy")
            sing_box = SingBoxProxy(vless_proxy)

            if not sing_box.running:
                sing_box.start()

            session = AiohttpSession(proxy=sing_box.socks5_proxy_url)

        else:
            logger.info("Запуск без proxy")
            session = None

        bot = Bot(token, session, default=DefaultBotProperties(parse_mode="html"))
        await setup_bot(bot)
        await asyncio.gather(start_bot(bot), start_update_changes_cache_service(bot))

    except ProxyTimeoutError:
        logger.error("Не удалось подключиться к proxy.")
        raise

    finally:
        if sing_box and sing_box.running:
            sing_box.stop()
        if bot:
            await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
