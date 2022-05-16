from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message
from typing import Any, Awaitable, Callable, Dict
from aioredis.client import Redis

from database.models import Users
from datetime import datetime


class SetExpire(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message or CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        result = await handler(event, data)
        user: Users = data['user']
        conn: Redis = data['redis_conn']
        await conn.expire(f"{user.telegram_user_id}_data", 86400)

