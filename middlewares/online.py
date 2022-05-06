from pprint import pprint
from typing import Any, Awaitable, Callable, Dict
from queue import Queue
from repositories.repo import SQLAlchemyRepo
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from utils.analytics import UserOnlinePre
from aiogram_dialog import DialogManager

class OnlineMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        telegram_user = data.get('event_chat')
        objects_queue: Queue = data.get("objects_queue")
        objects_queue.put(UserOnlinePre(telegram_user.id))
        await handler(event, data)
