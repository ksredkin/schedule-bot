from collections.abc import Awaitable, Callable
from typing import Any

from maxapi.filters.middleware import BaseMiddleware
from typing import Any, Awaitable, Callable, Dict
from maxapi.types import UpdateUnion
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class DatabaseSessionMiddleware(BaseMiddleware):
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        self.sessionmaker = sessionmaker

    async def __call__(
        self,
        handler: Callable[[UpdateUnion, Dict[str, Any]], Awaitable[Any]],
        event_object: UpdateUnion,
        data: dict[str, Any],
    ) -> Any:
        session: AsyncSession = self.sessionmaker()
        data["db_session"] = session
        try:
            await handler(event_object, data)
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
