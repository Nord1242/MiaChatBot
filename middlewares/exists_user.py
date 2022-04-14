from repositories.repo import SQLAlchemyRepo
from repositories.user_repo import UserRepo
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message
from typing import Any, Awaitable, Callable, Dict
from typing import Union
from datetime import datetime
from analytics import UniqueUserPre
from queue import Queue
from pprint import pprint


class ExistsUser(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message or CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        telegram_user = data.get('event_chat')
        objects_queue: Queue = data.get("objects_queue")
        repo: SQLAlchemyRepo = data['repo']
        user = await repo.get_repo(UserRepo).get_user(telegram_user.id)
        if user is None:
            objects_queue.put(UniqueUserPre())
            user = await repo.get_repo(UserRepo).add_user(
                user_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name
            )
        data['user'] = user
        result = await handler(event, data)

        data.pop('user')
        return result
