from repositories.repo import SQLAlchemyRepo
from repositories.user_repo import UserRepo
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message
from typing import Any, Awaitable, Callable, Dict
from datetime import datetime
from utils.analytics import UniqueUserChannelPre
from queue import Queue
from database.models import Users
from aioredis.client import Redis

class CheckUserTime(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message or CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        repo: SQLAlchemyRepo = data['repo']
        user_repo: UserRepo = repo.get_repo(UserRepo)
        user: Users = data['user']
        conn: Redis = data['redis_conn']
        time_ban = user.time_ban
        now_date = datetime.utcnow()
        if user:
            if user.product_date_end:
                if now_date > user.product_date_end:
                    await user_repo.delete_sub(user.telegram_user_id)
                    await conn.hdel(f"{user.telegram_user_id}_data", "sub")
                    await conn.hdel(f"{user.telegram_user_id}_data", "search_gender")
                    user.product_date_end = None

            if user.top_date_end:
                if now_date > user.top_date_end:
                    await user_repo.delete_top(user_id=user.telegram_user_id)
                    user.top = False
            if time_ban:
                if now_date > time_ban:
                    await user_repo.delete_time_ban(user_id=user.telegram_user_id)
                data['user'] = user
        result = await handler(event, data)
        return result
