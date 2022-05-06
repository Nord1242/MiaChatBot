import datetime

from repositories.repo import SQLAlchemyRepo
from repositories.user_repo import UserRepo
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message
from typing import Any, Awaitable, Callable, Dict
from aiogram_dialog import DialogManager
from database.models import Users
from states.all_state import MenuStates, BuyStates


class CheckUserBan(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message or CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        repo: SQLAlchemyRepo = data['repo']
        user_repo: UserRepo = repo.get_repo(UserRepo)
        user: Users = data['user']
        dialog_manager: DialogManager = data['dialog_manager']
        if user:
            ban = user.ban
            sub_ban = user.sub_ban
            time_ban = user.time_ban
            text = None
            current_context = dialog_manager.current_context()
            user_state = current_context.state if current_context else None
            print(user_state)
            texts = ['/stop', '/start', '/menu']
            states = [MenuStates.ban_sub, BuyStates.buy_subscription, BuyStates.successful_payment]
            if isinstance(event, Message):
                text = event.text
            if ban or sub_ban or time_ban:
                if sub_ban:
                    switch_state = MenuStates.ban_sub
                    if text not in texts and user_state in states:
                        result = await handler(event, data)
                        return result
                elif time_ban:
                    if datetime.datetime.utcnow() < time_ban:
                        switch_state = MenuStates.time_ban
                elif ban:
                    switch_state = MenuStates.ban
                await dialog_manager.start(state=switch_state)
                return
        result = await handler(event, data)
        return result
