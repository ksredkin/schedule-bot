from aiogram import F, Router, types

from src.bot.repositories.user_repository import UserRepository
from src.bot.services.cache_service import cache_service
from src.bot.utils.logger import Logger

callback_router = Router()
logger = Logger(__name__).get_logger()


@callback_router.callback_query(F.data.startswith("set_my_class:"))
async def process_class(callback: types.CallbackQuery) -> None:
    callback_data = callback.data

    if not callback_data or not callback_data.startswith("set_my_class:"):
        return

    grade = callback_data.split(":")[1].lower()

    user = await UserRepository.get_user_by_telegram_id(callback.from_user.id)

    if not user:
        await UserRepository.create_user(callback.from_user.id, grade)
    else:
        await UserRepository.update_user_grade(callback.from_user.id, grade)

    await cache_service.set_user_class_in_cache(callback.from_user.id, grade)

    callback_message = callback.message
    if not callback_message or not hasattr(callback_message, "edit_text"):
        logger.warning("Получен callback без доступного сообщения для редактирования")
        return

    await callback_message.edit_text("✅ Ваш класс успешно обновлен!")


@callback_router.callback_query(F.data == "cancell")
async def cancell(callback: types.CallbackQuery) -> None:
    callback_message = callback.message
    if not callback_message or not hasattr(callback_message, "edit_text"):
        logger.warning("Получен callback без доступного сообщения для редактирования")
        return

    await callback_message.edit_text("✅ Обновление класса отменено!")
