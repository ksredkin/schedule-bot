import asyncio
import re

from aiogram import Bot

from src.bot.core.config import MINUTES_TO_CHECK_CHANGES
from src.bot.repositories.user_repository import UserRepository
from src.bot.utils.api_client import ApiClient
from src.bot.utils.changes_cache import get_changes_from_cache, set_changes_in_cache
from src.bot.utils.csv_utils import get_changes
from src.bot.utils.formatters import get_changes_message
from src.bot.utils.logger import Logger
from src.bot.utils.parser import parse_changes_url

logger = Logger(__name__).get_logger()


async def get_changes_table_rows() -> list[list[str]] | None:
    try:
        main_page = await ApiClient.get_main_page()

        if not main_page:
            logger.warning(
                "Не удалось получить главную страницу для извлечения ссылки на замены"
            )
            return None

        changes_url = parse_changes_url(main_page)

        if not changes_url:
            logger.warning(
                "Не удалось найти ссылку на страницу с заменами на главной странице"
            )
            return None

        changes_url_without_https_and_edit = changes_url[8:].split("/")[:-1]
        changes_url_without_https_and_edit.append("export?format=csv")
        download_url = "https://" + "/".join(changes_url_without_https_and_edit)

        csv_text = await ApiClient.get_file(download_url)

        if not csv_text:
            logger.warning("Полученный CSV с изменениями пустой")
            return None

        table_rows = get_changes(csv_text)

        return table_rows
    except Exception as e:
        logger.critical(f"Не удалось получить строки таблицы изменений: {e}")
        return None


# Сгенерировано Gemini
def parse_changes_table_rows(
    rows: list[list[str]],
) -> dict[str, dict[str, list[dict[str, str]]]] | None:
    result: dict[str, dict[str, list[dict[str, str]]]] = {}
    current_date = None
    collecting_data = False
    date_pattern = re.compile(r"(\d{2}\.\d{2}\.\d{4})")

    for row in rows:
        row_text = " ".join(filter(None, map(str, row)))
        date_match = date_pattern.search(row_text)

        if date_match:
            current_date = date_match.group(1)
            if current_date not in result:
                result[current_date] = {}
            collecting_data = False
            continue

        row_joined = "".join(map(str, row))
        if "Урок" in row_joined and "Предмет" in row_joined:
            collecting_data = True
            continue

        if collecting_data and len(row) >= 2 and row[0] and row[1]:
            if str(row[0]).strip().lower() == "урок":
                continue

            if current_date:
                class_name = str(row[1]).strip().lower()
                if class_name not in result[current_date]:
                    result[current_date][class_name] = []

                result[current_date][class_name].append(
                    {
                        "lesson_num": str(row[0]).strip(),
                        "subject_orig": str(row[2]).strip(),
                        "teacher": str(row[3]).strip(),
                        "subject_new": str(row[4]).strip(),
                        "room": str(row[5]).strip() if len(row) > 5 else "",
                    }
                )

        if not any(row):
            collecting_data = False

    return result


async def start_update_changes_cache_service(bot: Bot) -> None:
    first_raw_rows = await get_changes_table_rows()

    if first_raw_rows:
        current_parsed_all = parse_changes_table_rows(first_raw_rows)
        if current_parsed_all is not None:
            await set_changes_in_cache(current_parsed_all)
    else:
        logger.warning("Не удалось получить новые данные, пропуск...")

    while True:
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

        old_parsed_all = await get_changes_from_cache()

        if current_parsed_all != old_parsed_all:
            users = await UserRepository.get_users()

            if not users:
                logger.info("Нет пользователей для рассылки обновлений")
                await set_changes_in_cache(current_parsed_all)
                await asyncio.sleep(MINUTES_TO_CHECK_CHANGES * 60)
                continue

            for user in users:
                grade = user.grade

                if grade is None:
                    continue

                grade = str(grade)  # type: ignore
                grade = grade.lower().strip()

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
                changes_message = get_changes_message(current_parsed_all, grade)

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
                    await bot.send_message(int(user.telegram_id), text)
                except Exception as e:
                    logger.warning(
                        f"Ошибка отправки пользователю {user.telegram_id}: {e}"
                    )

            await set_changes_in_cache(current_parsed_all)
            logger.info("Рассылка обновлений завершена")
        else:
            logger.info("Изменений в таблице нет")

        await asyncio.sleep(MINUTES_TO_CHECK_CHANGES * 60)
