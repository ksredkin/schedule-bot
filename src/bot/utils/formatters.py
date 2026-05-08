from datetime import timedelta
from typing import Any, Dict, List

emoji_prefixes = {
    "физическая": "🏀",
    "алгебра": "🧮",
    "математика": "🧮",
    "вероятность": "📊",
    "информатика": "💻",
    "иностранный": "🌐",
    "русский": "🇷🇺",
    "биология": "🌱",
    "разговор": "📢",
    "география": "🌍",
    "история": "🏛️",
    "музыка": "🎵",
    "труд(технология)": "📏",
    "геометрия": "📐",
    "изобразительное": "🎨",
    "физика": "🚀",
    "литература": "📚",
    "химия": "🧪",
    "россия-": "🧭",
    "обществознание": "⚖️",
    "индивидуальный": "⚙️",
    "основы": "⚠️",
    "программирование": "👨‍💻",
    "алгоритмика": "🧠",
    "окружающий": "🌎",
    "литературное": "📚",
}


def get_schedule_message(schedule: Dict[str, Dict[str, Dict[str, Any]]]) -> str:
    text = "<b>🗓️ Расписание на неделю:</b>\n\n"

    if not schedule:
        text += "Уроков нет\n\n"
        return text

    for day, lessons in schedule.items():
        text += f"<b>📅 {day}</b>\n"

        if not lessons:
            text += "\nУроков нет\n\n"
            continue

        for number, lesson in lessons.items():
            name: Any = lesson.get("name")
            time: Any = lesson.get("time")
            group: Any = lesson.get("group")
            cab: Any = lesson.get("cab")

            if (
                not isinstance(name, str)
                or not isinstance(time, str)
                or not isinstance(cab, str)
            ):
                return "🚫 Ошибка при формировании расписания. Пожалуйста, попробуйте позже."

            emoji_prefix = emoji_prefixes.get(name.lower().split()[0], "")

            if "groups" in lesson:
                text += f"{number}. {emoji_prefix} <b>{name}</b> — {time.replace(' ', '')}\n"

                if group:
                    text += f"   ├ группа {group} → каб. {cab}\n"

                lessons_groups = lesson.get("groups")

                if not lessons_groups:
                    continue

                for i, g in enumerate(lessons_groups):
                    prefix = "└" if len(lessons_groups) - 1 - i == 0 else "├"
                    text += f"   {prefix} группа {g['group']} → каб. {g['cab']}\n"

            else:
                text += f"{number}. {emoji_prefix} <b>{name}</b> — {time.replace(' ', '')} | каб. {cab}\n"

        text += "\n"

    return text


def get_schedule_today_message(
    schedule: Dict[str, Dict[str, Any]], day_of_week: str
) -> str:
    text = f"<b>🗓️ Расписание на сегодня ({day_of_week.lower()}):</b>\n\n"

    if not schedule:
        text += "Уроков нет"
        return text

    for number, lesson in schedule.items():
        name = lesson.get("name")
        time = lesson.get("time")
        group = lesson.get("group")
        cab = lesson.get("cab")

        if (
            not isinstance(name, str)
            or not isinstance(time, str)
            or not isinstance(cab, str)
        ):
            continue

        emoji_prefix = emoji_prefixes.get(name.lower().split()[0], "")

        if "groups" in lesson:
            text += (
                f"{number}. {emoji_prefix} <b>{name}</b> — {time.replace(' ', '')}\n"
            )

            if group:
                text += f"   ├ группа {group} → каб. {cab}\n"

            for i, g in enumerate(lesson["groups"]):
                prefix = "└" if len(lesson["groups"]) - 1 - i == 0 else "├"
                text += f"   {prefix} группа {g['group']} → каб. {g['cab']}\n"

        else:
            text += f"{number}. {emoji_prefix} <b>{name}</b> — {time.replace(' ', '')} | каб. {cab}\n"

        text += "\n"

    return text


def get_schedule_tomorrow_message(
    schedule: Dict[str, Dict[str, Any]], day_of_week: str
) -> str:
    text = f"<b>🗓️ Расписание на завтра ({day_of_week.lower()}):</b>\n\n"

    if not schedule:
        text += "Уроков нет"
        return text

    for number, lesson in schedule.items():
        name = lesson.get("name")
        time = lesson.get("time")
        group = lesson.get("group")
        cab = lesson.get("cab")

        if (
            not isinstance(name, str)
            or not isinstance(time, str)
            or not isinstance(cab, str)
        ):
            continue

        emoji_prefix = emoji_prefixes.get(name.lower().split()[0], "")

        if "groups" in lesson:
            text += (
                f"{number}. {emoji_prefix} <b>{name}</b> — {time.replace(' ', '')}\n"
            )

            if group:
                text += f"   ├ группа {group} → каб. {cab}\n"

            for i, g in enumerate(lesson["groups"]):
                prefix = "└" if len(lesson["groups"]) - 1 - i == 0 else "├"
                text += f"   {prefix} группа {g['group']} → каб. {g['cab']}\n"

        else:
            text += f"{number}. {emoji_prefix} <b>{name}</b> — {time.replace(' ', '')} | каб. {cab}\n"

        text += "\n"

    return text


