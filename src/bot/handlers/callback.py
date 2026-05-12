import html

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from src.bot.keyboards.inline import (
    create_cancell_inline_keyboard,
    create_inline_keyboard,
)
from src.bot.repositories.review_repository import ReviewRepository
from src.bot.repositories.user_repository import UserRepository
from src.bot.services.cache_service import cache_service
from src.bot.states.broadcast_states import BroadcastAll, BroadcastClass
from src.bot.states.review_states import ReviewReply
from src.bot.utils.constants import classes
from src.bot.utils.formatters import get_admin_panel_message
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

    await callback_message.edit_text("✅ Действие отменено!")


@callback_router.callback_query(F.data == "get_admin_panel", flags={"need_admin": True})
async def get_admin_panel(callback: types.CallbackQuery) -> None:
    if (
        not callback.from_user
        or not callback.message
        or not hasattr(callback.message, "edit_text")
        or not callback.data
    ):
        logger.warning("Получен некорректный callback")
        return

    logger.info(
        f"Пользователь @{callback.from_user.username} с id {callback.from_user.id} вызвал команду /admin"
    )

    total_users = await UserRepository().get_total_users()
    user_count_by_grades = await UserRepository().get_user_count_by_grades()

    reviews = await ReviewRepository.get_pending_reviews()
    reviews_count = len(reviews) if reviews else 0
    archived_reviews = await ReviewRepository.get_archived_reviews()
    archived_reviews_count = len(archived_reviews) if archived_reviews else 0

    buttons = {
        f"🔔 Активные отзывы ({reviews_count})": "get_pending_reviews",
        f"🗄 Архивные отзывы ({archived_reviews_count})": "get_archived_reviews",
        "📢 Рассылка всем": "broadcast_all",
        "📋 Рассылка классу": "broadcast_class",
    }

    await callback.message.edit_text(
        get_admin_panel_message(total_users, user_count_by_grades),
        reply_markup=create_inline_keyboard(buttons),
    )
    logger.info(
        f"Пользователь @{callback.from_user.username} с id {callback.from_user.id} получил админ-панель"
    )


@callback_router.callback_query(
    F.data == "get_pending_reviews", flags={"need_admin": True}
)
async def get_pending_reviews(callback: types.CallbackQuery) -> None:
    if (
        not callback.from_user
        or not callback.message
        or not hasattr(callback.message, "edit_text")
        or not callback.data
    ):
        logger.warning("Получен некорректный callback")
        return

    pending_reviews = await ReviewRepository().get_pending_reviews()

    if not pending_reviews:
        buttons = {"🔙 Назад": "get_admin_panel"}
        await callback.message.edit_text(
            "✅ Нет активных отзывов для рассмотрения.",
            reply_markup=create_inline_keyboard(buttons),
        )
        logger.info(
            f"Пользователь @{callback.from_user.username} с id {callback.from_user.id} получил сообщение об отсутствии активных отзывов для рассмотрения"
        )
        return

    buttons = {
        f"• ({review.created_at.strftime('%y-%m-%d %H:%M:%S')}) {review.text[:18]}"
        + "..."
        if len(review.text) > 18
        else f"• {review.text}": f"select_review:{review.id}"
        for review in pending_reviews
    }
    buttons = {**buttons, "🔙 Назад": "get_admin_panel"}

    await callback.message.edit_text(
        "🔔 Активные отзывы для рассмотрения:",
        reply_markup=create_inline_keyboard(buttons),
    )
    logger.info(
        f"Пользователь @{callback.from_user.username} с id {callback.from_user.id} получил список активных отзывов для рассмотрения"
    )


@callback_router.callback_query(
    F.data.startswith("select_review"), flags={"need_admin": True}
)
async def select_review(callback: types.CallbackQuery) -> None:
    if (
        not callback.from_user
        or not callback.message
        or not hasattr(callback.message, "edit_text")
        or not callback.data
    ):
        logger.warning("Получен некорректный callback")
        return

    selected_review_id = int(callback.data.split(":")[1])

    review = await ReviewRepository().get_by_id(selected_review_id)

    if not review:
        buttons = {"🔙 Назад": "get_pending_reviews"}
        await callback.message.edit_text(
            "🚫 Отзыв не найден.", reply_markup=create_inline_keyboard(buttons)
        )
        logger.warning(
            f"Пользователь @{callback.from_user.username} с id {callback.from_user.id} попытался выбрать отзыв с id {selected_review_id}, но он не был найден"
        )
        return

    text = f"""<b>Отзыв №{review.id}</b>

От: {review.telegram_id}
Дата: {review.created_at.strftime("%Y-%m-%d %H:%M:%S")}

{html.escape(str(review.text))}"""

    buttons = {
        "✅ Прочитано": f"mark_reviewed:{review.id}",
        "🗑 Удалить": f"delete_review:{review.id}",
        "💬 Ответить": f"reply_review:{review.id}",
        "🔙 К списку": "get_pending_reviews",
    }

    await callback.message.edit_text(
        text, reply_markup=create_inline_keyboard(buttons, [3, 1])
    )
    logger.info(
        f"Пользователь @{callback.from_user.username} с id {callback.from_user.id} получил информацию об отзыве"
    )


