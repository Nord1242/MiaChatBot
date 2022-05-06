from pprint import pprint

from aiogram import BaseMiddleware
from typing import Any, Awaitable, Callable, Dict
from aiogram.types import TelegramObject
from sqlalchemy.orm import sessionmaker
from aiogram_dialog import DialogManager
from aioredis.client import Redis


class GetConnectionToRedis(BaseMiddleware):

    def __init__(self, redis_conn: Redis):
        self.redis_conn = redis_conn

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]):
        async with self.redis_conn.client() as conn:
            data['redis_conn'] = conn
            await handler(event, data)
            data.pop('redis_conn')
