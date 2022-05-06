from states.all_state import MenuStates, BuyStates, ThemeDialogStates, RandomDialogStates
from aiogram_dialog import DialogManager, StartMode
from aiogram import types
from aiogram_dialog.widgets.kbd import Button
from typing import Any
from aioredis.client import Redis
from aiogram.types import CallbackQuery


async def start_buy_sub(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager):
    await dialog_manager.start(state=BuyStates.buy_subscription)


async def show_sub_info(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager):
    await dialog_manager.start(state=BuyStates.show_sub_info)


async def return_menu(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager):
    await dialog_manager.start(state=MenuStates.main_menu)


async def go_in_dialog_menu(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager):
    await dialog_manager.start(state=ThemeDialogStates.dialog_menu)


async def go_in_create_theme(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager):
    await dialog_manager.start(state=ThemeDialogStates.write_theme)


async def go_in_sub_data(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager):
    await dialog_manager.start(state=BuyStates.show_sub_info)

