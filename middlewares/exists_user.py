from repositories.repo import SQLAlchemyRepo
from repositories.user_repo import UserRepo
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message
from typing import Any, Awaitable, Callable, Dict
from typing import Union
from datetime import datetime
from analytics import NamedEventPre
from queue import Queue


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
        start_time = datetime.now()
        user = await repo.get_repo(UserRepo).get_user(telegram_user.id)
        if user is None:
            user = await repo.get_repo(UserRepo).add_user(
                user_id=telegram_user.id,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
                username=telegram_user.username,
                start_date=start_time
            )
            objects_queue.put(NamedEventPre(event="Уникальный пользователь"))
        data['user'] = user
        result = await handler(event, data)

        # data.pop('user')
        # return result
