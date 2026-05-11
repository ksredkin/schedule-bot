import asyncio
import os
import subprocess
import sys

import sentry_sdk
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import BotCommand
from aiohttp_socks._errors import ProxyTimeoutError
from dotenv import load_dotenv
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from singbox2proxy import SingBoxProxy

from src.bot.core.config import BOT_PHOTO_PATH
from src.bot.handlers.callback import callback_router
from src.bot.handlers.command import command_router
from src.bot.handlers.message import message_router
from src.bot.messages.common import before_start_description, profile_description
from src.bot.middlewares.admin import AdminMiddleware
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

    try:
        await bot.set_my_name("Расписание")
        logger.info("Имя бота обновлено")
    except Exception as e:
        logger.warning(f"Не удалось настроить имя бота: {e}")

    try:
        await bot.set_my_description(before_start_description)
        logger.info("Описание бота до start обновлено")
    except Exception as e:
        logger.warning(f"Не удалось настроить описание до start бота: {e}")

    try:
        await bot.set_my_short_description(profile_description)
        logger.info("Описание бота обновлено")
    except Exception as e:
        logger.warning(f"Не удалось настроить описание бота: {e}")

    try:
        await bot.set_my_commands(bot_commands)
        logger.info("Команды бота обновлены")
    except Exception as e:
        logger.warning(f"Не удалось настроить команды бота: {e}")

    try:
        photo = types.InputProfilePhotoStatic(photo=types.FSInputFile(BOT_PHOTO_PATH))
        await bot.set_my_profile_photo(photo=photo)
        logger.info("Фото бота обновлено")
    except Exception as e:
        logger.warning(f"Не удалось настроить фото бота: {e}")

    logger.info("Настройка бота завершена")


async def start_bot(bot: Bot) -> None:
    try:
        logger.info("Бот запущен")
        load_dotenv()

        subprocess.run(["alembic", "upgrade", "head"])
        # await setup_bot(bot)

        dp = Dispatcher()

        throttling_service = ThrottlingService(r)
        dp.message.middleware(ThrottlingMiddleware(throttling_service))

        dp.message.middleware(AdminMiddleware())
        dp.message.middleware(GradeMiddleware())

        dp.include_router(command_router)
        dp.include_router(callback_router)
        dp.include_router(message_router)

        logger.info("Начата работа бота")
        await dp.start_polling(bot)

    except Exception as e:
        logger.critical(f"Работа бота остановлена: {e}")
        sys.exit(1)


async def main() -> None:
    init_sentry()
    try:
        token = os.getenv("TOKEN")
        if not isinstance(token, str):
            logger.critical("Не найден токен бота в переменных окружения.")
            sys.exit(1)

        if os.getenv("PROXY"):
            logger.info("Запуск с ипользованием proxy")
            session = AiohttpSession(proxy=os.getenv("PROXY"))
            bot = Bot(token, session, DefaultBotProperties(parse_mode="html"))

        elif os.getenv("VLESS_PROXY"):
            logger.info("Запуск с ипользованием VLESS proxy")
            proxy = SingBoxProxy(os.getenv("VLESS_PROXY"))

            if not proxy.running:
                proxy.start()

            session = AiohttpSession(proxy=proxy.socks5_proxy_url)
            bot = Bot(token, session, DefaultBotProperties(parse_mode="html"))

        else:
            logger.info("Запуск без proxy")
            bot = Bot(token, default=DefaultBotProperties(parse_mode="html"))

        bot_service = asyncio.create_task(start_bot(bot))
        update_changes_cache_service = asyncio.create_task(
            start_update_changes_cache_service(bot)
        )
        await bot_service
        await update_changes_cache_service

    except ProxyTimeoutError:
        logger.critical("Не удалось подключиться к proxy.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
