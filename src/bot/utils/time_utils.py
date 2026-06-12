from datetime import datetime, time, timedelta

from src.bot.utils.constants import days_map


def parse_time_range(time_str: str) -> tuple[time, time] | tuple[None, None]:
    try:
        start_str, end_str = time_str.split(" - ")
        start = datetime.strptime(start_str, "%H:%M").time()
        end = datetime.strptime(end_str, "%H:%M").time()
        return start, end
    except Exception:
        return None, None


def get_current_lesson(
    schedule: dict[str, dict[str, dict[str, str | None]]], now: datetime
) -> tuple[str, dict[str, str | None]] | tuple[None, None]:
    if not isinstance(schedule, dict) or not isinstance(now, datetime):
        return None, None

    time_now = now.time()
    today = days_map.get(now.weekday())

    if not today or today not in schedule:
        return None, None

    for number, lesson in schedule[today].items():
        lesson_time = lesson.get("time")
        if not lesson_time:
            return None, None

        start, end = parse_time_range(lesson_time)
        if not start or not end:
            return None, None

        if start <= time_now <= end:
            return number, lesson

    return None, None


def get_time_to_bell(
    schedule: dict[str, dict[str, dict[str, str | None]]], now: datetime
) -> tuple[None, None] | tuple[timedelta, dict[str, str | None]]:
    if not isinstance(schedule, dict) or not isinstance(now, datetime):
        return None, None

    today = days_map.get(now.weekday())

    if not today or today not in schedule:
        return None, None

    lessons = list(schedule[today].items())

    for i, (_, lesson) in enumerate(lessons):
        lesson_time = lesson.get("time")

        if not lesson_time:
            return None, None

        start, end = parse_time_range(lesson_time)

        if not start or not end:
            return None, None

        start_dt = now.replace(hour=start.hour, minute=start.minute, second=0)
        end_dt = now.replace(hour=end.hour, minute=end.minute, second=0)

        if start_dt <= now <= end_dt:
            return end_dt - now, lesson

        if i < len(lessons) - 1:
            next_lesson = lessons[i + 1][1]

            if not next_lesson:
                return None, None

            next_lesson_time = next_lesson.get("time")

            if not next_lesson_time:
                return None, None

            next_start, _ = parse_time_range(next_lesson_time)

            if not next_start:
                return None, None

            next_start_dt = now.replace(
                hour=next_start.hour, minute=next_start.minute, second=0
            )

            if end_dt <= now <= next_start_dt:
                return next_start_dt - now, next_lesson

    return None, None
