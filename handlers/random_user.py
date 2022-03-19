from pprint import pprint
from repositories.repo import SQLAlchemyRepo
from aiogram_dialog import DialogManager, StartMode
from aiogram import types
from typing import Any
from aiogram.dispatcher.fsm.context import FSMContext
from repositories.random_user_repository import RandomUsersRepo
import random
from states.dialog_state import AllStates


async def search_random_user(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager):
    repo: SQLAlchemyRepo = dialog_manager.data.get('repo')
    user_repo = repo.get_repo(RandomUsersRepo)
    user_id = call.from_user.id
    all_users = await user_repo.get_all_users()
    state = dialog_manager.current_context().state
    if all_users:
        user = random.choice(all_users)
        companion_id = user.user_id
        if call.from_user.id != companion_id:
            await user_repo.delete_user(user_id=companion_id)
            companion_manager = dialog_manager.bg(user_id=companion_id, chat_id=companion_id)
            user_manager = dialog_manager.bg(user_id=user_id, chat_id=user_id)
            await user_manager.start(AllStates.in_dialog, mode=StartMode.RESET_STACK,
                                     data={"companion_id": companion_id, "text": "Пользователь найден!",
                                           "random_start": True})
            await companion_manager.start(AllStates.in_dialog, mode=StartMode.RESET_STACK,
                                          data={'companion_id': user_id, "text": "Пользователь найден!",
                                                "state_start": True})
    else:
        dialog_manager.current_context().dialog_data.update(random_start=True)
        await user_repo.add_user(user_id=user_id)
