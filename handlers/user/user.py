from aiogram_dialog import DialogManager
import math
import re
from aiogram_dialog.widgets.kbd import ManagedRadioAdapter
from repositories.product_repo import ProductRepo
from repositories.repo import SQLAlchemyRepo
from repositories.user_repo import UserRepo
from aioredis.client import Redis
from aiogram_dialog import ChatEvent, StartMode
from aiogram_dialog.widgets.kbd import ManagedListGroupAdapter, ManagedCheckboxAdapter
from aiogram import types
from typing import Dict, Any, Union
from datetime import datetime, timedelta
from database.models import Users
from states.all_state import ThemeDialogStates, BuyStates, MenuStates
from loader import dp
from aiogram.types.update import Update
import random


async def gender(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager, user_gender: str):
    repo: SQLAlchemyRepo = dialog_manager.data.get('repo')
    user_repo: UserRepo = repo.get_repo(UserRepo)
    await user_repo.set_gender(gender=user_gender, user_id=call.from_user.id)
    await dialog_manager.start(MenuStates.main_menu)


async def check_changed(event: ChatEvent, checkbox: ManagedCheckboxAdapter, manager: DialogManager):
    return checkbox.is_checked()


async def unban(dialog_manager: DialogManager, **kwargs):
    user: Users = dialog_manager.data.get('user')
    repo: SQLAlchemyRepo = dialog_manager.data.get('repo')
    ban_text = {"CP": "рассылка детского порно 🔞",
                "insult": "оскорбления собеседников 🤬",
                "money": "попрошайничество у участников системы 🤡",
                "viol": " рассылка материалов с целью насилия 😢"}
    products_repo: ProductRepo = repo.get_repo(ProductRepo)
    product = await products_repo.get_product("unbanned")
    product_button = [(f"Разбан - {int(product.amount)}₽", product.product_id)]
    return {
        "unban": product_button,
        "user_ban": ban_text[user.ban_info],
    }


async def ban_info(dialog_manager: DialogManager, **kwargs):
    user: Users = dialog_manager.data.get('user')
    ban_text = {"CP": "рассылка детского порно 🔞",
                "insult": "оскорбления собеседников 🤬",
                "money": "попрошайничество у участников системы 🤡",
                "viol": " рассылка материалов с целью насилия 😢"}
    return {
        "user_ban": ban_text[user.ban_info],
    }


async def time_ban_info(dialog_manager: DialogManager, **kwargs):
    user: Users = dialog_manager.data.get('user')
    time_ban: datetime = user.time_ban
    minutes = time_ban - datetime.utcnow()
    round_minutes = math.ceil(minutes.total_seconds() / 60)
    end = ''
    if round_minutes == 2:
        end = 'ы'
    elif round_minutes == 1:
        end = 'у'
    return {
        "user_ban": user.ban_info,
        "min": round_minutes,
        "end": end
    }


async def get_captcha(dialog_manager: DialogManager, **kwargs):
    counter = dialog_manager.current_context().start_data.get("counter")
    if not counter:
        counter = 5
    balls = [("🔴", "red"), ("🟠", "orange"), ("🟡", "yellow"), ("🟢", "green"), ("🟣", "purple"),
             ("⚫", "white"), ("️⚪", "black"), ("️🟤", "brown")]
    correct_ball = random.choice(balls)
    dialog_manager.current_context().start_data.update(correct_ball=correct_ball[1])
    dialog_manager.current_context().start_data.update(counter=counter)
    random.shuffle(balls)
    return {
        "captcha_balls": balls,
        "captcha": correct_ball[0],
        "counter": counter,
        "ending": "ок" if counter > 1 else "ка"
    }


async def check_captcha(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager, ball: str):
    counter = dialog_manager.current_context().start_data.get("counter")
    repo: SQLAlchemyRepo = dialog_manager.data.get('repo')
    user: Users = dialog_manager.data.get('user')
    user_repo: UserRepo = repo.get_repo(UserRepo)
    correct_ball = dialog_manager.current_context().start_data.get("correct_ball")
    if correct_ball == ball:
        await user_repo.set_human(call.from_user.id)
        await dialog_manager.start(MenuStates.gender)
    else:
        counter -= 1
        if counter == 0:
            attempts = user.attempts
            now = datetime.utcnow()
            attempts -= 1
            minute_ban = {5: 2, 4: 5, 3: 10, 2: 15, 1: 30}
            ban_time = now + timedelta(minutes=minute_ban[attempts])
            await user_repo.set_time_ban(user_id=user.telegram_user_id,
                                         ban_info="не пройдена анти-спам защита 🤖", ban_date=ban_time,
                                         attempts=attempts)
            await dialog_manager.start(MenuStates.time_ban)
        else:
            dialog_manager.current_context().start_data.update(counter=counter)


async def timeout(dialog_manager: DialogManager, **kwargs):
    user: Users = dialog_manager.data.get('user')
    time_ban: datetime = user.timeout
    timeout_date = time_ban - datetime.utcnow()
    pattern = r'(\d\d|\d):'
    timeout_time = re.findall(pattern, str(timeout_date))
    hour = int(timeout_time[0])
    minutes = timeout_time[1]
    minutes_end = ''
    hour_end = 'а'
    if hour <= 0:
        hour = ''
    if hour == 1:
        hour_end = ''
    if minutes[-1] in ['2', '3', '4']:
        minutes_end = 'ы'
    elif minutes[-1] == '1':
        minutes_end = 'у'
    return {
        "hour": hour,
        "hour_end": hour_end,
        "minutes": int(minutes),
        "minutes_end": minutes_end
    }


