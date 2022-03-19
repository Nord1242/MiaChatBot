from pprint import pprint
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.repo import SQLAlchemyRepo


class Repository(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        session: AsyncSession = data['session']
        data['repo'] = SQLAlchemyRepo(session)
        await handler(event, data)
        data.pop('repo')
