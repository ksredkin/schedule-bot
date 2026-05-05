import os

os.environ["REDIS_PORT"] = "6379"
os.environ["REDIS_HOST"] = "localhost"

from typing import Any
from unittest.mock import AsyncMock

import pytest

test_schedule_html = """<!DOCTYPE html>
<html>
    <body>
        <table class="rasp">
            <tr><td colspan="1"></td></tr>
            <tr><th colspan="1"><h3>Понедельник</h3></th></tr>
            <tr><th>№</th><th>Время</th><th>Урок</th><th>Гр.</th><th align="center">Каб.</th></tr>
            <tr bgcolor="#f9f9f9">
            <td width="10">1</td>
            <td class="rasp">08:00 - 08:40</td>
            <td class="rasp">Разговор о важном</td>
            <td class="rasp" align="center"></td>
            <td class="rasp" align="center">137</td>
            </tr>
        </table>
    </body>
</html>"""


@pytest.mark.asyncio
async def test_get_schedule_by_grade_with_redis(mocker: Any) -> None:
    mock = AsyncMock()
    mock.get_schedule_from_cache.return_value = {"Понедельник": "Весь день математика"}

    mocker.patch(
        "src.bot.services.schedule_service.cache_service",
        mock,
    )

    from src.bot.services.schedule_service import get_schedule_by_grade

    grade = "10А"
    result = await get_schedule_by_grade(grade)

    assert result == {"Понедельник": "Весь день математика"}


@pytest.mark.asyncio
async def test_get_schedule_by_grade_without_redis(mocker: Any) -> None:
    mock = AsyncMock()
    mock.get_schedule_from_cache.return_value = None
    mock.set_schedule_in_cache.return_value = lambda grade, schedule: None

    mocker.patch(
        "src.bot.services.schedule_service.cache_service",
        mock,
    )

    mocker.patch(
        "src.bot.services.schedule_service.ApiClient.get_grade_schedule",
        return_value=test_schedule_html,
    )

    from src.bot.services.schedule_service import get_schedule_by_grade

    grade = "10А"
    result = await get_schedule_by_grade(grade)

    assert result == {
        "Понедельник": {
            "1": {
                "cab": "137",
                "group": None,
                "name": "Разговор о важном",
                "time": "08:00 - 08:40",
            }
        }
    }


@pytest.mark.asyncio
async def test_get_schedule_by_grade_without_redis_and_html(mocker: Any) -> None:
    mock = AsyncMock()
    mock.get_schedule_from_cache.return_value = None
    mock.set_schedule_in_cache.return_value = lambda grade, schedule: None

    mocker.patch(
        "src.bot.services.schedule_service.cache_service",
        mock,
    )
    mocker.patch(
        "src.bot.services.schedule_service.ApiClient.get_grade_schedule",
        return_value=None,
    )

    from src.bot.services.schedule_service import get_schedule_by_grade

    grade = "10А"
    result = await get_schedule_by_grade(grade)

    assert result is None
