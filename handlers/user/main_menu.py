from aiogram_dialog import DialogManager, StartMode
from loader import dp
from states.all_state import MenuStates, RandomDialogStates, ThemeDialogStates
from aiogram import types
from queue import Queue
from utils.analytics import NamedEventPre
from aioredis.client import Redis


@dp.message(commands={'start', 'menu'})
async def start_handler(message: types.Message, dialog_manager: DialogManager, objects_queue: Queue):
    objects_queue.put(NamedEventPre(event="Команда /start"))
    current_context = dialog_manager.current_context()
    if current_context and current_context.start_data:
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
    conn: Redis = dialog_manager.data.get('redis_conn')
    await conn.lrem('random_users', count=1, value=message.from_user.id)
    await conn.hdel("user_theme", message.from_user.id)
    await conn.hdel("user_theme_top", message.from_user.id)
    await dialog_manager.start(MenuStates.main_menu, mode=StartMode.RESET_STACK)
