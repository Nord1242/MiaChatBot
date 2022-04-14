from pprint import pprint

from aiogram import BaseMiddleware
from typing import Any, Awaitable, Callable, Dict
from aiogram.types import TelegramObject, CallbackQuery, Message
from aiogram_dialog import DialogManager
from states.all_state import AllStates


class StateMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message or CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        dialog_manager: DialogManager = data['dialog_manager']
        await handler(event, data)
