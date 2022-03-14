from aiogram.dispatcher.fsm.storage.base import BaseStorage, StorageKey
from aiogram_dialog import DialogManager, StartMode, Dialog
from aiogram_dialog.manager.protocols import ShowMode
from aiogram_dialog.widgets.kbd import Button
from states.dialog_state import AllStates
from database.models import ThemeTable
from loader import dp, bot
from loader import session
from aiogram import types
from typing import Any
import random


@dp.message(commands={'start'})
async def test_handler(message: types.Message, dialog_manager: DialogManager):
    last_message_id = dialog_manager.current_stack().last_message_id
    if last_message_id:
        await bot.delete_message(chat_id=message.from_user.id, message_id=last_message_id)
    await dialog_manager.start(AllStates.main_menu, mode=StartMode.RESET_STACK)


async def get_user_id(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager):
    dialog_manager.current_context().dialog_data.update(user_id=call.from_user.id)


async def create_dialog(message: types.Message, dialog: Dialog, dialog_manager: DialogManager):
    last_message_id = dialog_manager.current_stack().last_message_id
    theme_name = message.text
    user_id = message.from_user.id
    new_theme = ThemeTable(theme_name=theme_name, telegram_user_id=message.from_user.id)
    session.add(new_theme)
    session.commit()
    await bot.delete_message(chat_id=user_id, message_id=last_message_id)
    await dialog.next()


async def cancel_search(call: types.CallbackQuery, button: Button, manager: DialogManager):
    session.query(ThemeTable).filter(ThemeTable.telegram_user_id == call.from_user.id).delete()
    session.commit()


async def suggested_themes(**kwargs):
    all_themes = []
    themes_buttons = list()
    for theme in all_themes:
        themes_buttons.append(
            (theme.theme_name,
             theme.telegram_user_id)
        )
    return {
        "themes_buttons": themes_buttons
    }


async def join_in_dialog(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager, companion_id: str):
    user_id = call.from_user.id
    companion_id = int(companion_id)
    session.query(ThemeTable).filter(ThemeTable.telegram_user_id == companion_id).delete()
    session.commit()
    companion_manager = dialog_manager.bg(user_id=companion_id, chat_id=companion_id)
    await companion_manager.start(AllStates.in_dialog, mode=StartMode.NORMAL,
                                  data={'companion_id': user_id, "text": "Пользователь найден!"})
    await dialog_manager.start(AllStates.in_dialog, mode=StartMode.NORMAL,
                               data={"companion_id": companion_id, "text": "Добро пожаловать в чат!"})


async def text_join_in_dialog(dialog_manager: DialogManager, **kwargs):
    text = dialog_manager.current_context().start_data.get('text')
    return {"text": text}


async def cancel_dialog(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager):
    companion_id = dialog_manager.current_context().start_data.get("companion_id")
    companion_manager = dialog_manager.bg(user_id=companion_id, chat_id=companion_id)
    await dialog_manager.start(AllStates.cancel, mode=StartMode.NORMAL, data={"text": "Вы завершили диалог"})
    await companion_manager.start(AllStates.cancel, mode=StartMode.NORMAL, data={"text": "Собеседник зввершил диалог"})


async def who_cancel_dialog(dialog_manager: DialogManager, **kwargs):
    text = dialog_manager.current_context().start_data.get('text')
    return {"text": text}


async def dialog(message: types.Message, dialog: Dialog, dialog_manager: DialogManager):
    companion_id = dialog_manager.current_context().start_data.get("companion_id")
    dialog_manager.show_mode = ShowMode.EDIT
    await message.copy_to(chat_id=companion_id)


async def restart_dialog_menu(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager):
    await dialog_manager.start(AllStates.cancel, mode=StartMode.RESET_STACK)
