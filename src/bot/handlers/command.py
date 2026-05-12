from datetime import datetime

import pytz
from aiogram import Router, types
from aiogram.exceptions import TelegramNetworkError
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

from src.bot.keyboards.inline import (
    create_cancell_inline_keyboard,
    create_inline_keyboard,
)
from src.bot.messages.common import before_review_message, start_message
from src.bot.repositories.review_repository import ReviewRepository
from src.bot.repositories.user_repository import UserRepository
from src.bot.services.cache_service import cache_service
from src.bot.services.schedule_service import get_schedule_by_grade
from src.bot.states.review_states import ReviewCreate
from src.bot.utils.constants import classes, days_map
from src.bot.utils.formatters import (
    get_admin_panel_message,
    get_bell_message,
    get_changes_message,
    get_lesson_message,
    get_next_lesson_message,
    get_schedule_message,
    get_schedule_today_message,
    get_schedule_tomorrow_message,
)
from src.bot.utils.logger import Logger
from src.bot.utils.parser import get_changes_url
from src.bot.utils.time_utils import get_current_lesson, get_time_to_bell

command_router = Router()
logger = Logger(__name__).get_logger()


@command_router.message(CommandStart(), flags={"need_grade": False})
async def start(message: types.Message) -> None:
    if not message.from_user:
        logger.warning("Получено сообщение без информации о пользователе")
        return

    logger.info(f"Пользователь @{message.from_user.username} вызвал команду /start")

    user_class_in_cache = await cache_service.get_user_class_from_cache(
        message.from_user.id
    )

    if user_class_in_cache is None:
        logger.info(
            f"Класс пользователя @{message.from_user.username} не найден в кэше"
        )
        user = await UserRepository().get_user_by_telegram_id(message.from_user.id)

        if not user:
            logger.info(
                f"Пользователь @{message.from_user.username} не найден в базе данных, создается новый пользователь"
            )
            await UserRepository().create_user(
                telegram_id=message.from_user.id, grade=None
            )
            await cache_service.set_user_class_in_cache(message.from_user.id, None)
        else:
            if user.grade:
                logger.info(
                    f"Класс пользователя @{message.from_user.username} найден в базе данных: {user.grade}, сохраняется в кэше"
                )
                await cache_service.set_user_class_in_cache(
                    message.from_user.id, str(user.grade)
                )
            else:
                logger.info(
                    f"Класс пользователя @{message.from_user.username} не установлен в базе данных"
                )
                await cache_service.set_user_class_in_cache(message.from_user.id, None)

    elif user_class_in_cache is False:
        logger.info(
            f"Класс пользователя @{message.from_user.username} установлен как None в кэше"
        )

    if await cache_service.get_image_id_from_cache("start") is None:
        try:
            image = types.FSInputFile("./src/bot/img/bot.png")
            message = await message.answer_photo(image, caption=start_message)

            if not message.photo:
                logger.warning("Ответ на /start не содержит фото")
                await message.answer(start_message)
                return

            await cache_service.set_image_id_in_cache(
                "start", message.photo[-1].file_id
            )
        except TelegramNetworkError:
            logger.warning("Не удалось отправить ответ с фото на /start")
            await message.answer(start_message)
    else:
        cached_image_id = await cache_service.get_image_id_from_cache("start")

        if not isinstance(cached_image_id, str):
            logger.warning(
                "Кэш для фото ответа на /start содержит некорректное значение"
            )
            await message.answer(start_message)
            return

        await message.answer_photo(cached_image_id, caption=start_message)


@command_router.message(
    Command("schedule"), flags={"need_grade": True, "cmd": "schedule"}
)
async def schedule(message: types.Message, grade: str) -> None:
    if not message.from_user or not grade:
        logger.warning("Получено сообщение без информации о пользователе")
        return

    logger.info(
        f"Пользователь @{message.from_user.username} вызвал команду /schedule для класса {grade}"
    )

    rasp = await get_schedule_by_grade(grade)

    if not rasp:
        await message.answer("🚫 Не удалось получить расписание. Попробуйте позже.")
        return

    await message.answer(get_schedule_message(rasp))


@command_router.message(
    Command("schedule_today"), flags={"need_grade": True, "cmd": "schedule_today"}
)
async def schedule_today(message: types.Message, grade: str) -> None:
    if not message.from_user or not grade:
        logger.warning("Получено сообщение без информации о пользователе")
        return

    now = datetime.now()
    current_day = days_map.get(now.weekday())

    if not current_day:
        await message.answer("🏝️ Сегодня выходной!")
        return

    logger.info(
        f"Пользователь @{message.from_user.username} вызвал команду /schedule_today для класса {grade}"
    )

    rasp = await get_schedule_by_grade(grade)

    if not rasp:
        await message.answer("🚫 Не удалось получить расписание. Попробуйте позже.")
        return

    today_schedule = rasp.get(current_day)

    if not today_schedule:
        await message.answer("🏝️ Сегодня выходной!")
        return

    await message.answer(get_schedule_today_message(today_schedule, current_day))


@command_router.message(
    Command("schedule_tomorrow"), flags={"need_grade": True, "cmd": "schedule_tomorrow"}
)
async def schedule_tomorrow(message: types.Message, grade: str) -> None:
    if not message.from_user or not grade:
        logger.warning("Получено сообщение без информации о пользователе")
        return

    now = datetime.now()
    day_tomorrow = days_map.get(now.weekday() + 1 if now.weekday() + 1 != 7 else 0)

    if not day_tomorrow:
        await message.answer("🏝️ Завтра выходной!")
        return

    logger.info(
        f"Пользователь @{message.from_user.username} вызвал команду /schedule_tomorrow для класса {grade}"
    )

    rasp = await get_schedule_by_grade(grade)

    if not rasp:
        await message.answer("🚫 Не удалось получить расписание. Попробуйте позже.")
        return

    tomorrow_schedule = rasp.get(day_tomorrow)

    if not tomorrow_schedule:
        await message.answer("🏝️ Завтра выходной!")
        return

    await message.answer(
        get_schedule_tomorrow_message(tomorrow_schedule, day_tomorrow.lower())
    )


