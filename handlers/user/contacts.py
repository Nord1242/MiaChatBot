from aiogram import types
from aiogram_dialog import DialogManager


async def friend_request(call: types.CallbackQuery, dialog_manager: DialogManager):
    companion_id = dialog_manager.current_context().start_data.get("companion_id")
