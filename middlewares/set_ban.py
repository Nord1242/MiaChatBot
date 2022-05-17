from repositories.repo import SQLAlchemyRepo
from repositories.user_repo import UserRepo
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message
from typing import Any, Awaitable, Callable, Dict
from utils.analytics import UniqueUserChannelPre
from queue import Queue
from database.models import Users
from aiogram_dialog import DialogManager


class SetUserBan(BaseMiddleware):

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
            product_date_end = user.product_date_end
            complaints = user.complaints
            if user.attempts == 0:
                await user_repo.set_ban(user.telegram_user_id,
                                        ban_info="исчерпано максимальное количество попыток для прохождения анти-спам защиты 🤖")
            for complaint in complaints:
                counter = complaint.counter
                if counter >= 5 and complaint.complaint == "CP":
                    user.ban = True
                    await user_repo.set_ban(user.telegram_user_id, ban_info=complaint.complaint)
                elif product_date_end and complaint.complaint != "CP" and counter >= 8:
                    user.sub_ban = True
                    await user_repo.set_sub_ban(user.telegram_user_id, ban_info=complaint.complaint)
                elif counter >= 5 and not product_date_end:
                    user.ban = True
                    await user_repo.set_ban(user.telegram_user_id, ban_info=complaint.complaint)

        data['user'] = user
        result = await handler(event, data)
        return result
