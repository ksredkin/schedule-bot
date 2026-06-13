import asyncio

from aiogram import Bot

from src.bot.core.config import MINUTES_TO_CHECK_CHANGES
from src.bot.database.connection import sessionmaker
from src.bot.repositories.user_repository import UserRepository
from src.bot.services.cache_service import cache_service
from src.bot.utils.formatters import get_changes_message
from src.bot.utils.logger import Logger
from src.bot.utils.parser import (
    get_changes_table_rows,
    get_changes_url,
    parse_changes_table_rows,
)

logger = Logger(__name__).get_logger()


async def start_update_changes_cache_service(bot: Bot) -> None:
    first_raw_rows = await get_changes_table_rows()

    if first_raw_rows:
        current_parsed_all = parse_changes_table_rows(first_raw_rows)
        if current_parsed_all is not None:
            await cache_service.set_changes_in_cache(current_parsed_all)
    else:
        logger.warning("Не удалось получить новые данные, пропуск...")

    initial_url = await get_changes_url()
    if initial_url:
        await cache_service.set_changes_url_in_cache(initial_url)

    while True:
        async with sessionmaker() as session:
            raw_rows = await get_changes_table_rows()

            if not raw_rows:
                logger.warning("Не удалось получить новые данные, пропуск...")
                await asyncio.sleep(MINUTES_TO_CHECK_CHANGES * 60)
                continue

            current_parsed_all = parse_changes_table_rows(raw_rows)

            if current_parsed_all is None:
                logger.warning("Не удалось распарсить новые данные, пропуск...")
                await asyncio.sleep(MINUTES_TO_CHECK_CHANGES * 60)
                continue

            old_parsed_all = await cache_service.get_changes_from_cache()

            if current_parsed_all != old_parsed_all:
                user_repository = UserRepository(session)
                users = await user_repository.get_users()

                if not users:
                    logger.info("Нет пользователей для рассылки обновлений")
                    await cache_service.set_changes_in_cache(current_parsed_all)
                    await asyncio.sleep(MINUTES_TO_CHECK_CHANGES * 60)
                    continue

                changes_table_url = await get_changes_url()
                if (
                    changes_table_url
                    != await cache_service.get_changes_url_from_cache()
                    and changes_table_url is not None
                ):
                    await cache_service.set_changes_url_in_cache(changes_table_url)

                for user in users:
                    if not user.grade:
                        continue

                    grade = str(user.grade).lower().strip()

                    has_changes_for_user = False

                    for date in current_parsed_all:
                        new_grade_data = current_parsed_all.get(date, {}).get(grade)
                        old_grade_data = (old_parsed_all or {}).get(date, {}).get(grade)

                        if new_grade_data != old_grade_data:
                            has_changes_for_user = True
                            break

                    if not has_changes_for_user:
                        continue

                    text = "🔄 <b>Обновились замены!</b>\n\n"

                    changes_message = get_changes_message(
                        current_parsed_all, grade, changes_table_url
                    )

                    if changes_message is None:
                        logger.warning(
                            f"Не удалось сформировать сообщение с заменами для пользователя {user.telegram_id} и класса {grade}"
                        )
                        continue

                    text += (
                        changes_message
                        if changes_message
                        else "Ошибка при формировании сообщения с заменами."
                    )

                    try:
                        await bot.send_message(
                            int(user.telegram_id), text, disable_web_page_preview=True
                        )
                        await asyncio.sleep(0.05)
                    except Exception as e:
                        logger.warning(
                            f"Ошибка отправки пользователю {user.telegram_id}: {e}"
                        )

                await cache_service.set_changes_in_cache(current_parsed_all)
                logger.info("Рассылка обновлений завершена")
            else:
                logger.info("Изменений в таблице нет")

            await asyncio.sleep(MINUTES_TO_CHECK_CHANGES * 60)
