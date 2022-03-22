from aiogram_dialog import DialogManager
from typing import Any
from aiogram import types
from loader import bot
from repositories.repo import SQLAlchemyRepo
from repositories.profile_repo import ProfileRepo
from states.all_state import AllStates
from aiogram_dialog import Dialog
from aiogram_dialog.widgets.kbd import ManagedListGroupAdapter, ManagedCheckboxAdapter
from typing import Dict
import hashlib


def show_info_profile(data: Dict, widget, dialog_manager: DialogManager):
    profile = dialog_manager.current_context().dialog_data.get('have_profile')
    if profile:
        return True
    else:
        return False


def show_button_reg(data: Dict, widget, dialog_manager: DialogManager):
    profile = dialog_manager.current_context().dialog_data.get('have_profile')
    if not profile:
        return True
    else:
        return False


async def check_profile_in_base(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.data.get('event_from_user')
    repo: SQLAlchemyRepo = dialog_manager.data.get('repo')
    user_repo = repo.get_repo(ProfileRepo)
    user_profile = await user_repo.get_user_profile(user_id=user.id)
    if user_profile:
        have_profile = True
    else:
        have_profile = False
    dialog_manager.current_context().dialog_data.update(have_profile=have_profile)
    return {
        "login": user_profile.login if user_profile else None,
        "sub": user_profile.sub if user_profile else None
    }


def when_checked(data: Dict, widget, dialog_manager: DialogManager) -> bool:
    lg: ManagedListGroupAdapter = dialog_manager.dialog().find("lg")
    check: ManagedCheckboxAdapter = lg.find_for_item("check", data["item"])
    return check.is_checked()


async def get_login(message: types.Message, dialog: Dialog, dialog_manager: DialogManager):
    dialog_manager.current_context().dialog_data.update(login=message.text)
    await bot.delete_message(chat_id=message.from_user.id, message_id=dialog_manager.current_stack().last_message_id)
    await dialog.switch_to(AllStates.form_done)


async def reg_done(dialog_manager: DialogManager, **kwargs):
    user = kwargs.get('event_from_user')
    dialog_data = dialog_manager.current_context().dialog_data
    login = dialog_data.get('login')
    repo: SQLAlchemyRepo = dialog_manager.data.get('repo')
    user_repo = repo.get_repo(ProfileRepo)
    start_state = dialog_manager.current_context().dialog_data.get('start_state')
    user_profile = await user_repo.add_user_profile(login=login, user_id=user.id)
    return {'text': "Вы успешно прошли регистрацию"}
