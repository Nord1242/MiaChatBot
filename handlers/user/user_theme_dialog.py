from aiogram_dialog import DialogManager, StartMode, Dialog
from aiogram_dialog.manager.protocols import ShowMode

from repositories.product_repo import ProductRepo
from repositories.user_repo import UserRepo
from states.all_state import ThemeDialogStates
from database.models import Users

from aioredis.client import Redis
from aiogram_dialog.widgets.kbd import ManagedListGroupAdapter, ManagedRadioAdapter
from aiogram import types
from typing import Any

from utils.analytics import NamedEventPre
from repositories.repo import SQLAlchemyRepo

from aiogram import Bot

import re
import random


# async def get_user_id(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager):
#     dialog_manager.current_context().dialog_data.update(user_id=call.from_user.id)


async def check_user_top(dialog_manager: DialogManager, **kwargs):
    user: Users = dialog_manager.data['user']
    repo: SQLAlchemyRepo = dialog_manager.data.get('repo')
    products_repo: ProductRepo = repo.get_repo(ProductRepo)
    product = await products_repo.get_product("top")
    product_button = [(f"Выдвигать темы в топ на 24 часа 💎 - {int(product.amount)}₽", product.product_id)]
    return {
        "product_button": product_button,
        "top": user.top,
    }


async def create_dialog(message: types.Message, dialog: Dialog, dialog_manager: DialogManager):
    pattern = r'[Дд][Ее][Тт]|' \
              r'[Дд][Ее][Цц]|' \
              r'[Дд][Ее][Тт][Cc][Кк][Оо][Ое]|' \
              r'[Пп][Оо][Рр]|' \
              r'[Цц][Пп]' \
              r'|[Нн][Аа][Рр]|' \
              r''
    conn: Redis = dialog_manager.data.get('redis_conn')
    user: Users = dialog_manager.data.get('user')
    cat = await conn.hget("cat", key=str(message.from_user.id))
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
    elif len(theme_name) <= 36:
        if top:
            name = "user_theme_top"
        else:
            name = cat.decode('utf-8')
        await conn.hset(name, key=user_id, value=f"{theme_name} X{user.gender}X")
        await dialog.next()
        await conn.hset("companion_state", key=user_id, value=ThemeDialogStates.waiting_user_theme.__str__())
    else:
        await message.answer(text="❗️ Максимальная длина темы 36 символов ❗️")


async def select_cat_for_theme(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager):
    conn: Redis = dialog_manager.data.get('redis_conn')
    cat = await conn.hget("cat", key=str(call.from_user.id))
    if not cat:
        await call.answer(text="Выберите категорию!", show_alert=True)
    else:
        await dialog_manager.dialog().next()


async def choice_cat(dialog_manager: DialogManager, **kwargs):
    event = dialog_manager.data['event_chat']
    user: Users = dialog_manager.data['user']
    conn: Redis = dialog_manager.data.get('redis_conn')
    cat = await conn.hget("cat", key=str(user.telegram_user_id))
    if cat:
        cat = cat.decode('utf-8')
    radio: ManagedRadioAdapter = dialog_manager.dialog().find('get_cat')
    await radio.set_checked(item_id=cat, event=event)
    categories = [
        ('18+ 🔞', 'adult'),
        ('Знакомства 💞', 'dating'),
        ('Общение 💬', 'commun')
    ]
    return {
        "cat": cat,
        "categories": categories
    }


async def generate_themes_button(all_themes, pattern):
    themes_buttons = list()
    top_button = list()
    for name, themes in all_themes.items():
        for user_id, theme in themes.items():
            user_id = user_id.decode('utf-8')
            user_themes: str = theme.decode('utf-8')
            gender = re.search(pattern, user_themes).group()
            if name == "top_theme":
                top_button.append(
                    (user_themes.replace(f" {gender}", ''), user_id)
                )
            else:
                themes_buttons.append(
                    (user_themes.replace(f" {gender}", ''), user_id)
                )
    return themes_buttons, top_button


