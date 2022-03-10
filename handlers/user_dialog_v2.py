import random
from loader import dp, bot
from aiogram import types
from aiogram_dialog import DialogManager, StartMode, Dialog
from aiogram_dialog.widgets.text import Const
from states.dialog_state import DialogState
from models.models import ThemeTable
from loader import session
from aiogram_dialog.widgets.kbd import Select


@dp.message(commands={'start'})
async def test_handler(message: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(DialogState.main_menu, mode=StartMode.RESET_STACK)


async def create_dialog(message: types.Message, dialog: Dialog, dialog_manager: DialogManager, ):
    last_message_id = dialog_manager.current_stack().last_message_id
    theme_name = message.text
    user_id = message.from_user.id
    new_theme = ThemeTable(theme_name=theme_name, telegram_user_id=message.from_user.id)
    session.add(new_theme)
    session.commit()
    await bot.delete_message(chat_id=user_id, message_id=last_message_id)
    await dialog.next()


async def delete_theme(call: types.CallbackQuery, button: Button, manager: DialogManager):
    session.query(ThemeTable).filter(ThemeTable.telegram_user_id == call.from_user.id).delete()
    session.commit()


async def suggested_themes():
    all_themes = ThemeTable.get_all_theme()
    random.shuffle(all_themes)
    themes_button = list()
    for theme in all_themes:
        themes_button.append(
            Select(
                Const(f"{theme.theme_name}"),
                id=theme.telegram_user_id
            )
        )
    return themes_button