async def check_top(event: ChatEvent, checkbox: ManagedCheckboxAdapter, dialog_manager: DialogManager):
    top = checkbox.is_checked()
    dialog_manager.current_context().dialog_data.update(top=top)
    return top


async def select_cat(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager, cat: str):
    conn: Redis = dialog_manager.data.get('redis_conn')
    await conn.hset(f"{call.from_user.id}_data", key="cat", value=cat)
    return True


async def select_search_gender(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager,
                               search_gender: str):
    conn: Redis = dialog_manager.data.get('redis_conn')
    await conn.hset(f"{call.from_user.id}_data", key="search_gender", value=search_gender)
    return True


async def get_profile_data(dialog_manager: DialogManager, **kwargs):
    show_gender = {"male": "🚹", "fem": "🚺"}
    conn: Redis = dialog_manager.data.get('redis_conn')
    user_profile: Users = dialog_manager.data.get('user')
    user = dialog_manager.data.get('event_from_user')
    repo: SQLAlchemyRepo = dialog_manager.data.get('repo')
    user_repo: UserRepo = repo.get_repo(UserRepo)
    if user_profile:
        first_name = user_profile.first_name
        product_date_end = user_profile.product_date_end
        companion_gender = await conn.hget(f'{user_profile.telegram_user_id}_data', "search_gender")
    else:
        user_data: Users = await user_repo.get_user(user_id=user.id)
        first_name = user_data.first_name
        product_date_end = user_data.product_date_end
        companion_gender = await conn.hget(f'{user_data.telegram_user_id}_data', "search_gender")
    if companion_gender:
        companion_gender = companion_gender.decode('utf-8')
        companion_gender = show_gender[companion_gender]
    else:
        companion_gender = "❌"
    return {
        "companion_gender": companion_gender,
        "login": first_name,
        "sub": product_date_end
    }


async def get_search_gender(dialog_manager: DialogManager, **kwargs):
    event = dialog_manager.data['event_chat']
    user: Users = dialog_manager.data.get('user')
    conn: Redis = dialog_manager.data.get('redis_conn')
    search_gender = await conn.hget(f'{user.telegram_user_id}_data', "search_gender")
    radio: ManagedRadioAdapter = dialog_manager.dialog().find('get_menu_gender')
    await radio.set_checked(item_id=search_gender.decode('utf-8'), event=event)


@dp.message(commands={'create'})
async def checks_restrictions(event: Union[types.CallbackQuery, types.Message], widget: Any = None,
                              dialog_manager: DialogManager = None):
    count = None
    cat = None
    conn: Redis = dialog_manager.data.get('redis_conn')
    user: Users = dialog_manager.data.get('user')
    user_id = event.from_user.id
    user_data = await conn.hgetall(f"{user_id}_data")
    if b'restrictions' in user_data:
        count = user_data[b'restrictions']
    if b'cat' in user_data:
        cat = user_data[b'cat']
    repo: SQLAlchemyRepo = dialog_manager.data.get('repo')
    user_repo: UserRepo = repo.get_repo(UserRepo)
    now = datetime.utcnow()
    user_timeout = user.timeout
    state = ThemeDialogStates.choose_cat
    if not user.product_date_end:
        if user_timeout:
            if now > user.timeout:
                await user_repo.delete_timeout(user_id)
            else:
                state = ThemeDialogStates.timeout
        elif count:
            if int(count) >= 15:
                await user_repo.set_timeout(user_id)
                await conn.hset(f"{user_id}_data", key="restrictions", value=0)
                state = ThemeDialogStates.timeout
        await dialog_manager.start(state)
        return
    if cat and isinstance(event, types.CallbackQuery):
        state = ThemeDialogStates.write_theme
    await dialog_manager.start(state)


def when_checked(data: Dict, widget, dialog_manager: DialogManager) -> bool:
    check: ManagedListGroupAdapter = dialog_manager.dialog().find("check")

    return check.is_checked()


async def get_sub_data(dialog_manager: DialogManager, **kwargs):
    user_profile: Users = dialog_manager.data.get('user')
    return {
        'text': f'⚙️ Подписка действует до {user_profile.product_date_end.strftime("%Y-%m-%d %H:%M")} (utc)\n\n'
                f'📝 Доступный функционал:\n'
                f'- отсутствует ограничение на количество создаваемых тем;\n'
                f'- сокращение шанса словить бан в нашей системе;\n'
                f'- под темой и во время диалога, будет показан пол пользователя\n🚹🚺\n'
                f'- доступен поиск случайного собеседника по полу'
                f'- в случае бана вашего аккаунта, есть возможность разбана.\n\n'
                f'⚠️ На подписку не распространяется:\n'
                f'└ продвижение вашей темы в топ;\n'
                f'└ разбан вашего аккаунта в системе.'
    }


def write_theme(data: Dict, widget, dialog_manager: DialogManager):
    if dialog_manager.current_context().start_data.get('state') == ThemeDialogStates.write_theme.__str__():
        return True
    else:
        return False


def buy_sub(data: Dict, widget, dialog_manager: DialogManager):
    if dialog_manager.current_context().start_data.get('state') == BuyStates.buy_subscription.__str__():
        return True
    else:
        return False


def get_button(data: Dict, widget, dialog_manager: DialogManager):
    return list(data["themes_buttons"])
