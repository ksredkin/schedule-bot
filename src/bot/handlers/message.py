import html

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputMediaPhoto, InputMediaVideo

from src.bot.core.config import MAX_REVIEWS_PER_USER_PER_DAY
from src.bot.messages.common import after_review_message, too_many_reviews_message
from src.bot.repositories.review_repository import ReviewRepository
from src.bot.states.review_states import ReviewCreate, ReviewReply
from src.bot.states.broadcast_states import BroadcastAll, BroadcastClass
from src.bot.utils.logger import Logger
from src.bot.repositories.user_repository import UserRepository
import os
import asyncio

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


@message_router.message(BroadcastAll.waiting_for_message, flags={"need_admin": True, "need_album": True})
async def handle_broadcast_all_message(message: Message, state: FSMContext, album: list[Message] = []) -> None:
    if not message.from_user:
        logger.warning("Получено сообщение без информации о пользователе")
        return
    
    await state.clear()

    media_group = []
    text = ""
    
    if album:
        for msg in album:
            if msg.caption:
                text = msg.caption
            
            if msg.photo:
                media_group.append(InputMediaPhoto(media=msg.photo[-1].file_id))
            elif msg.video:
                media_group.append(InputMediaVideo(media=msg.video.file_id))
        
        if media_group and text:
            media_group[0].caption = text
    else:
        text = message.text or message.caption or ""
        if message.photo:
            media_group.append(InputMediaPhoto(media=message.photo[-1].file_id, caption=text))
        elif message.video:
            media_group.append(InputMediaVideo(media=message.video.file_id, caption=text))

    users = await UserRepository.get_users()
    admin_id = os.getenv("ADMIN_ID")
    admin_id = int(admin_id) if admin_id else None

    bot = message.bot
    if not bot:
        logger.error("Не удалось получить экземпляр бота")
        await message.answer(
            "Извините, произошла ошибка. Пожалуйста, попробуйте позже."
        )
        return
    elif not users or len(users) == 1 and users[0].id == admin_id:
        await message.answer("⚠️ Нет пользователей для рассылки.")
        return

    await message.answer("✅ Сообщение для рассылки принято. Начинаю отправку...")

    for user in users:
        try:
            telegram_id = int(user.telegram_id) if user.telegram_id else None
            if not telegram_id:
                logger.warning(f"Пользователь с id {user.id} не имеет telegram_id, пропускаю")
                continue
            elif telegram_id == int(admin_id):
                continue

            if media_group:
                if len(media_group) > 1:
                    await message.bot.send_media_group(chat_id=user.telegram_id, media=media_group)
                elif message.photo:
                    await message.bot.send_photo(chat_id=user.telegram_id, photo=media_group[0].media, caption=text)
                elif message.video:
                    await message.bot.send_video(chat_id=user.telegram_id, video=media_group[0].media, caption=text)
            else:
                await message.bot.send_message(chat_id=user.telegram_id, text=text)
            
            await asyncio.sleep(0.05)
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения пользователю {user.telegram_id}: {e}")

    logger.info(
        f"Пользователь @{message.from_user.username} с id {message.from_user.id} отправил рассылку c {len(media_group)} медиа: {text[:100]}{'...' if len(text) > 100 else ''}"
    )

@message_router.message(BroadcastClass.waiting_for_message, flags={"need_admin": True, "need_album": True})
async def handle_broadcast_class_message(message: Message, state: FSMContext, album: list[Message] = []) -> None:
    if not message.from_user:
        logger.warning("Получено сообщение без информации о пользователе")
        return
    
    await state.clear()
    data = await state.get_data()
    grade = data.get("grade")

    media_group = []
    text = ""
    
    if album:
        for msg in album:
            if msg.caption:
                text = msg.caption
            
            if msg.photo:
                media_group.append(InputMediaPhoto(media=msg.photo[-1].file_id))
            elif msg.video:
                media_group.append(InputMediaVideo(media=msg.video.file_id))
        
        if media_group and text:
            media_group[0].caption = text
    else:
        text = message.text or message.caption or ""
        if message.photo:
            media_group.append(InputMediaPhoto(media=message.photo[-1].file_id, caption=text))
        elif message.video:
            media_group.append(InputMediaVideo(media=message.video.file_id, caption=text))

    users = await UserRepository.get_users_by_class(grade)
    admin_id = os.getenv("ADMIN_ID")
    admin_id = int(admin_id) if admin_id else None

    bot = message.bot
    if not bot:
        logger.error("Не удалось получить экземпляр бота")
        await message.answer(
            "Извините, произошла ошибка. Пожалуйста, попробуйте позже."
        )
        return
    elif not users or len(users) == 1 and users[0].id == admin_id:
        await message.answer("⚠️ Нет пользователей для рассылки.")
        return

    await message.answer("✅ Сообщение для рассылки принято. Начинаю отправку...")

    for user in users:
        try:
            telegram_id = int(user.telegram_id) if user.telegram_id else None
            if not telegram_id:
                logger.warning(f"Пользователь с id {user.id} не имеет telegram_id, пропускаю")
                continue
            elif telegram_id == int(admin_id):
                continue

            if media_group:
                if len(media_group) > 1:
                    await message.bot.send_media_group(chat_id=user.telegram_id, media=media_group)
                elif message.photo:
                    await message.bot.send_photo(chat_id=user.telegram_id, photo=media_group[0].media, caption=text)
                elif message.video:
                    await message.bot.send_video(chat_id=user.telegram_id, video=media_group[0].media, caption=text)
            else:
                await message.bot.send_message(chat_id=user.telegram_id, text=text)
            
            await asyncio.sleep(0.05)
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения пользователю {user.telegram_id}: {e}")

    logger.info(
        f"Пользователь @{message.from_user.username} с id {message.from_user.id} отправил рассылку c {len(media_group)} медиа: {text[:100]}{'...' if len(text) > 100 else ''}"
    )