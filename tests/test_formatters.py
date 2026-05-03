def test_get_schedule_message():
    from src.bot.utils.formatters import get_schedule_message

    schedule = {
        "Понедельник": {
            "1": {"name": "Математика", "time": "08:00 - 09:30", "cab": "101"},
            "2": {"name": "Физика", "time": "09:45 - 11:15", "cab": "102"},
        },
        "Вторник": {},
    }

    expected_message = """<b>🗓️ Расписание на неделю:</b>

<b>📅 Понедельник</b>
1. 🧮 <b>Математика</b> — 08:00-09:30 | каб. 101
2. 🚀 <b>Физика</b> — 09:45-11:15 | каб. 102

<b>📅 Вторник</b>

Уроков нет

"""

    result = get_schedule_message(schedule)
    assert result == expected_message

    result_empty = get_schedule_message({})
    assert result_empty == "<b>🗓️ Расписание на неделю:</b>\n\nУроков нет\n\n"

    result_empty_day = get_schedule_message({"Среда": {}})
    assert (
        result_empty_day
        == "<b>🗓️ Расписание на неделю:</b>\n\n<b>📅 Среда</b>\n\nУроков нет\n\n"
    )

    result_none = get_schedule_message(None)
    assert result_none == "<b>🗓️ Расписание на неделю:</b>\n\nУроков нет\n\n"


def test_get_schedule_today_message():
    from src.bot.utils.formatters import get_schedule_today_message

    schedule = {
        "1": {"name": "Математика", "time": "08:00 - 09:30", "cab": "101"},
        "2": {"name": "Физика", "time": "09:45 - 11:15", "cab": "102"},
    }

    expected_message = """<b>🗓️ Расписание на сегодня (понедельник):</b>

1. 🧮 <b>Математика</b> — 08:00-09:30 | каб. 101

2. 🚀 <b>Физика</b> — 09:45-11:15 | каб. 102

"""

    result = get_schedule_today_message(schedule, "Понедельник")
    assert result == expected_message

    result_empty = get_schedule_today_message({}, "Понедельник")
    assert result_empty == "<b>🗓️ Расписание на сегодня (понедельник):</b>\n\nУроков нет"

    result_none = get_schedule_today_message(None, "Понедельник")
    assert result_none == "<b>🗓️ Расписание на сегодня (понедельник):</b>\n\nУроков нет"


def test_get_schedule_tomorrow_message():
    from src.bot.utils.formatters import get_schedule_tomorrow_message

    schedule = {
        "1": {"name": "Математика", "time": "08:00 - 09:30", "cab": "101"},
        "2": {"name": "Физика", "time": "09:45 - 11:15", "cab": "102"},
    }

    expected_message = """<b>🗓️ Расписание на завтра (вторник):</b>

1. 🧮 <b>Математика</b> — 08:00-09:30 | каб. 101

2. 🚀 <b>Физика</b> — 09:45-11:15 | каб. 102

"""

    result = get_schedule_tomorrow_message(schedule, "Вторник")
    assert result == expected_message

    result_empty = get_schedule_tomorrow_message({}, "Вторник")
    assert result_empty == "<b>🗓️ Расписание на завтра (вторник):</b>\n\nУроков нет"

    result_none = get_schedule_tomorrow_message(None, "Вторник")
    assert result_none == "<b>🗓️ Расписание на завтра (вторник):</b>\n\nУроков нет"


def test_get_lesson_message():
    from src.bot.utils.formatters import get_lesson_message

    lesson = {"name": "Математика", "time": "08:00 - 09:30", "cab": "101"}
    expected_message = """<b>⏰ Текущий урок: 🧮 Математика</b>

<b>🕜 Время:</b> 08:00 - 09:30
<b>🔢 Урок по счету:</b> 1
<b>🚪 Кабинет:</b> 101
"""

    result = get_lesson_message("1", lesson)
    assert result == expected_message

    result_empty = get_lesson_message("1", {})
    assert result_empty == "Ошибка: данные урока не найдены"

    result_none = get_lesson_message("1", None)
    assert result_none == "Ошибка: данные урока не найдены"

    result_double_none = get_lesson_message(None, None)
    assert result_double_none == "Ошибка: номер урока не найден"


