import pytest
import respx
from httpx import Response


@pytest.mark.asyncio
@respx.mock
async def test_get_grade_schedule():
    from src.bot.utils.api_client import ApiClient

    url = "https://vplicei.org/?page_id=465"
    respx.post(url).mock(
        return_value=Response(status_code=200, text="<html>Расписание для 10А</html>")
    )

    grade = "10А"
    result = await ApiClient.get_grade_schedule(grade)

    assert result is not None
    assert "10А" in result


@pytest.mark.asyncio
@respx.mock
async def test_get_grade_schedule_server_error():
    from src.bot.utils.api_client import ApiClient

    url = "https://vplicei.org/?page_id=465"
    respx.post(url).mock(return_value=Response(500))

    result = await ApiClient.get_grade_schedule("10A")

    assert result is None


@pytest.mark.asyncio
@respx.mock
async def test_get_grade_schedule_connection_timeout(mocker):
    url = "https://vplicei.org/?page_id=465"
    respx.post(url).side_effect = Exception("Connection timed out")

    mock_logger = mocker.patch("src.bot.utils.api_client.logger")

    from src.bot.utils.api_client import ApiClient

    grade = "10А"
    result = await ApiClient.get_grade_schedule(grade)

    assert result is None
    mock_logger.warning.assert_called()


@pytest.mark.asyncio
@respx.mock
async def test_get_main_page():
    from src.bot.utils.api_client import ApiClient

    url = "https://vplicei.org"
    respx.get(url).mock(
        return_value=Response(status_code=200, text="<html>Сайт ВМЛ</html>")
    )

    result = await ApiClient.get_main_page()

    assert result is not None
    assert "Сайт ВМЛ" in result


@pytest.mark.asyncio
@respx.mock
async def test_get_main_page_server_error():
    from src.bot.utils.api_client import ApiClient

    url = "https://vplicei.org"
    respx.get(url).mock(return_value=Response(500))

    result = await ApiClient.get_main_page()

    assert result is None


@pytest.mark.asyncio
@respx.mock
async def test_get_main_page_connection_timeout(mocker):
    from src.bot.utils.api_client import ApiClient

    url = "https://vplicei.org"
    respx.post(url).side_effect = Exception("Connection timed out")

    mock_logger = mocker.patch("src.bot.utils.api_client.logger")

    result = await ApiClient.get_main_page()

    assert result is None
    mock_logger.warning.assert_called()


@pytest.mark.asyncio
@respx.mock
async def test_get_file():
    from src.bot.utils.api_client import ApiClient

    url = "https://vplicei.org/get_changes_file"
    respx.get(url).mock(
        return_value=Response(status_code=200, text="<html>Замены уроков: -</html>")
    )

    result = await ApiClient.get_file(url)

    assert result is not None
    assert "Замены уроков" in result


@pytest.mark.asyncio
@respx.mock
async def test_get_file_server_error():
    from src.bot.utils.api_client import ApiClient

    url = "https://vplicei.org/get_changes_file"
    respx.get(url).mock(return_value=Response(500))

    result = await ApiClient.get_file(url)

    assert result is None


@pytest.mark.asyncio
@respx.mock
async def test_get_file_connection_timeout(mocker):
    from src.bot.utils.api_client import ApiClient

    url = "https://vplicei.org/get_changes_file"
    respx.post(url).side_effect = Exception("Connection timed out")

    mock_logger = mocker.patch("src.bot.utils.api_client.logger")

    result = await ApiClient.get_file(url)

    assert result is None
    mock_logger.warning.assert_called()
