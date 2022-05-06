from loader import dp, config
from aiogram import types
from aiogram_dialog import DialogManager, Dialog
from states.all_state import AdminStates
from repositories.repo import SQLAlchemyRepo
from repositories.user_repo import UserRepo
from asyncio import sleep


@dp.message(commands={'nordadmin'})
async def admin_menu(message: types.Message, dialog_manager: DialogManager):
    print(message.from_user.id)
    if message.from_user.id == config.admin.id:
        await dialog_manager.start(AdminStates.admin_menu)


async def distribution_message(message: types.Message, dialog: Dialog, dialog_manager: DialogManager):
    repo: SQLAlchemyRepo = dialog_manager.data.get("repo")
    user_repo: UserRepo = repo.get_repo(UserRepo)
    all_id = await user_repo.get_all_user_id()
    success = 0
    unsuccess = 0
    for user_id in all_id:
        if user_id != message.from_user.id:
            try:
                await message.send_copy(chat_id=user_id)
                success += 1
            except Exception as ex:
                print(ex)
                unsuccess += 1
            await sleep(0.34)
    dialog_manager.current_context().dialog_data.update(success=success, unsuccess=unsuccess)
    await dialog_manager.switch_to(AdminStates.success_send)


async def get_send_data(dialog_manager: DialogManager, **kwargs):
    success = dialog_manager.current_context().dialog_data.get("success")
    unsuccess = dialog_manager.current_context().dialog_data.get("unsuccess")
    text = "Пользователю" if success == 1 else "Пользователям"
    unsuc_text = "Пользователь" if unsuccess == 1 else "Пользователей"
    return {
        "text": text,
        "success": success,
        "unsuccess": unsuccess,
        "unsuc_text": unsuc_text
    }
