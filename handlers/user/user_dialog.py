from pprint import pprint

from aiogram_dialog import DialogManager, StartMode, Dialog
from aiogram_dialog.manager.protocols import ShowMode
from aiogram_dialog.widgets.kbd import Button

from loader import dp, bot, async_sessionmaker

from states.all_state import AllStates
from database.models import ThemeTable

from repositories.repo import SQLAlchemyRepo
from repositories.theme_repository import ThemeRepo
from repositories.random_user_repository import RandomUsersRepo

from aiogram import types
from typing import Any

from analytics import NamedEventPre
# async def get_user_id(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager):
#     dialog_manager.current_context().dialog_data.update(user_id=call.from_user.id)


async def create_dialog(message: types.Message, dialog: Dialog, dialog_manager: DialogManager):
    objects_queue = dialog_manager.data.get("objects_queue")
    objects_queue.put(NamedEventPre(event="Создание диалог"))
    last_message_id = dialog_manager.current_stack().last_message_id
    theme_name = message.text
    user_id = message.from_user.id
    repo: SQLAlchemyRepo = dialog_manager.data.get('repo')
    await repo.get_repo(ThemeRepo).add_theme(user_id=user_id, theme_name=theme_name)
    await bot.delete_message(chat_id=user_id, message_id=last_message_id)
    await dialog.next()


async def cancel_search(call: types.CallbackQuery, button: Button, dialog_manager: DialogManager):
    repo: SQLAlchemyRepo = dialog_manager.data.get('repo')
    if dialog_manager.current_context().dialog_data.get('random_start'):
        state = AllStates.main_menu
        await repo.get_repo(RandomUsersRepo).delete_user(user_id=call.from_user.id)
    else:
        print('ss')
        state = AllStates.dialog_menu
        await repo.get_repo(ThemeRepo).delete_theme(user_id=call.from_user.id)
    await dialog_manager.switch_to(state=state)


async def suggested_themes(dialog_manager: DialogManager, **kwargs):
    repo: SQLAlchemyRepo = dialog_manager.data.get('repo')
    all_themes = await repo.get_repo(ThemeRepo).get_all_themes()
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
    objects_queue = dialog_manager.data.get("objects_queue")
    objects_queue.put(NamedEventPre(event="Присоединение к диалогу"))
    user_id = call.from_user.id
    companion_id = int(companion_id)
    if companion_id == user_id:
        await call.answer(show_alert=True, text="Вы не можете выбрать свою тему!!")
    else:
        repo: SQLAlchemyRepo = dialog_manager.data.get('repo')
        await repo.get_repo(ThemeRepo).delete_theme(user_id=companion_id)
        companion_manager = dialog_manager.bg(user_id=companion_id, chat_id=companion_id)
        await companion_manager.start(AllStates.in_dialog, mode=StartMode.NORMAL,
                                      data={'companion_id': user_id, "text": "Пользователь найден!"})
        await dialog_manager.start(AllStates.in_dialog, mode=StartMode.NORMAL,
                                   data={"companion_id": companion_id, "text": "Добро пожаловать в чат!"})


async def text_join_in_dialog(dialog_manager: DialogManager, **kwargs):
    text = dialog_manager.current_context().start_data.get('text')
    return {"text": text}


async def cancel_dialog(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager):
    start_data = dialog_manager.current_context().start_data
    companion_id = start_data.get("companion_id")
    companion_manager = dialog_manager.bg(user_id=companion_id, chat_id=companion_id)
    await dialog_manager.start(AllStates.cancel, mode=StartMode.RESET_STACK,
                               data={"text": "Вы завершили диалог", "random_start": True})
    await companion_manager.start(AllStates.cancel, mode=StartMode.RESET_STACK,
                                  data={"text": "Собеседник завершил диалог", "random_start": True})


async def who_cancel_dialog(dialog_manager: DialogManager, **kwargs):
    text = dialog_manager.current_context().start_data.get('text')
    if dialog_manager.current_context().start_data.get('random_start'):
        button = "Вернуться в главное меню"
    else:
        button = "Вернуться в меню диалогов"
    return {"text": text, "button": button}


async def return_menu(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager):
    if dialog_manager.current_context().start_data.get('random_start'):
        state_return = AllStates.main_menu
    else:
        state_return = AllStates.dialog_menu
    await dialog_manager.dialog().switch_to(state=state_return)


async def dialog(message: types.Message, dialog: Dialog, dialog_manager: DialogManager):
    companion_id = dialog_manager.current_context().start_data.get("companion_id")
    dialog_manager.show_mode = ShowMode.EDIT
    await message.copy_to(chat_id=companion_id)