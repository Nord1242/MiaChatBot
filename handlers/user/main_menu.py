from aiogram_dialog import DialogManager, StartMode
from loader import dp
from states.all_state import MenuStates, RandomDialogStates, ThemeDialogStates
from aiogram import types
from queue import Queue
from utils.analytics import NamedEventPre
# from .dialog_utils import cancel_dialog_command
from aioredis.client import Redis


@dp.message(commands={'start', 'menu'})
async def start_handler(message: types.Message, dialog_manager: DialogManager, objects_queue: Queue):
    objects_queue.put(NamedEventPre(event="Команда /start"))
    conn: Redis = dialog_manager.data.get('redis_conn')
    current_context = dialog_manager.current_context()
    # await cancel_dialog_command(dialog_manager, current_context)
    await conn.lrem('random_users', count=1, value=message.from_user.id)
    await conn.hdel("user_theme", message.from_user.id)
    await conn.hdel("user_theme_top", message.from_user.id)
    await dialog_manager.start(MenuStates.main_menu, mode=StartMode.RESET_STACK)
