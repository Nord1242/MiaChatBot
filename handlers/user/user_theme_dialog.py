from aiogram_dialog import DialogManager, StartMode, Dialog
from aiogram_dialog.manager.protocols import ShowMode

from states.all_state import ThemeDialogStates
from database.models import Users

from aioredis.client import Redis
from aiogram_dialog.widgets.kbd import ManagedListGroupAdapter
from aiogram import types
from typing import Any

from utils.analytics import NamedEventPre
from repositories.repo import SQLAlchemyRepo

from aiogram import Bot

import re
import random


# async def get_user_id(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager):
#     dialog_manager.current_context().dialog_data.update(user_id=call.from_user.id)


async def create_dialog(message: types.Message, dialog: Dialog, dialog_manager: DialogManager):
    pattern = r'[Дд][Ее][Тт]|' \
              r'[Дд][Ее][Тт][Cc][Кк][Оо][Ое]|' \
              r'[Пп][Оо][Рр]|' \
              r'[Цц][Пп]' \
              r'|[Нн][Аа][Рр]|' \
              r''
    conn: Redis = dialog_manager.data.get('redis_conn')
    user: Users = dialog_manager.data.get('user')
    objects_queue = dialog_manager.data.get("objects_queue")
    objects_queue.put(NamedEventPre(event="Создание диалог"))
    top_def: ManagedListGroupAdapter = dialog_manager.dialog().find("check_top")
    dialog_data = dialog_manager.current_context().dialog_data
    if user.top:
        top = dialog_data.get("top") if dialog_data else top_def
    else:
        top = None
    user_id = message.from_user.id
    if not user.product_date_end:
        count = await conn.hget(name="restrictions", key=user_id)
        if not count:
            value = 1
        else:
            value = int(count) + 1
        await conn.hset("restrictions", key=user_id, value=value)
    theme_name = message.text
    check = re.search(pattern, theme_name).group()
    if check:
        await message.answer(text="В теме присутствует запрещенное слово!")
    elif len(theme_name) <= 19:
        if top:
            name = "user_theme_top"
        else:
            name = "user_theme"
        await conn.hset(name, key=user_id, value=theme_name)
        await dialog.next()
        await conn.hset("companion_state", key=user_id, value=ThemeDialogStates.waiting_user_theme.__str__())
    else:
        await message.answer(text="❗️ Максимальная длина темы 19 символов ❗️")


async def suggested_themes(dialog_manager: DialogManager, **kwargs):
    conn: Redis = dialog_manager.data.get('redis_conn')
    user_theme = await conn.hgetall("user_theme")
    top_theme = await conn.hgetall("user_theme_top")
    all_themes = {"top_theme": top_theme, "user_theme": user_theme}
    themes_buttons = list()
    top_button = list()
    for name, themes in all_themes.items():
        for user_id, theme in themes.items():
            if name == "top_theme":
                top_button.append(
                    (theme.decode('utf-8'),
                     user_id.decode('utf-8'))
                )
            else:
                themes_buttons.append(
                    (theme.decode('utf-8'),
                     user_id.decode('utf-8'))
                )
            random.shuffle(themes_buttons)
    return {
        "themes_buttons": themes_buttons,
        "top_button": top_button
    }


async def join_in_dialog(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager, companion_id: str):
    conn: Redis = dialog_manager.data.get('redis_conn')
    objects_queue = dialog_manager.data.get("objects_queue")
    objects_queue.put(NamedEventPre(event="Присоединение к диалогу"))
    user_id = call.from_user.id
    companion_id = int(companion_id)
    companion_state = (await conn.hget(name="companion_state", key=companion_id))
    if companion_id == user_id:
        await call.answer(show_alert=True, text="Вы не можете выбрать свою тему!!")
    elif not companion_state or companion_state.decode('utf-8') != ThemeDialogStates.waiting_user_theme.__str__():
        await call.answer(show_alert=True, text="Пользователь уже нашел собеседника!!")
    else:
        conn: Redis = dialog_manager.data.get('redis_conn')
        name = "user_theme_top"
        companion_manager = dialog_manager.bg(user_id=companion_id, chat_id=companion_id)
        await conn.hdel('user_theme', str(companion_id))
        await conn.hdel('user_theme_top', str(companion_id))
        await conn.hset(name="companion_state", key=companion_id, value=ThemeDialogStates.in_dialog_theme.__str__())
        await companion_manager.start(ThemeDialogStates.in_dialog_theme, mode=StartMode.RESET_STACK,
                                      data={'companion_id': user_id,
                                            "text": "Пользователь найден! 👀\nЧтобы завершить диалог, нажмите кнопку "
                                                    "ниже или воспользуйтесь командой: /stop"})
        await dialog_manager.start(ThemeDialogStates.in_dialog_theme, mode=StartMode.NORMAL,
                                   data={"companion_id": companion_id,
                                         "text": "Добро пожаловать в чат! 👀"
                                                 "Чтобы завершить диалог, нажмите кнопку ниже или воспользуйтесь"
                                                 " командой: /stop"})


async def text_join_in_dialog(dialog_manager: DialogManager, **kwargs):
    text = dialog_manager.current_context().start_data.get('text')
    return {"text": text}


async def who_cancel_dialog(dialog_manager: DialogManager, **kwargs):
    report_button = [
        ('🔞 Рассылка детского порно', 'CP'),
        ('😢 Рассылка материалов с целью насилия', 'viol'),
        ('🤡 Попрошайничество у участников системы', 'money'),
        ('🤬 Оскорбления собеседников', 'insult')

    ]
    text = dialog_manager.current_context().start_data.get('text')
    return {
        "text": text,
        "report_button": report_button
    }


async def dialog(message: types.Message, dialog: Dialog, dialog_manager: DialogManager):
    companion_id = dialog_manager.current_context().start_data.get("companion_id")
    dialog_manager.show_mode = ShowMode.EDIT
    await message.copy_to(chat_id=companion_id)
