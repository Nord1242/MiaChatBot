from aiogram_dialog import DialogManager, StartMode
from loader import dp, bot
from states.dialog_state import AllStates
from aiogram import types


@dp.message(commands={'start'})
async def start_handler(message: types.Message, dialog_manager: DialogManager):
    last_message_id = dialog_manager.current_stack().last_message_id
    if last_message_id:
        await bot.delete_message(chat_id=message.from_user.id, message_id=last_message_id)
    await dialog_manager.start(AllStates.main_menu, mode=StartMode.RESET_STACK)