@callback_router.callback_query(
    F.data.startswith("mark_reviewed"), flags={"need_admin": True}
)
async def mark_reviewed(callback: types.CallbackQuery) -> None:
    if (
        not callback.from_user
        or not callback.message
        or not hasattr(callback.message, "edit_text")
        or not callback.data
    ):
        logger.warning("Получен некорректный callback")
        return

    review_id = int(callback.data.split(":")[1])

    await ReviewRepository().update_status(review_id, "reviewed")

    buttons = {"🔙 К списку": "get_pending_reviews"}
    await callback.message.edit_text(
        "✅ Отзыв помечен как прочитанный.",
        reply_markup=create_inline_keyboard(buttons),
    )
    logger.info(
        f"Пользователь @{callback.from_user.username} с id {callback.from_user.id} пометил отзыв с id {review_id} как прочитанный"
    )


@callback_router.callback_query(
    F.data.startswith("delete_review"), flags={"need_admin": True}
)
async def delete_review(callback: types.CallbackQuery) -> None:
    if (
        not callback.from_user
        or not callback.message
        or not hasattr(callback.message, "edit_text")
        or not callback.data
    ):
        logger.warning("Получен некорректный callback")
        return

    review_id = int(callback.data.split(":")[1])

    await ReviewRepository().delete_by_id(review_id)

    buttons = {"🔙 К списку": "get_pending_reviews"}
    await callback.message.edit_text(
        "✅ Отзыв удален.", reply_markup=create_inline_keyboard(buttons)
    )
    logger.info(
        f"Пользователь @{callback.from_user.username} с id {callback.from_user.id} удалил отзыв с id {review_id}"
    )


@callback_router.callback_query(
    F.data.startswith("reply_review"), flags={"need_admin": True}
)
async def reply_review(callback: types.CallbackQuery, state: FSMContext) -> None:
    if (
        not callback.from_user
        or not callback.message
        or not hasattr(callback.message, "edit_text")
        or not callback.data
    ):
        logger.warning("Получен некорректный callback")
        return

    review_id = int(callback.data.split(":")[1])

    await state.update_data(selected_review_id=review_id)
    await state.set_state(ReviewReply.waiting_for_reply_text)

    await callback.message.edit_text(
        "✍️ Напишите ответ на отзыв:", reply_markup=create_cancell_inline_keyboard({})
    )
    logger.info(
        f"Пользователь @{callback.from_user.username} с id {callback.from_user.id} начал отвечать на отзыв с id {review_id}"
    )


@callback_router.callback_query(
    F.data == "get_archived_reviews", flags={"need_admin": True}
)
async def get_archived_reviews(callback: types.CallbackQuery) -> None:
    if (
        not callback.from_user
        or not callback.message
        or not hasattr(callback.message, "edit_text")
        or not callback.data
    ):
        logger.warning("Получен некорректный callback")
        return

    archived_reviews = await ReviewRepository.get_archived_reviews()

    if not archived_reviews:
        buttons = {"🔙 Назад": "get_admin_panel"}
        await callback.message.edit_text(
            "✅ Нет архивных отзывов.", reply_markup=create_inline_keyboard(buttons)
        )
        logger.info(
            f"Пользователь @{callback.from_user.username} с id {callback.from_user.id} получил сообщение об отсутствии архивных отзывов"
        )
        return

    text = "🗄 Архивные отзывы:"

    buttons = {
        f"• ({review.created_at.strftime('%y-%m-%d %H:%M:%S')}) {review.text[:18]}"
        + "..."
        if len(review.text) > 18
        else f"• {review.text}": f"select_archived_review:{review.id}"
        for review in archived_reviews
    }
    buttons = {**buttons, "🔙 Назад": "get_admin_panel"}

    await callback.message.edit_text(text, reply_markup=create_inline_keyboard(buttons))
    logger.info(
        f"Пользователь @{callback.from_user.username} с id {callback.from_user.id} получил список архивных отзывов"
    )


