import re
from typing import Any, Dict

from bs4 import BeautifulSoup
from bs4.element import Tag

from src.bot.utils.api_client import ApiClient
from src.bot.utils.csv_utils import get_changes
from src.bot.utils.logger import Logger

logger = Logger(__name__).get_logger()


def parse_schedule(html: str) -> Dict[str, Dict[str, Dict[str, Any]]] | None:
    try:
        soup = BeautifulSoup(html, "lxml")

        table = soup.find("table", class_="rasp")

        if not isinstance(table, Tag):
            logger.critical("Не удалось найти таблицу с расписанием")
            return None

        rows = table.find_all("tr")

        result: Dict[str, Dict[str, Dict[str, Any]]] = {}

        current_day: str | None = None
        current_lesson: str | None = None

        for row in rows:
            if row.find("h3"):
                current_day = row.getText(strip=True)
                if current_day:
                    result[current_day] = {}
                continue

            tds = row.find_all("td")

            if len(tds) != 5:
                continue

            number = tds[0].get_text(strip=True)
            time = tds[1].get_text()
            name = tds[2].get_text()
            group = tds[3].get_text(strip=True)
            cab = tds[4].get_text(strip=True)

            if number and current_day:
                current_lesson = number

                result[current_day][current_lesson] = {
                    "time": time,
                    "name": name,
                    "group": group or None,
                    "cab": cab,
                }

            else:
                if current_lesson is None or current_day is None:
                    continue

                lesson = result[current_day][current_lesson]

                if "groups" not in lesson:
                    lesson["groups"] = []

                lesson["groups"].append({"group": group, "cab": cab})

        return result
    except Exception as e:
        logger.critical(f"Не удалось спарсить расписание: {e}")
        return None


def parse_changes_url(html: str) -> str | None:
    try:
        soup = BeautifulSoup(html, "lxml")

        li = soup.find(
            "li",
            class_="menu-item menu-item-type-custom menu-item-object-custom menu-item-5101",
        )
        if not isinstance(li, Tag):
            logger.critical("Не удалось найти элемент с URL изменений")
            return None

        a_tag = li.find("a")
        if not isinstance(a_tag, Tag):
            logger.critical("Не удалось найти ссылку с URL изменений")
            return None

        url = a_tag.get("href")

        if not isinstance(url, str):
            logger.critical("Не удалось найти URL изменений")
            return None

        return url
    except Exception as e:
        logger.critical(f"Не удалось спарсить URL изменений: {e}")
        return None


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


async def get_changes_table_rows() -> list[list[str]] | None:
    try:
        changes_url = await get_changes_url()

        if not changes_url:
            logger.warning(
                "Не удалось получить ссылку на страницу с заменами, пропуск получения данных о заменах"
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


async def get_changes_url() -> str | None:
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

        return changes_url
    except Exception as e:
        logger.critical(f"Не удалось получить ссылку на таблицу замен: {e}")
        return None
