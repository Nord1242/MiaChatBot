from aiogram_dialog import DialogManager
import math
import re

from repositories.product_repo import ProductRepo
from repositories.repo import SQLAlchemyRepo
from repositories.user_repo import UserRepo
from aioredis.client import Redis
from aiogram_dialog import ChatEvent, StartMode
from aiogram_dialog.widgets.kbd import ManagedListGroupAdapter, ManagedCheckboxAdapter
from aiogram import types
from typing import Dict, Any
from datetime import datetime, timedelta
from database.models import Users
from states.all_state import ThemeDialogStates, BuyStates, MenuStates
from loader import dp

import random


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
        await dialog_manager.start(MenuStates.main_menu, mode=StartMode.RESET_STACK)
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
    print(checkbox.is_checked())
    return top


async def get_profile_data(dialog_manager: DialogManager, **kwargs):
    product_date_end, first_name = None, None
    user_profile = dialog_manager.data.get('user')
    user = dialog_manager.data.get('event_from_user')
    repo: SQLAlchemyRepo = dialog_manager.data.get('repo')
    user_repo: UserRepo = repo.get_repo(UserRepo)
    if user_profile:
        first_name = user_profile.first_name
        product_date_end = user_profile.product_date_end
    else:
        user_data: Users = await user_repo.get_user(user_id=user.id)
        first_name = user_data.first_name
        product_date_end = user_data.product_date_end
    return {
        "login": first_name,
        "sub": product_date_end
    }


@dp.message(commands={'create'})
async def checks_restrictions(call: types.CallbackQuery, widget: Any = None, dialog_manager: DialogManager = None):
    conn: Redis = dialog_manager.data.get('redis_conn')
    user: Users = dialog_manager.data.get('user')
    user_id = call.from_user.id
    repo: SQLAlchemyRepo = dialog_manager.data.get('repo')
    user_repo: UserRepo = repo.get_repo(UserRepo)
    now = datetime.utcnow()
    count = await conn.hget(name="restrictions", key=user_id)
    timeout = user.timeout
    state = ThemeDialogStates.write_theme
    if not user.product_date_end:
        if timeout:
            if now > user.timeout:
                await user_repo.delete_timeout(user_id)
            else:
                state = ThemeDialogStates.timeout
        elif count:
            if int(count) >= 5:
                await user_repo.set_timeout(user_id)
                await conn.hset("restrictions", key=user_id, value=0)
                state = ThemeDialogStates.timeout
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
