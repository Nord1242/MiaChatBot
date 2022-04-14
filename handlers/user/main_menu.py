from aiogram_dialog import DialogManager, StartMode
from loader import dp, bot, async_sessionmaker
from states.all_state import AllStates
from aiogram import types
from repositories.repo import SQLAlchemyRepo
from repositories.random_user_repository import RandomUsersRepo
from repositories.theme_repository import ThemeRepo
from repositories.pay_repo import PayRepo
from queue import Queue
from analytics import NamedEventPre


@dp.message(commands={'start'})
async def start_handler(message: types.Message, dialog_manager: DialogManager, objects_queue: Queue):
    objects_queue.put(NamedEventPre(event="Команда /start"))
    last_message_id = dialog_manager.current_stack().last_message_id
    if last_message_id:
        await bot.delete_message(chat_id=message.from_user.id, message_id=last_message_id)
    repo: SQLAlchemyRepo = dialog_manager.data.get('repo')
    await repo.get_repo(RandomUsersRepo).delete_user(user_id=message.from_user.id)
    await repo.get_repo(ThemeRepo).delete_theme(user_id=message.from_user.id)
    await repo.get_repo(PayRepo).delete_pay(user_id=message.from_user.id)
    await dialog_manager.start(AllStates.main_menu, mode=StartMode.RESET_STACK)