async def generate_sub_button(all_themes, pattern):
    themes_buttons = list()
    top_button = list()
    show_gender = {"XmaleX": "🚹", "XfemX": "🚺"}
    for name, themes in all_themes.items():
        for user_id, theme in themes.items():
            user_id = user_id.decode('utf-8')
            user_themes: str = theme.decode('utf-8')
            gender = re.search(pattern, user_themes).group()
            user_themes = user_themes.replace(gender, '')
            if name == "top_theme":
                top_button.append(
                    (f"{user_themes}\n{show_gender[gender]}", user_id)
                )
            else:
                themes_buttons.append(
                    (f"{user_themes}\n{show_gender[gender]}", user_id)
                )
    return themes_buttons, top_button


async def suggested_themes(dialog_manager: DialogManager, **kwargs):
    pattern = r'XmaleX|XfemX'
    event = dialog_manager.data['event_chat']
    user: Users = dialog_manager.data['user']
    conn: Redis = dialog_manager.data.get('redis_conn')
    cat = await conn.hget("cat", key=str(user.telegram_user_id))
    if not cat:
        cat = "adult"
    else:
        cat = cat.decode('utf-8')
    radio: ManagedRadioAdapter = dialog_manager.dialog().find('get_cat')
    await radio.set_checked(item_id=cat, event=event)
    user_theme = await conn.hgetall(cat)
    print(user_theme)
    top_theme = await conn.hgetall("user_theme_top")
    all_themes = {"top_theme": top_theme, "user_theme": user_theme}
    categories = [
        ('18+ 🔞', 'adult'),
        ('Знакомства 💞', 'dating'),
        ('Общение 💬', 'commun')

    ]
    if user.product_date_end:
        themes_buttons, top_button = await generate_sub_button(all_themes, pattern)
    else:
        themes_buttons, top_button = await generate_themes_button(all_themes, pattern)
    return {
        "themes_buttons": themes_buttons,
        "top_button": top_button,
        "categories": categories
    }


async def join_in_dialog(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager, companion_id: str):
    if companion_id == 'sad':
        return
    conn: Redis = dialog_manager.data.get('redis_conn')
    objects_queue = dialog_manager.data.get("objects_queue")
    objects_queue.put(NamedEventPre(event="Присоединение к диалогу"))
    user: Users = dialog_manager.data['user']
    user_id = call.from_user.id
    cat = await conn.hget("cat", key=companion_id)
    companion_id = int(companion_id)
    companion_state = (await conn.hget(name="companion_state", key=companion_id))
    repo: SQLAlchemyRepo = dialog_manager.data['repo']
    user_repo: UserRepo = repo.get_repo(UserRepo)
    if companion_id == user_id:
        await call.answer(show_alert=True, text="Вы не можете выбрать свою тему!!")
    elif not companion_state or companion_state.decode('utf-8') != ThemeDialogStates.waiting_user_theme.__str__():
        await call.answer(show_alert=True, text="Пользователь уже нашел собеседника!!")
    else:
        conn: Redis = dialog_manager.data.get('redis_conn')
        name = "user_theme_top"
        companion_manager = dialog_manager.bg(user_id=companion_id, chat_id=companion_id)
        await conn.hdel(cat.decode('utf-8'), str(companion_id))
        await conn.hdel('user_theme_top', str(companion_id))
        await conn.hset(name="companion_state", key=companion_id, value=ThemeDialogStates.in_dialog_theme.__str__())
        text = "Пользователь найден! 👀\nЧтобы завершить диалог, нажмите кнопку ниже или воспользуйтесь командой: /stop"
        companion: Users = await user_repo.get_user(companion_id)
        if companion.product_date_end:
            show_gender = {"male": "🚹", "fem": "🚺"}
            text = f"Пользователь найден! 👀\n\nПол пользователя: {show_gender[user.gender]}\n\nЧтобы завершить диалог, нажмите кнопку " \
                   "ниже или воспользуйтесь командой: /stop"
        await companion_manager.start(ThemeDialogStates.in_dialog_theme, mode=StartMode.RESET_STACK,
                                      data={'companion_id': user_id,
                                            "text": text})
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