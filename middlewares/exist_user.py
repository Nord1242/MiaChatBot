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
        text = "📝 Хотим сообщить об обновление нашего чат-бота!\n\n" \
               "Вот список некоторых изменений:\n" \
               "- внедрены категории, они помогут находить людей с общими интересами и сделают поиск более приятным ☺️\n"\
               "- добавлена кнопка '🔄 Обновить', которая отображает только актуальные темы 🔥\n"\
               "- улучшен способ отображение названия тем на странице поиска, это позволит более " \
               "четко выражать критерии для поиска собеседника🔍\n\n"\
               "🌀 Новая функция для премиум пользователей:\n"\
               "- теперь, под темой и во время диалога, будет показан пол пользователя 🚹🚺\n\n"\
               "В честь этого, мы делает 25% скидку на приобретение" \
               "подписки, успейте забрать этот подарок ❤️‍🔥\n\n"\
               "На этом всё, хорошего времяпровождения в нашем чат-боте, спасибо, что вы всё ещё с нами! 😉"
        # st = StorageKey(bot_id=bot.id, chat_id=chat, user_id=telegram_user.id, destiny=DEFAULT_DESTINY)
        # ss = await red.get_state(bot=bot, key=st)
        if user is None:
            user = await repo.get_repo(UserRepo).add_user(
                user_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,

            )
            await bot.send_message(chat_id=telegram_user.id, text=text)
        data['user'] = user
        result = await handler(event, data)
        data.pop('user')
        return result
