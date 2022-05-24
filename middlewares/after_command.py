from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message
from typing import Any, Awaitable, Callable, Dict
from aiogram_dialog import DialogManager, StartMode
from aioredis.client import Redis

from database.models import Users
from states.all_state import ThemeDialogStates, RandomDialogStates


class CancelDialog(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message or CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        user: Users = data['user']
        dialog_manager: DialogManager = data['dialog_manager']
        current_context = dialog_manager.current_context()
        commands = ['/random', '/menu', '/search', '/create', '/buysub']
        command = None
        conn: Redis = data['redis_conn']
        await conn.lrem(f'{user.gender}_random_users', count=1, value=user.telegram_user_id)
        await conn.hdel("user_theme_top", str(user.telegram_user_id))
        await conn.hdel('adult', str(user.telegram_user_id))
        await conn.hdel('dating', str(user.telegram_user_id))
        await conn.hdel('commun', str(user.telegram_user_id))
        if isinstance(event, Message):
            command = event.text
        if current_context and current_context.start_data and command in commands:
            state = current_context.state
            companion_id = current_context.start_data.get("companion_id")
            companion_manager = dialog_manager.bg(user_id=companion_id, chat_id=companion_id)
            state_switch = None
            if state == ThemeDialogStates.in_dialog_theme:
                state_switch = ThemeDialogStates.cancel_theme
            elif state == RandomDialogStates.in_dialog:
                state_switch = RandomDialogStates.cancel
            if state_switch:
                await companion_manager.start(state_switch, mode=StartMode.RESET_STACK,
                                              data={"text": "Собеседник завершил диалог"})
        result = await handler(event, data)
        return result
