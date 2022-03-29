import datetime
from queue import Queue
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.types import TelegramObject, Message, CallbackQuery

from analytics import RawUpdatePre


class LogUpdatesMiddleware(BaseMiddleware):

    def __init__(self):
        super().__init__()

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        objects_queue: Queue = data.get("objects_queue")

        result = await handler(event, data)
        event_datetime = datetime.datetime.utcnow()
        if isinstance(event, Message):
            event_datetime = event.date
        elif isinstance(event, CallbackQuery) and event.message is not None:
            event_datetime = event.message.date

        objects_queue.put(RawUpdatePre(is_handled=result is not UNHANDLED))
        return result
