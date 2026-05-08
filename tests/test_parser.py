from src.bot.utils.parser import parse_changes_url, parse_schedule, parse_changes_table_rows
from unittest.mock import AsyncMock

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

correct_test_schedule = {
    "Понедельник": {
        "1": {
            "time": "08:00 - 08:40",
            "name": "Разговор о важном",
            "group": None,
            "cab": "137",
        }
    }
}

test_changes_html = """<!DOCTYPE html>
<html>
    <body>
        <li class="menu-item menu-item-type-custom menu-item-object-custom menu-item-5101"><a href="https://example.com">Ссылка</a></li>
    </body>
</html>"""


def test_parse_schedule_valid() -> None:
    schedule = parse_schedule(test_schedule_html)
    assert schedule == correct_test_schedule


def test_parse_schedule_invalid() -> None:
    schedule = parse_schedule(None)
    assert schedule is None


def test_parse_changes_url_valid() -> None:
    url = parse_changes_url(test_changes_html)
    assert url == "https://example.com"


def test_parse_changes_url_invalid() -> None:
    url = parse_changes_url(None)
    assert url is None


def test_parse_changes_table_rows() -> None:
    test_data = [
        ["", "", "", "", "", ""],
        ["", "", "01.01.2026", "", "", ""],
        ["Урок", "Класс", "Предмет", "Заменяющий учитель", "Предмет", "Кабинет"],
        ["1", "7Д", "Разговоры о важном", "нет", "", ""], 
        ["2", "7Д", "Математика", "Иванов И.И.", "Математика", "101"],
    ]

    correct_test_data = {"01.01.2026": {"7д": [{"lesson_num": "1", "subject_orig": "Разговоры о важном", "subject_new": "", "teacher": "нет", "room": ""}, {"lesson_num": "2", "subject_orig": "Математика", "subject_new": "Математика", "teacher": "Иванов И.И.", "room": "101"}]}}

    changes = parse_changes_table_rows(test_data)
    assert changes == correct_test_data


import pytest
from src.bot.utils.parser import get_changes_url, get_changes_table_rows

@pytest.mark.asyncio
async def test_get_changes_url_success(mocker):
    mock_html = "<html><body>Some content</body></html>"
    mock_url = "https://docs.google.com/spreadsheets/d/123/edit"
    
    mock_get_page = mocker.patch("src.bot.utils.parser.ApiClient.get_main_page", return_value=mock_html)
    mock_parse = mocker.patch("src.bot.utils.parser.parse_changes_url", return_value=mock_url)
    
    result = await get_changes_url()
    
    assert result == mock_url
    mock_get_page.assert_called_once()
    mock_parse.assert_called_once_with(mock_html)

@pytest.mark.asyncio
async def test_get_changes_url_main_page_fail(mocker):
    mocker.patch("src.bot.utils.parser.ApiClient.get_main_page", return_value=None)
    
    result = await get_changes_url()
    
    assert result is None

@pytest.mark.asyncio
async def test_get_changes_url_exception(mocker):
    mocker.patch("src.bot.utils.parser.ApiClient.get_main_page", side_effect=Exception("Network error"))
    
    result = await get_changes_url()
    
    assert result is None

@pytest.mark.asyncio
async def test_get_changes_table_rows_success(mocker):
    mock_url = "https://docs.google.com/spreadsheets/d/123/edit"
    expected_download_url = "https://docs.google.com/spreadsheets/d/123/export?format=csv"
    mock_csv_text = "col1,col2\nval1,val2"
    mock_rows = [["col1", "col2"], ["val1", "val2"]]
    
    mocker.patch("src.bot.utils.parser.get_changes_url", return_value=mock_url)
    mock_get_file = mocker.patch("src.bot.utils.parser.ApiClient.get_file", return_value=mock_csv_text)
    mock_get_changes = mocker.patch("src.bot.utils.parser.get_changes", return_value=mock_rows)
    
    result = await get_changes_table_rows()
    
    assert result == mock_rows
    mock_get_file.assert_called_once_with(expected_download_url)
    mock_get_changes.assert_called_once_with(mock_csv_text)

@pytest.mark.asyncio
async def test_get_changes_table_rows_url_fail(mocker):
    mocker.patch("src.bot.utils.parser.get_changes_url", return_value=None)
    
    result = await get_changes_table_rows()
    
    assert result is None

@pytest.mark.asyncio
async def test_get_changes_table_rows_empty_csv(mocker):
    mocker.patch("src.bot.utils.parser.get_changes_url", return_value="https://some-url.com/edit")
    mocker.patch("src.bot.utils.parser.ApiClient.get_file", return_value=None)
    
    result = await get_changes_table_rows()
    
    assert result is None

@pytest.mark.asyncio
async def test_get_changes_table_rows_exception(mocker):
    mocker.patch("src.bot.utils.parser.get_changes_url", side_effect=RuntimeError("Unexpected error"))
    
    result = await get_changes_table_rows()
    
    assert result is None
