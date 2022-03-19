from pprint import pprint

from aiogram import BaseMiddleware
from typing import Any, Awaitable, Callable, Dict
from aiogram.types import TelegramObject
from loader import async_sessionmaker
from typing import Union
from sqlalchemy.orm import sessionmaker


class GetConnectionToDB(BaseMiddleware):

    def __init__(self, sm: sessionmaker):
        self.session = sm

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]):
        async with self.session() as session:
            async with self.session.begin():
                data['session'] = session
                await handler(event, data)
                data.pop('session')
