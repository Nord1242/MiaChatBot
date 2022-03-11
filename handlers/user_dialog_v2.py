from aiogram.dispatcher.fsm.storage.base import BaseStorage, StorageKey
from aiogram_dialog import DialogManager, StartMode, Dialog
from aiogram_dialog.widgets.kbd import Button
from states.dialog_state import DialogState
from models.models import ThemeTable
from loader import dp, bot
from loader import session
from aiogram import types
from typing import Any
import random


@dp.message(commands={'start'})
async def test_handler(message: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(DialogState.main_menu, mode=StartMode.RESET_STACK)


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


async def join_in_dialog(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager, theme_id: str,
                         fsm_context: BaseStorage):
    session.query(ThemeTable).filter(ThemeTable.telegram_user_id == call.from_user.id).delete()
    session.commit()
    companion = int(theme_id)
    user_id = call.from_user.id
    dialog_manager.current_context().dialog_data["companion_id"] = companion
    storage_kwargs = {
        'storage_key': {
            'user_id': companion,
            'chat_id': companion,
            'bot_id': bot.id},
        'state_none': None,
        'state_in_dialog': DialogState.in_dialog
    }
    print(fsm_context.set_state(bot=bot, key=StorageKey(**storage_kwargs['storage_key']), state=DialogState.in_dialog))