@callback_router.callback_query(
    F.data.startswith("select_archived_review"), flags={"need_admin": True}
)
async def select_archived_review(callback: types.CallbackQuery) -> None:
    if (
        not callback.from_user
        or not callback.message
        or not hasattr(callback.message, "edit_text")
        or not callback.data
    ):
        logger.warning("Получен некорректный callback")
        return

    selected_review_id = int(callback.data.split(":")[1])

    review = await ReviewRepository().get_by_id(selected_review_id)

    if not review:
        buttons = {"🔙 Назад": "get_archived_reviews"}
        await callback.message.edit_text(
            "🚫 Отзыв не найден.", reply_markup=create_inline_keyboard(buttons)
        )
        logger.warning(
            f"Пользователь @{callback.from_user.username} с id {callback.from_user.id} попытался выбрать архивный отзыв с id {selected_review_id}, но он не был найден"
        )
        return

    text = f"""<b>Отзыв №{review.id}</b>

От: {review.telegram_id}
Дата: {review.created_at.strftime("%Y-%m-%d %H:%M:%S")}

{html.escape(str(review.text))}"""

    buttons = {
        "↩️ Вернуть": f"restore_archived_review:{review.id}",
        "🗑 Удалить": f"delete_archived_review:{review.id}",
        "🔙 Назад": "get_archived_reviews",
    }
    await callback.message.edit_text(text, reply_markup=create_inline_keyboard(buttons))
    logger.info(
        f"Пользователь @{callback.from_user.username} с id {callback.from_user.id} выбрал архивный отзыв с id {selected_review_id}"
    )


@callback_router.callback_query(
    F.data.startswith("restore_archived_review"), flags={"need_admin": True}
)
async def restore_archived_review(callback: types.CallbackQuery) -> None:
    if (
        not callback.from_user
        or not callback.message
        or not hasattr(callback.message, "edit_text")
        or not callback.data
    ):
        logger.warning("Получен некорректный callback")
        return

    review_id = int(callback.data.split(":")[1])

    await ReviewRepository().update_status(review_id, "pending")

    buttons = {"🔙 К списку": "get_archived_reviews"}
    await callback.message.edit_text(
        "✅ Отзыв восстановлен в список активных.",
        reply_markup=create_inline_keyboard(buttons),
    )
    logger.info(
        f"Пользователь @{callback.from_user.username} с id {callback.from_user.id} восстановил отзыв с id {review_id} из архива"
    )


@callback_router.callback_query(
    F.data.startswith("delete_archived_review"), flags={"need_admin": True}
)
async def delete_archived_review(callback: types.CallbackQuery) -> None:
    if (
        not callback.from_user
        or not callback.message
        or not hasattr(callback.message, "edit_text")
        or not callback.data
    ):
        logger.warning("Получен некорректный callback")
        return

    review_id = int(callback.data.split(":")[1])

    await ReviewRepository().delete_by_id(review_id)

    buttons = {"🔙 К списку": "get_archived_reviews"}
    await callback.message.edit_text(
        "✅ Отзыв удален из архива.", reply_markup=create_inline_keyboard(buttons)
    )
    logger.info(
        f"Пользователь @{callback.from_user.username} с id {callback.from_user.id} удалил отзыв с id {review_id} из архива"
    )


@callback_router.callback_query(F.data == "broadcast_all", flags={"need_admin": True})
async def broadcast_all(callback: types.CallbackQuery, state: FSMContext) -> None:
    if (
        not callback.from_user
        or not callback.message
        or not hasattr(callback.message, "edit_text")
        or not callback.data
    ):
        logger.warning("Получен некорректный callback")
        return

    await callback.message.edit_text(
        "✍️ Напишите текст рассылки для всех пользователей:",
        reply_markup=create_cancell_inline_keyboard({}),
    )
    await state.set_state(BroadcastAll.waiting_for_message)
    logger.info(
        f"Пользователь @{callback.from_user.username} с id {callback.from_user.id} начал создавать рассылку для всех пользователей"
    )


@callback_router.callback_query(F.data == "broadcast_class", flags={"need_admin": True})
async def broadcast_class(callback: types.CallbackQuery, state: FSMContext) -> None:
    if (
        not callback.from_user
        or not callback.message
        or not hasattr(callback.message, "edit_text")
        or not callback.data
    ):
        logger.warning("Получен некорректный callback")
        return

    buttons = {grade: "select_broadcast_class:" + grade.lower() for grade in classes}

    await callback.message.edit_text(
        "📃 Выберите класс:",
        reply_markup=create_cancell_inline_keyboard(buttons),
    )
    await state.set_state(BroadcastClass.waiting_for_class)
    logger.info(
        f"Пользователь @{callback.from_user.username} с id {callback.from_user.id} начал создавать рассылку для класса"
    )


@callback_router.callback_query(
    F.data.startswith("select_broadcast_class:"), flags={"need_admin": True}
)
async def select_broadcast_class(
    callback: types.CallbackQuery, state: FSMContext
) -> None:
    if (
        not callback.from_user
        or not callback.message
        or not hasattr(callback.message, "edit_text")
        or not callback.data
    ):
        logger.warning("Получен некорректный callback")
        return

    selected_class = callback.data.split(":")[1]

    await state.update_data(selected_class=selected_class)

    await callback.message.edit_text(
        f"✍️ Напишите текст рассылки для класса {selected_class}:",
        reply_markup=create_cancell_inline_keyboard({}),
    )
    await state.set_state(BroadcastClass.waiting_for_message)
    logger.info(
        f"Пользователь @{callback.from_user.username} с id {callback.from_user.id} выбрал класс {selected_class} для рассылки"
    )