def test_get_next_lesson_message():
    from datetime import timedelta

    from src.bot.utils.formatters import get_next_lesson_message

    next_time_to_bell = timedelta(minutes=5, seconds=30)
    next_lesson = {"name": "Математика", "time": "09:45 - 11:15", "cab": "102"}
    expected_message = """<b>⏰ Следующий урок: 🧮 Математика</b>

<b>⏳ До звонка:</b> 5 минут 30 секунд
<b>🕜 Время:</b> 09:45 - 11:15
<b>🚪 Кабинет:</b> 102
"""
    result = get_next_lesson_message(next_time_to_bell, next_lesson)
    assert result == expected_message

    next_lesson_with_group = {
        "name": "Физика",
        "time": "11:30 - 13:00",
        "cab": "103",
        "group": True,
        "groups": [{"group": "2", "cab": "104"}, {"group": "3", "cab": "105"}],
    }
    expected_message_with_group = """<b>⏰ Следующий урок: 🚀 Физика</b>
<b>⏳ До звонка:</b> 5 минут 30 секунд
<b>🕜 Время:</b> 11:30 - 13:00

<b>Группы:</b>
   ├ группа 1 → каб. 103
   ├ группа 2 → каб. 104
   └ группа 3 → каб. 105
"""
    result_with_group = get_next_lesson_message(
        next_time_to_bell, next_lesson_with_group
    )
    assert result_with_group == expected_message_with_group

    invalid_lesson = {"name": 123, "time": "09:45 - 11:15", "cab": "102"}
    result_error = get_next_lesson_message(next_time_to_bell, invalid_lesson)
    assert result_error == "Ошибка: данные урока не найдены"

    missing_cab = {"name": "Математика", "time": "09:45 - 11:15", "cab": None}
    result_missing = get_next_lesson_message(next_time_to_bell, missing_cab)
    assert result_missing == "Ошибка: данные урока не найдены"

    no_emoji_lesson = {
        "name": "Неизвестный предмет",
        "time": "10:00 - 11:30",
        "cab": "200",
    }
    expected_no_emoji = """<b>⏰ Следующий урок:  Неизвестный предмет</b>

<b>⏳ До звонка:</b> 5 минут 30 секунд
<b>🕜 Время:</b> 10:00 - 11:30
<b>🚪 Кабинет:</b> 200
"""
    result_no_emoji = get_next_lesson_message(next_time_to_bell, no_emoji_lesson)
    assert result_no_emoji == expected_no_emoji


def test_get_bell_message():
    from datetime import timedelta

    from src.bot.utils.formatters import get_bell_message

    time_to_bell = timedelta(minutes=3, seconds=45)
    expected_message = "🔔 Время до звонка: 3 минут 45 секунд"
    result = get_bell_message(time_to_bell)
    assert result == expected_message

    time_to_bell_zero = timedelta(seconds=0)
    expected_zero_message = "🔔 Время до звонка: 0 минут 0 секунд"
    result_zero = get_bell_message(time_to_bell_zero)
    assert result_zero == expected_zero_message

    time_to_bell_none = None
    expected_none_message = "Ошибка: данные времени до звонка не найдены"
    result_none = get_bell_message(time_to_bell_none)
    assert result_none == expected_none_message


def test_get_changes_message():
    from src.bot.utils.formatters import get_changes_message

    all_changes = {
        "01.10.2023": {
            "10а": [
                {
                    "lesson_num": "1",
                    "subject_orig": "Математика",
                    "subject_new": "Алгебра",
                    "teacher": "Иванов И.И.",
                    "room": "101",
                },
                {
                    "lesson_num": "2",
                    "subject_orig": "Физика",
                    "subject_new": "",
                    "teacher": "нет",
                    "room": "102",
                },
                {
                    "lesson_num": "3",
                    "subject_orig": "Химия",
                    "subject_new": "Химия",
                    "teacher": "Петров П.П.",
                    "room": "",
                },
            ]
        },
        "02.10.2023": {
            "10а": [
                {
                    "lesson_num": "1",
                    "subject_orig": "История",
                    "subject_new": "Обществознание",
                    "teacher": "",
                    "room": "203",
                }
            ]
        },
    }
    _grade = "10А"
    expected_message = """<b>🔄 Замены уроков для 10А:</b>

📅 <b>На 01.10.2023:</b>
1. Математика ➔ <b>Алгебра</b> (Иванов И.И.) | каб. 101
2. Физика (❌ Урока нет) | каб. 102
3. Химия (Петров П.П.)

📅 <b>На 02.10.2023:</b>
1. История ➔ <b>Обществознание</b> | каб. 203

"""
    result = get_changes_message(all_changes, _grade)
    assert result == expected_message

    all_changes_no_grade = {
        "01.10.2023": {
            "11б": [
                {
                    "lesson_num": "1",
                    "subject_orig": "Математика",
                    "subject_new": "Алгебра",
                    "teacher": "Иванов И.И.",
                    "room": "101",
                }
            ]
        }
    }
    _grade_no = "10А"
    expected_no_message = "<b>🔄 Замены уроков:</b>\n\nЗамен для класса 10А не найдено."
    result_no = get_changes_message(all_changes_no_grade, _grade_no)
    assert result_no == expected_no_message

    result_empty = get_changes_message({}, "10А")
    assert (
        result_empty == "<b>🔄 Замены уроков:</b>\n\nЗамен для класса 10А не найдено."
    )

    _grade_upper = "  10а  "
    result_upper = get_changes_message(all_changes, _grade_upper)
    assert result_upper == expected_message

    result_none = get_changes_message(None, None)
    assert result_none == "Ошибка: данные замен не найдены"


def test_get_admin_panel_message():
    from src.bot.utils.formatters import get_admin_panel_message

    total_users = 100
    user_count_by_grades = {"10А": 30, "10Б": 20, "11А": 50}
    expected_message = """🤖 <b>Админ-панель</b>

👤 Всего пользователей: 100

📋 <b>Распределение по классам:</b> 
• 10А: 30
• 10Б: 20
• 11А: 50"""

    assert (
        get_admin_panel_message(total_users, user_count_by_grades) == expected_message
    )

    expected_message = """🤖 <b>Админ-панель</b>

👤 Всего пользователей: 100

📋 <b>Распределение по классам:</b> У пользователей не установлен класс"""

    assert get_admin_panel_message(total_users, {}) == expected_message
