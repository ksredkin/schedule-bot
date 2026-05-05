from src.bot.services.cache_service import cache_service
from src.bot.utils.api_client import ApiClient
from src.bot.utils.logger import Logger
from src.bot.utils.parser import parse_schedule

logger = Logger(__name__).get_logger()


async def get_schedule_by_grade(
    grade: str,
) -> dict[str, dict[str, dict[str, str | None]]] | None:
    rasp = await cache_service.get_schedule_from_cache(grade)

    if rasp:
        logger.info(f"Расписание для класса {grade} получено из кэша")
        return rasp

    rasp_html = await ApiClient.get_grade_schedule(grade)

    if not rasp_html:
        return None

    rasp = parse_schedule(rasp_html)

    if not rasp:
        return None

    await cache_service.set_schedule_in_cache(grade, rasp)
    return rasp
