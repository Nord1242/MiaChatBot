from pprint import pprint

from repositories.repo import SQLAlchemyRepo
from repositories.user_repo import UserRepo
from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, CallbackQuery, Message
from typing import Any, Awaitable, Callable, Dict
from datetime import datetime

from states.all_state import MenuStates
from utils.analytics import UniqueUserPre
from queue import Queue
from database.models import Users
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from aiogram.dispatcher.fsm.storage.base import StorageKey, DEFAULT_DESTINY
from aiogram_dialog import DialogManager


class ExistsUser(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message or CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        red: RedisStorage = data.get('fsm_storage')
        bot: Bot = data.get('bot')
        # chat = event.chat.id
        dialog_manager: DialogManager = data['dialog_manager']
        telegram_user = data.get('event_chat')
        objects_queue: Queue = data.get("objects_queue")
        repo: SQLAlchemyRepo = data['repo']
        user_repo: UserRepo = repo.get_repo(UserRepo)
        user: Users = await user_repo.get_user(telegram_user.id)
        # st = StorageKey(bot_id=bot.id, chat_id=chat, user_id=telegram_user.id, destiny=DEFAULT_DESTINY)
        # ss = await red.get_state(bot=bot, key=st)
        if user is None:
            user = await repo.get_repo(UserRepo).add_user(
                user_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,

            )
            objects_queue.put(UniqueUserPre())
        data['user'] = user
        result = await handler(event, data)
        data.pop('user')
        return result