@command_router.message(Command("lesson"), flags={"need_grade": True, "cmd": "lesson"})
async def lesson(message: types.Message, grade: str) -> None:
    if not message.from_user or not grade:
        logger.warning("Получено сообщение без информации о пользователе")
        return

    now = datetime.now()
    current_day = days_map.get(now.weekday())

    if not current_day:
        await message.answer("🏝️ Сегодня выходной!")
        return

    logger.info(
        f"Пользователь @{message.from_user.username} вызвал команду /lesson для класса {grade}"
    )

    rasp = await get_schedule_by_grade(grade)

    if not rasp:
        await message.answer("🚫 Не удалось получить расписание. Попробуйте позже.")
        return

    now = datetime.now(pytz.timezone("Europe/Moscow"))
    number, lesson = get_current_lesson(rasp, now)

    if not number or not lesson:
        next_time_to_bell, next_lesson = get_time_to_bell(rasp, now)

        if not next_lesson:
            await message.answer("🏝️ Сейчас нет уроков.")
            return

        if not next_time_to_bell:
            logger.warning("Не удалось определить время до следующего звонка")
            await message.answer(
                "🏝️ Сейчас нет урока, но не удалось определить время до следующего звонка."
            )
            return

        await message.answer(
            "🏝️ Сейчас нет урока.\n\n"
            + get_next_lesson_message(next_time_to_bell, next_lesson)
        )
        return

    await message.answer(get_lesson_message(number, lesson))


@command_router.message(Command("bell"), flags={"need_grade": True, "cmd": "bell"})
async def bell(message: types.Message, grade: str) -> None:
    if not message.from_user or not grade:
        logger.warning("Получено сообщение без информации о пользователе")
        return

    logger.info(
        f"Пользователь @{message.from_user.username} вызвал команду /bell для класса {grade}"
    )

    now = datetime.now()
    current_day = days_map.get(now.weekday())

    if not current_day:
        await message.answer("🏝️ Сегодня выходной!")
        return

    rasp = await get_schedule_by_grade(grade)

    if not rasp:
        await message.answer("🚫 Не удалось получить расписание. Попробуйте позже.")
        return

    now = datetime.now(pytz.timezone("Europe/Moscow"))
    time_to_bell, _ = get_time_to_bell(rasp, now)

    if not time_to_bell:
        await message.answer("🏝️ Сейчас нет уроков.")
        return

    await message.answer(get_bell_message(time_to_bell))


@command_router.message(Command("set_my_class"), flags={"need_grade": False})
async def set_my_class(message: types.Message) -> None:
    if not message.from_user:
        logger.warning("Получено сообщение без информации о пользователе")
        return

    logger.info(
        f"Пользователь @{message.from_user.username} вызвал команду /set_my_class"
    )

    buttons = {grade: "set_my_class:" + grade.lower() for grade in classes}

    await message.answer(
        "📃 Выберите Ваш класс из списка:",
        reply_markup=create_cancell_inline_keyboard(buttons),
    )


@command_router.message(
    Command("changes"), flags={"need_grade": True, "cmd": "changes"}
)
async def changes(message: types.Message, grade: str) -> None:
    if not message.from_user or not grade:
        logger.warning("Получено сообщение без информации о пользователе")
        return

    logger.info(
        f"Пользователь @{message.from_user.username} вызвал команду /changes для класса {grade}"
    )

    changes = await cache_service.get_changes_from_cache()

    if changes is None:
        await message.answer(
            "🚫 <b>Ошибка:</b> не удалось получить информацию о заменах. Попробуйте позже."
        )
        return

    changes_table_url = await cache_service.get_changes_url_from_cache()

    if not isinstance(changes_table_url, str):
        logger.warning(
            "Не удалось получить ссылку на страницу с заменами из кэша, пробуем получить напрямую"
        )
        changes_table_url = await get_changes_url()
        if not isinstance(changes_table_url, str):
            await message.answer(
                "🚫 <b>Ошибка:</b> не удалось получить ссылку на страницу с заменами. Попробуйте позже."
            )
            return
        await cache_service.set_changes_url_in_cache(changes_table_url)

    await message.answer(
        get_changes_message(changes, grade.lower(), changes_table_url),
        disable_web_page_preview=True,
    )


@command_router.message(
    Command("admin"), flags={"need_grade": False, "need_admin": True}
)
async def admin(message: types.Message) -> None:
    if not message.from_user:
        logger.warning("Получено сообщение без информации о пользователе")
        return

    logger.info(
        f"Пользователь @{message.from_user.username} с id {message.from_user.id} вызвал команду /admin"
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

    await message.answer(
        get_admin_panel_message(total_users, user_count_by_grades),
        reply_markup=create_inline_keyboard(buttons),
    )
    logger.info(
        f"Пользователь @{message.from_user.username} с id {message.from_user.id} получил админ-панель"
    )


@command_router.message(Command("review"), flags={"need_grade": False})
async def review(message: types.Message, state: FSMContext) -> None:
    if not message.from_user:
        logger.warning("Получено сообщение без информации о пользователе")
        return

    logger.info(
        f"Пользователь @{message.from_user.username} с id {message.from_user.id} вызвал команду /review"
    )

    await state.set_state(ReviewCreate.waiting_for_review)
    await message.answer(
        before_review_message, reply_markup=create_cancell_inline_keyboard({})
    )
