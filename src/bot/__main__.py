import asyncio
import os

import sentry_sdk
from maxapi import Bot, Dispatcher
from maxapi.types import BotCommand
#from maxapi.client.default import DefaultBotProperties
#from aiogram.client.session.aiohttp import AiohttpSession
#from aiogram.types import BotCommand
from aiohttp_socks._errors import ProxyTimeoutError
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

from src.bot.core.config import BOT_PHOTO_PATH
from src.bot.database.connection import sessionmaker
from src.bot.handlers.callback import callback_router
from src.bot.handlers.command import command_router
#from src.bot.handlers.message import message_router
from src.bot.messages.common import before_start_description, profile_description
#from src.bot.middlewares.admin import AdminMiddleware
#from src.bot.middlewares.album import AlbumMiddleware
from src.bot.middlewares.database import DatabaseSessionMiddleware
from maxapi.enums.http_method import HTTPMethod
from src.bot.middlewares.grade import GradeMiddleware
#from src.bot.middlewares.throttling import ThrottlingMiddleware
#from src.bot.redis_client.client import r
#from src.bot.services.throttling_service import ThrottlingService
#from src.bot.services.update_changes_cache_service import (
#    start_update_changes_cache_service,
#)
from maxapi.types import User
from maxapi.enums.parse_mode import ParseMode
from src.bot.utils.logger import Logger

from pydantic import BaseModel

logger = Logger(__name__).get_logger()

bot_commands = [
    BotCommand(name="start", description="👋 Приветственное сообщение"),
    BotCommand(name="schedule", description="📆 Расписание на неделю"),
    BotCommand(name="schedule_today", description="📅 Расписание на сегодня"),
    BotCommand(name="schedule_tomorrow", description="📅 Расписание на завтра"),
    BotCommand(name="bell", description="🔔 Время до звонка"),
    BotCommand(name="changes", description="🔄 Замены"),
    BotCommand(name="lesson", description="ℹ️ Информация о текущем уроке"),
    BotCommand(name="set_my_class", description="⚙️ Выбрать класс по умолчанию"),
    BotCommand(name="review", description="✍️ Оставить отзыв или идею"),
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


class BotCommandsResponse(BaseModel):
    commands: list[BotCommand] = []

async def setup_bot(bot: Bot) -> None:
    logger.info("Начата настройка бота")

    await bot.request(
        method=HTTPMethod.PATCH,
        path="/me/commands",
        model=BotCommandsResponse,
        json={"commands": [cmd.model_dump() for cmd in bot_commands]},
    )

    logger.info("Настройка бота завершена")


async def start_bot(bot: Bot) -> None:
    logger.info("Бот запущен")
    dp = Dispatcher()

    #dp.message.middleware(ThrottlingMiddleware(ThrottlingService(r)))
    #dp.message.middleware(AdminMiddleware())

    database_session_middleware = DatabaseSessionMiddleware(sessionmaker)
    dp.register_outer_middleware(database_session_middleware)
    #dp.callback_query.middleware(database_session_middleware)

    #dp.message.middleware(AlbumMiddleware())

    dp.include_routers(command_router, callback_router)
    #dp.routers.append(callback_router)
    #dp.routers.append(message_router)

    logger.info("Начата работа бота")
    await dp.start_polling(bot)


async def main() -> None:
    init_sentry()
    bot = None
    try:
        token = os.getenv("TOKEN")
        if not token:
            raise ValueError("Не найден токен бота в переменных окружения.")

        bot = Bot(token, parse_mode=ParseMode.HTML)
        await setup_bot(bot)
        await asyncio.gather(start_bot(bot)), #start_update_changes_cache_service(bot))

    except Exception:
        logger.error("Не удалось запустить бота.")
        raise

    finally:
        if bot:
            await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
