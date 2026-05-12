import asyncio
from typing import Any, Awaitable, Callable, Dict, List

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message


class AlbumMiddleware(BaseMiddleware):
    def __init__(self, latency: float = 0.1):
        self.latency = latency
        self.album_data: Dict[str, List[Message]] = {}
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,  # type: ignore
        data: Dict[str, Any],
    ) -> Any:
        if not event.media_group_id:
            return await handler(event, data)

        need_album = get_flag(data, "need_album", default=False)
        if not need_album:
            return await handler(event, data)

        try:
            self.album_data[event.media_group_id].append(event)
        except KeyError:
            self.album_data[event.media_group_id] = [event]

            await asyncio.sleep(self.latency)

            data["album"] = self.album_data.pop(event.media_group_id)
            return await handler(event, data)