def get_lesson_message(number: str, lesson: Dict[str, Any]) -> str:
    if not isinstance(number, str):
        return "Ошибка: номер урока не найден"

    if not isinstance(lesson, dict):
        return "Ошибка: данные урока не найдены"

    name = lesson.get("name")
    time = lesson.get("time")
    group = lesson.get("group")
    cab = lesson.get("cab")

    if (
        not isinstance(name, str)
        or not isinstance(time, str)
        or not isinstance(cab, str)
    ):
        return "Ошибка: данные урока не найдены"

    emoji_prefix = emoji_prefixes.get(name.lower().split()[0], "")

    if group:
        text = f"""<b>⏰ Текущий урок: {emoji_prefix} {name}</b>
<b>🕜 Время:</b> {time}
<b>🔢 Урок по счету:</b> {number}

<b>Группы:</b>
"""

        if group:
            text += f"   ├ группа {group} → каб. {cab}\n"
        else:
            text += f"   ├ группа 1 → каб. {cab}\n"

        for i, g in enumerate(lesson["groups"]):
            prefix = "└" if len(lesson["groups"]) - 1 - i == 0 else "├"
            text += f"   {prefix} группа {g['group']} → каб. {g['cab']}\n"

    else:
        text = f"""<b>⏰ Текущий урок: {emoji_prefix} {name}</b>

<b>🕜 Время:</b> {time}
<b>🔢 Урок по счету:</b> {number}
<b>🚪 Кабинет:</b> {cab}
"""

    return text


def get_next_lesson_message(
    next_time_to_bell: timedelta, next_lesson: Dict[str, Any]
) -> str:
    name = next_lesson.get("name")
    time = next_lesson.get("time")
    group = next_lesson.get("group")
    cab = next_lesson.get("cab")

    if (
        not isinstance(name, str)
        or not isinstance(time, str)
        or not isinstance(cab, str)
    ):
        return "Ошибка: данные урока не найдены"

    emoji_prefix = emoji_prefixes.get(name.lower().split()[0], "")

    minutes: int = int(next_time_to_bell.total_seconds() // 60)
    seconds: int = int(next_time_to_bell.total_seconds() % 60)

    if group:
        text = f"""<b>⏰ Следующий урок: {emoji_prefix} {name}</b>
<b>⏳ До звонка:</b> {minutes} минут {seconds} секунд
<b>🕜 Время:</b> {time}

<b>Группы:</b>
"""

        text += f"   ├ группа 1 → каб. {cab}\n"

        for i, g in enumerate(next_lesson["groups"]):
            prefix = "└" if len(next_lesson["groups"]) - 1 - i == 0 else "├"
            text += f"   {prefix} группа {g['group']} → каб. {g['cab']}\n"

    else:
        text = f"""<b>⏰ Следующий урок: {emoji_prefix} {name}</b>

<b>⏳ До звонка:</b> {minutes} минут {seconds} секунд
<b>🕜 Время:</b> {time}
<b>🚪 Кабинет:</b> {cab}
"""

    return text


def get_bell_message(time_to_bell: timedelta) -> str:
    if not isinstance(time_to_bell, timedelta):
        return "Ошибка: данные времени до звонка не найдены"

    minutes: int = int(time_to_bell.total_seconds() // 60)
    seconds: int = int(time_to_bell.total_seconds() % 60)

    return f"""🔔 Время до звонка: {minutes} минут {seconds} секунд"""


def get_changes_message(
    all_changes: Dict[str, Dict[str, List[Dict[str, str]]]],
    _grade: str,
    table_url: str | None = None,
) -> str:
    if not isinstance(all_changes, dict) or not isinstance(_grade, str):
        return "Ошибка: данные замен не найдены"

    _grade = _grade.lower().strip()
    text = f"<b>🔄 Замены уроков для {_grade.upper()}:</b>\n\n"

    found_any = False

    for date, grades in all_changes.items():
        if _grade in grades:
            found_any = True
            text += f"📅 <b>На {date}:</b>\n"

            for replace in grades[_grade]:
                l_num = replace["lesson_num"]
                s_orig = replace["subject_orig"]
                s_new = replace["subject_new"]
                teacher = replace["teacher"]
                room = replace["room"]

                text += f"{l_num}. {s_orig}"

                is_cancelled = (
                    not s_new and (not teacher or teacher.lower() == "нет") and not room
                )

                if is_cancelled:
                    text += " (❌ Урок отменен)"
                else:
                    if s_new and s_new.lower() != s_orig.lower():
                        text += f" ➔ <b>{s_new}</b>"

                    if teacher and teacher.lower() != "нет":
                        text += f" ({teacher})"

                    if room:
                        text += f" | каб. {room}"

                text += "\n"
            text += "\n"

    if not found_any:
        return (
            f"<b>🔄 Замены уроков:</b>\n\nЗамен для класса {_grade.upper()} не найдено."
        )

    if table_url:
        text += f"🔗 <a href='{table_url}'>Посмотреть оригинал таблицы</a>"

    return text


def get_admin_panel_message(
    total_users: int | None, user_count_by_grades: Dict[str, int | None]
) -> str:
    text = f"""🤖 <b>Админ-панель</b>

👤 Всего пользователей: {total_users if total_users is not None else "Ошибка"}

📋 <b>Распределение по классам:</b> """

    if total_users:
        if not user_count_by_grades:
            text += "У пользователей не установлен класс"

        for grade, count in user_count_by_grades.items():
            text += f"\n• {grade}: {count if count is not None else 'Ошибка'}"

    return text
