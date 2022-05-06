from database.models import Users
from states.all_state import MenuStates, BuyStates, ThemeDialogStates, RandomDialogStates
from aiogram_dialog import DialogManager, StartMode
from aiogram import types
from aiogram_dialog.widgets.kbd import Button
from typing import Any
from aioredis.client import Redis
from aiogram.types import CallbackQuery
from loader import dp


@dp.message(commands={'buysub'})
async def start_buy_sub(call: types.CallbackQuery, widget: Any=None, dialog_manager: DialogManager=None):
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


async def go_in_create_theme(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager):
    await dialog_manager.start(state=ThemeDialogStates.write_theme)


async def go_in_sub_data(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager):
    await dialog_manager.start(state=BuyStates.show_sub_info)
