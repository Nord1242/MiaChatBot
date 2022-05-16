from database.models import Users
from states.all_state import MenuStates, BuyStates, ThemeDialogStates, RandomDialogStates
from aiogram_dialog import DialogManager, StartMode
from aiogram import types
from aiogram_dialog.widgets.kbd import Button
from typing import Any
from aioredis.client import Redis
from aiogram.types import CallbackQuery
from loader import dp
from handlers.user.random_user import search_random_user, search_random_gender_user


@dp.message(commands={'buysub'})
async def start_buy_sub(call: types.CallbackQuery, widget: Any = None, dialog_manager: DialogManager = None):
    user: Users = dialog_manager.data['user']
    if not user.product_date_end:
        await dialog_manager.start(state=BuyStates.buy_subscription)
    else:
        await dialog_manager.start(state=BuyStates.show_sub_info)


async def show_sub_info(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager):
    await dialog_manager.start(state=BuyStates.show_sub_info)


async def return_menu(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager):
    await dialog_manager.start(state=MenuStates.main_menu)


@dp.message(commands={'search'})
async def return_to_search_theme(call: types.CallbackQuery, widget: Any = None, dialog_manager: DialogManager = None):
    await dialog_manager.start(state=ThemeDialogStates.search_theme)


@dp.message(commands={'changegender'})
async def go_to_change_gender_menu(call: types.CallbackQuery, widget: Any = None, dialog_manager: DialogManager = None):
    await dialog_manager.start(RandomDialogStates.get_menu_gender)


async def go_in_create_theme(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager):
    await dialog_manager.start(state=ThemeDialogStates.write_theme)


async def go_in_sub_data(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager):
    await dialog_manager.start(state=BuyStates.show_sub_info)


@dp.message(commands={'random'})
async def check_sub_random(call: types.CallbackQuery, widget: Any = None, dialog_manager: DialogManager = None):
    conn: Redis = dialog_manager.data.get('redis_conn')
    user: Users = dialog_manager.data.get('user')
    if user.product_date_end:
        search_gender = await conn.hget(f'{call.from_user.id}_data', "search_gender")
        if search_gender:
            await search_random_gender_user(call, widget, dialog_manager, search_gender, conn)
            return
        await dialog_manager.start(RandomDialogStates.get_gender)
    else:
        await search_random_user(call=call, dialog_manager=dialog_manager, widget=widget, conn=conn)


async def check_gender(call: types.CallbackQuery, widget: Any = None, dialog_manager: DialogManager = None):
    conn: Redis = dialog_manager.data.get('redis_conn')
    search_gender = await conn.hget('search_gender', str(call.from_user.id))
    if search_gender:
        await search_random_gender_user(call=call, widget=widget, dialog_manager=dialog_manager, gender=search_gender,
                                        conn=conn)
        return
    else:
        await search_random_user(call=call, widget=widget, dialog_manager=dialog_manager, conn=conn)
