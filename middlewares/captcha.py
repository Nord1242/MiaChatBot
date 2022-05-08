from repositories.repo import SQLAlchemyRepo
from repositories.user_repo import UserRepo
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message
from typing import Any, Awaitable, Callable, Dict
from datetime import datetime
from aiogram_dialog import DialogManager
from database.models import Users
from states.all_state import MenuStates


class CheckCaptcha(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message or CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        repo: SQLAlchemyRepo = data['repo']
        user_repo: UserRepo = repo.get_repo(UserRepo)
        user: Users = data['user']
        now_date = datetime.utcnow()
        dialog_manager: DialogManager = data['dialog_manager']
        if user:
            if not user.is_human:
                counter = None
                context = dialog_manager.current_context()
                if context:
                    start_data = context.start_data
                    if start_data:
                        counter = dialog_manager.current_context().start_data.get("counter")
                await dialog_manager.start(state=MenuStates.captcha, data={"counter": counter})
            elif not user.gender:
                await dialog_manager.start(state=MenuStates.gender)
            elif user.is_human:
                result = await handler(event, data)
                return result
