import html

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.core.config import MAX_REVIEWS_PER_USER_PER_DAY
from src.bot.messages.common import after_review_message, too_many_reviews_message
from src.bot.repositories.review_repository import ReviewRepository
from src.bot.states.review_states import ReviewCreate, ReviewReply
from src.bot.utils.logger import Logger

message_router = Router()
logger = Logger(__name__).get_logger()


@message_router.message(ReviewCreate.waiting_for_review, F.text)
async def handle_message(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        logger.warning("Получено сообщение без информации о пользователе")
        return

    count = await ReviewRepository.get_count_by_user_today(message.from_user.id)
    if count >= MAX_REVIEWS_PER_USER_PER_DAY:
        await message.answer(too_many_reviews_message)
        await state.clear()
        return

    review = await ReviewRepository.create(
        telegram_id=message.from_user.id, text=str(message.text)
    )

    if not review:
        logger.error("Не удалось создать отзыв")
        await message.answer(
            "Извините, произошла ошибка при создании отзыва. Пожалуйста, попробуйте позже."
        )
        await state.clear()
        return

    logger.info(
        f"Пользователь @{message.from_user.username} с id {message.from_user.id} оставил отзыв с id {review.id}"
    )

    await message.answer(after_review_message)
    await state.clear()


@message_router.message(
    F.text, ReviewReply.waiting_for_reply_text, flags={"need_admin": True}
)
async def handle_reply_message(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        logger.warning("Получено сообщение без информации о пользователе")
        return

    data = await state.get_data()
    review_id = data.get("selected_review_id")

    if not review_id:
        logger.error("Не удалось получить ID отзыва")
        await message.answer(
            "Извините, произошла ошибка. Пожалуйста, попробуйте позже."
        )
        await state.clear()
        return

    review = await ReviewRepository.get_by_id(review_id)
    if not review:
        logger.error(f"Отзыв с id {review_id} не найден")
        await message.answer("Извините, отзыв не найден. Пожалуйста, попробуйте позже.")
        await state.clear()
        return

    bot = message.bot

    if not bot:
        logger.error("Не удалось получить экземпляр бота")
        await message.answer(
            "Извините, произошла ошибка. Пожалуйста, попробуйте позже."
        )
        await state.clear()
        return

    await bot.send_message(
        chat_id=int(review.telegram_id),
        text=f"""<b>📩 Ответ от администратора на ваш отзыв:</b>

<b>Текст отзыва:</b> {html.escape(str(review.text))}

<b>Ответ администратора:</b> {html.escape(str(message.text))}""",
    )

    logger.info(
        f"Пользователь @{message.from_user.username} с id {message.from_user.id} оставил ответ на отзыв с id {review_id}"
    )

    await message.answer("✅ Ответ на отзыв отправлен.")
    await state.clear()
