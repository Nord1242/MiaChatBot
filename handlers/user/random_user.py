from aiogram_dialog import DialogManager, StartMode
from aiogram import types
from typing import Any
import random
from loader import redis_connect
from database.models import Users
from states.all_state import RandomDialogStates
from aioredis.client import Redis
from utils.analytics import NamedEventPre
from aiogram import Bot
from loader import dp


# from .dialog_utils import cancel_dialog_command

async def get_companion_gender(dialog_manager: DialogManager, **kwargs):
    show_gender = {"male": "🚹", "fem": "🚺"}
    companion_gender = dialog_manager.current_context().start_data.get('companion_gender')
    if 'user' in dialog_manager.data:
        user: Users = dialog_manager.data['user']
        sub = user.product_date_end
    else:
        user_id = dialog_manager.current_context().start_data.get('user_id')
        async with redis_connect.client() as conn:
            sub = await conn.hget(f"{user_id}_data", key="sub")
    return {
        "sub": sub,
        "companion_gender": show_gender[companion_gender]
    }


async def search_random_user(call: types.CallbackQuery, widget: Any = None, dialog_manager: DialogManager = None,
                             conn: Redis = None):
    objects_queue = dialog_manager.data.get("objects_queue")
    user: Users = dialog_manager.data.get('user')
    user_id = call.from_user.id
    current_context = dialog_manager.current_context()
    male = await conn.lrange(name='male_random_users', start=0, end=-1)
    fem = await conn.lrange(name='fem_random_users', start=0, end=-1)
    all_users = male + fem
    companion_id = int(random.choice(all_users)) if all_users else None
    if all_users and call.from_user.id != companion_id:
        gender = 'male'
        if companion_id in fem:
            gender = 'fem'
        search_gender = await conn.hget(f'{companion_id}_data', "search_gender")
        if search_gender:
            search_gender = search_gender.decode('utf-8')
        objects_queue.put(NamedEventPre(event="Рандомный пользователь найден"))
        if not search_gender or search_gender == user.gender:
            await conn.lrem(name=f'{gender}_random_users', count=1, value=companion_id)
            await connect_random_user(dialog_manager, user_id, companion_id, conn, user, gender)
            return
        # else:
        #     await call.answer(show_alert=True, text="Пользователь уже нашел собеседника!!")
    await add_random_user(dialog_manager, conn, user_id, objects_queue, user, all_users)


async def search_random_gender_user(call: types.CallbackQuery, widget: Any = None,
                                    dialog_manager: DialogManager = None, gender: bytes = None, conn: Redis = None):
    objects_queue = dialog_manager.data.get("objects_queue")
    user: Users = dialog_manager.data.get('user')
    user_id = call.from_user.id
    search_gender = gender.decode('utf-8')
    users = await conn.lrange(name=f'{search_gender}_random_users', start=0, end=-1)
    # await cancel_dialog_command(dialog_manager, current_context)
    companion_id = int(random.choice(users)) if users else None
    if users and call.from_user.id != companion_id:
        objects_queue.put(NamedEventPre(event="Рандомный пользователь найден"))
        await conn.lrem(name=f'{search_gender}_random_users', count=1, value=companion_id)
        await connect_random_user(dialog_manager, user_id, companion_id, conn, user, gender=search_gender)
        return
    await add_random_user(dialog_manager=dialog_manager, conn=conn, user_id=user_id, objects_queue=objects_queue,
                          user=user, users_list=users)


async def add_random_user(dialog_manager: DialogManager, conn: Redis, user_id: int, objects_queue, user: Users,
                          users_list: list):
    user_id_bytes = str(user_id).encode('utf-8')
    await conn.lpush(f'{user.gender}_random_users', user_id)
    if user.product_date_end:
        await conn.hset(f"{user_id}_data", key="sub", value=str(user.product_date_end))
    await conn.hset(f"{user_id}_data", key="state", value=RandomDialogStates.waiting_user.__str__())
    objects_queue.put(NamedEventPre(event="Поиск рандомного пользователя"))
    await dialog_manager.start(state=RandomDialogStates.waiting_user)


async def connect_random_user(dialog_manager: DialogManager, user_id: int, companion_id: int, conn: Redis, user: Users,
                              gender=None):
    companion_manager = dialog_manager.bg(user_id=companion_id, chat_id=companion_id)
    bot: Bot = dialog_manager.data.get('bot')
    await dialog_manager.start(RandomDialogStates.in_dialog, mode=StartMode.RESET_STACK,
                               data={"companion_id": companion_id, "companion_gender": gender})
    await conn.hdel('companion_data', str(companion_id))
    await companion_manager.start(RandomDialogStates.in_dialog, mode=StartMode.RESET_STACK,
                                  data={'companion_id': user_id, "companion_gender": user.gender,
                                        "user_id": companion_id})
