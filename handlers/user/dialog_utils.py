from database.models import Users, Report
from loader import dp
from repositories.repo import SQLAlchemyRepo
from repositories.user_repo import UserRepo
from repositories.user_report_repo import UserReportRepo

from states.all_state import RandomDialogStates, ThemeDialogStates, MenuStates

from aiogram import types
from typing import Any

from aiogram_dialog.widgets.kbd import Button

from aioredis.client import Redis
from aiogram import Bot
from aiogram_dialog import DialogManager, StartMode


async def cancel_search(call: types.CallbackQuery, button: Button, dialog_manager: DialogManager):
    conn: Redis = dialog_manager.data.get('redis_conn')
    cat = await conn.hget("cat", key=str(call.from_user.id))
    state = dialog_manager.current_context().state
    switch_state = None
    if state == RandomDialogStates.waiting_user:
        switch_state = MenuStates.main_menu
        await conn.lrem('random_users', count=1, value=call.from_user.id)
    elif state == ThemeDialogStates.waiting_user_theme:
        switch_state = ThemeDialogStates.search_theme
        await conn.hdel(cat.decode('utf-8'), call.from_user.id)
        await conn.hdel("user_theme_top", call.from_user.id)
    await conn.hdel('companion_state', call.from_user.id)
    print(switch_state.__str__())
    await dialog_manager.start(state=switch_state)

#
# async def cancel_dialog_command(dialog_manager, current_context):
#     if current_context and current_context.start_data:
#         state = current_context.state
#         companion_id = current_context.start_data.get("companion_id")
#         companion_manager = dialog_manager.bg(user_id=companion_id, chat_id=companion_id)
#         state_switch = None
#         if state == ThemeDialogStates.in_dialog_theme:
#             state_switch = ThemeDialogStates.cancel_theme
#         elif state == RandomDialogStates.in_dialog:
#             state_switch = RandomDialogStates.cancel
#         if state_switch:
#             await companion_manager.start(state_switch, mode=StartMode.RESET_STACK,
#                                           data={"text": "Собеседник завершил диалог"})


async def return_to_cancel_window(dialog_manager: DialogManager, companion_id: int, user_id: int):
    conn: Redis = dialog_manager.data.get("redis_conn")
    bot: Bot = dialog_manager.data.get('bot')
    state = dialog_manager.current_context().state
    if state == RandomDialogStates.in_dialog:
        state = RandomDialogStates.cancel
    elif state == ThemeDialogStates.in_dialog_theme:
        state = ThemeDialogStates.cancel_theme
    companion_manager = dialog_manager.bg(user_id=companion_id, chat_id=companion_id)
    await dialog_manager.start(state, mode=StartMode.RESET_STACK,
                               data={"text": "😔 Вы завершили диалог", "companion_id": companion_id})
    await companion_manager.start(state, mode=StartMode.RESET_STACK,
                                  data={"text": "😔 Собеседник завершил диалог", "companion_id": user_id})


@dp.message(commands={'stop'})
async def cancel_dialog(call: types.CallbackQuery, widget: Any = None, dialog_manager: DialogManager = None):
    conn: Redis = dialog_manager.data.get("redis_conn")
    current_context = dialog_manager.current_context()
    state = current_context.state if current_context else None
    if state == RandomDialogStates.in_dialog or state == ThemeDialogStates.in_dialog_theme:
        start_data = dialog_manager.current_context().start_data
        companion_id = start_data.get("companion_id")
        await conn.hdel('companion_state', str(companion_id))
        await conn.hdel('companion_state', str(call.from_user.id))
        user_id = call.from_user.id
        await return_to_cancel_window(dialog_manager, companion_id, user_id)
    else:
        await dialog_manager.start(state=MenuStates.not_companion)


async def report(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager, report_user: str):
    repo: SQLAlchemyRepo = dialog_manager.data.get('repo')
    companion_id = dialog_manager.current_context().start_data.get('companion_id')
    user_repo = repo.get_repo(UserRepo)
    user = await user_repo.get_user(user_id=companion_id)
    report_repo: UserReportRepo = repo.get_repo(UserReportRepo)
    complaints = user.complaints
    for complaint in complaints:
        if complaint.complaint == report_user:
            await report_repo.update_report(user_id=user.telegram_user_id, report=report_user,
                                            count=complaint.counter)
            break
    else:
        await report_repo.add_report(user_id=user.telegram_user_id, report=report_user, user=user)
    state = dialog_manager.current_context().state
    state_switch = ThemeDialogStates.report
    if state == RandomDialogStates.set_report:
        state_switch = RandomDialogStates.report
    await dialog_manager.switch_to(state_switch)
