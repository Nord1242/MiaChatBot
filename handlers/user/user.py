from aiogram_dialog import DialogManager
from typing import Any
from aiogram import types
from loader import bot
from repositories.repo import SQLAlchemyRepo
from repositories.user_repo import UserRepo
from states.all_state import AllStates
from aiogram_dialog import Dialog
from aiogram_dialog.widgets.kbd import ManagedListGroupAdapter, ManagedCheckboxAdapter
from typing import Dict
import hashlib


async def get_profile_data(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.data.get('event_from_user')
    repo: SQLAlchemyRepo = dialog_manager.data.get('repo')
    user_repo = repo.get_repo(UserRepo)
    user_profile = await user_repo.get_user(user_id=user.id)
    return {
        "login": user_profile.first_name,
        "sub": user_profile.sub if user_profile else None,
    }


def when_checked(data: Dict, widget, dialog_manager: DialogManager) -> bool:
    lg: ManagedListGroupAdapter = dialog_manager.dialog().find("lg")
    check: ManagedCheckboxAdapter = lg.find_for_item("check", data["item"])
    return check.is_checked()
