from aiogram_dialog import DialogManager, StartMode
from aiogram import types
from typing import Any
import random

from database.models import Users
from states.all_state import RandomDialogStates
from aioredis.client import Redis
from utils.analytics import NamedEventPre
from aiogram import Bot
from loader import dp
# from .dialog_utils import cancel_dialog_command


async def add_random_user(dialog_manager: DialogManager, conn: Redis, user_id: int, objects_queue, all_users):
    user_id_bytes = str(user_id).encode('utf-8')
    if user_id_bytes not in all_users:
        await conn.lpush('random_users', user_id)
    await conn.hset("companion_state", key=user_id, value=RandomDialogStates.waiting_user.__str__())
    objects_queue.put(NamedEventPre(event="Поиск рандомного пользователя"))
    await dialog_manager.start(state=RandomDialogStates.waiting_user)


async def connect_random_user(dialog_manager: DialogManager, user_id: int, companion_id: int, conn: Redis, user: Users):
    companion_message = await conn.hget(name='companion_data', key=str(companion_id))
    companion_manager = dialog_manager.bg(user_id=companion_id, chat_id=companion_id)
    bot: Bot = dialog_manager.data.get('bot')
    await dialog_manager.start(RandomDialogStates.in_dialog, mode=StartMode.RESET_STACK,
                               data={"companion_id": companion_id,
                                     "text": "Пользователь найден!",
                                     "random_start": True})
    await conn.hdel('companion_data', str(companion_id))
    await companion_manager.start(RandomDialogStates.in_dialog, mode=StartMode.RESET_STACK,
                                  data={'companion_id': user_id,
                                        "text": "Пользователь найден!",
                                        "random_start": True})


# @dp.message(commands={'random'})
async def search_random_user(call: types.CallbackQuery, widget: Any = None, dialog_manager: DialogManager = None):
    conn: Redis = dialog_manager.data.get('redis_conn')
    objects_queue = dialog_manager.data.get("objects_queue")
    user: Users = dialog_manager.data.get('user')
    user_id = call.from_user.id
    current_context = dialog_manager.current_context()
    # await cancel_dialog_command(dialog_manager, current_context)
    all_users = await conn.lrange(name='random_users', start=0, end=-1)
    print(all_users)
    companion_id = int(random.choice(all_users)) if all_users else None
    if all_users and call.from_user.id != companion_id:
        await conn.lrem(name='random_users', count=1, value=companion_id)
        objects_queue.put(NamedEventPre(event="Рандоиный пользователь найден"))
        companion_state = (await conn.hget(name="companion_state", key=companion_id)).decode('utf-8')
        if companion_state != RandomDialogStates.in_dialog.__str__():
            await connect_random_user(dialog_manager, user_id, companion_id, conn, user)
        else:
            await call.answer(show_alert=True, text="Пользователь уже нашел собеседника!!")
    else:
        await add_random_user(dialog_manager, conn, user_id, objects_queue, all_users)
