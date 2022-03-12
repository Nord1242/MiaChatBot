from aiogram.dispatcher.fsm.storage.base import BaseStorage, StorageKey
from aiogram_dialog import DialogManager, StartMode, Dialog
from aiogram_dialog.widgets.kbd import Button
from states.dialog_state import AllStates
from models.models import ThemeTable
from loader import dp, bot
from loader import session
from aiogram import types
from typing import Any
import random


@dp.message(commands={'start'})
async def test_handler(message: types.Message, dialog_manager: DialogManager):
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
    all_themes = ThemeTable.get_all_theme()
    random.shuffle(all_themes)
    themes_buttons = list()
    for theme in all_themes:
        themes_buttons.append(
            (theme.theme_name,
             theme.telegram_user_id)
        )
    return {
        "themes_buttons": themes_buttons
    }


async def join_in_dialog(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager, theme_id: str):
    companion = int(theme_id)
    user_id = call.from_user.id
    session.query(ThemeTable).filter(ThemeTable.telegram_user_id == companion).delete()
    session.commit()
    companion_manager = dialog_manager.bg(user_id=companion, chat_id=companion)
    await companion_manager.update(data={'companion_id': user_id})
    dialog_manager.current_context().dialog_data.update(companion_id=companion)
    await companion_manager.start(AllStates.in_dialog)
    await dialog_manager.dialog().switch_to(state=AllStates.in_dialog)


async def get_text_for_window(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.current_context().dialog_data.get('user_id')
    companion_id = dialog_manager.current_context().dialog_data.get('companion_id')
    if user_id == companion_id:
        return {"text": "Пользователь найден"}
    else:
        return {"text": "Добро пожаловать в чат"}


async def cancel_dialog(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager):
    dialog_manager.current_context().dialog_data.update(user_id=call.from_user.id)
    companion_id = dialog_manager.current_context().dialog_data.get("companion_id")
    print(dialog_manager.current_context().dialog_data)
    # print(f"{call.from_user.id}\ncompanion_id: {companion_id}")
    # await dialog_manager.bg(chat_id=companion_id, user_id=companion_id, load=True).start(AllStates.cancel)
    # await dialog_manager.dialog().next()

# async def who_cancel_dialog(dialog_manager: DialogManager, **kwargs):
#     user_id = dialog_manager.current_context().dialog_data.get('user_id')
#     companion_id = dialog_manager.current_context().dialog_data.get('companion_id')
#     if user_id == companion_id:
#         return {"text": "Пользователь завершли чат"}
#     else:
#         return {"text": "Вы завершили чат"}
