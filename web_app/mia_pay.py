import base64
import urllib.parse
import urllib.parse
import aiohttp
import random
import re
import hashlib
import aiohttp_jinja2
import string


from datetime import datetime, timedelta
from typing import Any
from utils.analytics import UniqueUserPre
from aiohttp import web
from loader import config, extra_router, bot, registry, objects_queue
from repositories.pay_repo import PayRepo
from repositories.success_pay_repo import SuccessPayRepo
from repositories.product_repo import ProductRepo
from repositories.user_repo import UserRepo
from aiogram.types import Chat, User
from aiohttp.web import Request
from .get_repo import get_repo
from aiogram_dialog.context.stack import DEFAULT_STACK_ID
from aiogram_dialog.manager.bg_manager import BgManager
from states.all_state import BuyStates
from database.models import Pay


async def check_pay(payment_id):
    async with aiohttp.ClientSession() as session:
        async with session.post('https://payok.io/api/transaction', data={"API_ID": config.buy.api_id,
                                                                          "API_KEY": config.buy.api_key,
                                                                          "shop": config.buy.project_id,
                                                                          "payment": payment_id}) as rest:
            answer = await rest.json(content_type=None)
            print(answer)
            status = answer['status']
            return status


async def check_sing(pay_object, payment_id, data):
    if pay_object:
        amount = int(pay_object.product_data["amount"])
        sing_data = [config.buy.secret_key, pay_object.product_data['desc'], data['currency'], data['shop'],
                     data['payment_id'], amount]
        print(sing_data)
        sign = hashlib.md5("|".join(map(str, sing_data)).encode('utf-8')).hexdigest()
        print("|".join(map(str, sing_data)))
        print(sign, data['sign'])
        if data['sign'] == sign:
            return True
    return False


async def switch_state(pay_object, chat_data, from_user):
    chat = Chat(**chat_data)
    from_user = User(**from_user)
    bg_manager = BgManager(chat=chat, user=from_user, stack_id=DEFAULT_STACK_ID,
                           intent_id=pay_object.intent_id,
                           bot=bot,
                           registry=registry, load=True)
    await bg_manager.start(state=BuyStates.successful_payment)


async def set_product(user_id: int, day_sub: Any, product_id: str, payment_id: int):
    user_repo: UserRepo = await get_repo(UserRepo)
    if product_id == "top":
        await user_repo.set_top(user_id=user_id, product_id=product_id, payment_id=payment_id)
    elif product_id == "unbanned":
        await user_repo.delete_ban(user_id=user_id, product_id=product_id, payment_id=payment_id)
    else:
        await user_repo.set_sub(user_id=user_id, day_sub=int(day_sub), product_id=product_id, payment_id=payment_id)


@extra_router.get("/")
async def home(request: Request):
    params = request.rel_url.query
    if params:
        channel = params['channel']
        objects_queue.put(UniqueUserPre(channel=channel))
    raise web.HTTPFound("https://t.me/MiaAnonimChatBot")


@extra_router.get("/buy")
async def buy(request: Request):
    params = request.rel_url.query['params']
    str_params = urllib.parse.unquote(params)
    raise web.HTTPFound(config.buy.url + str_params)


@extra_router.post('/notification')
async def notification(request: Request):
    print('sssss')
    pattern = r'(\w+)=(\w+)'
    request_body_str = (await request.read()).decode('utf-8')
    data = {data[0]: data[1] for data in re.findall(pattern, request_body_str)}
    payment_id = int(data['payment_id'])
    print(data['sign'])
    success_repo: SuccessPayRepo = await get_repo(SuccessPayRepo)
    pay_repo: PayRepo = await get_repo(PayRepo)
    pay_object: Pay = await pay_repo.get_pay(payment_id=payment_id)
    if await check_sing(pay_object, payment_id, data):
        chat_data = pay_object.user_data["chat"]
        from_user = pay_object.user_data["from_user"]
        product_id = pay_object.product_data["product_id"]
        status = await check_pay(payment_id)
        if status == 'success':
            print('suc')
            await set_product(user_id=from_user["id"], day_sub=pay_object.product_data['days'],
                              payment_id=payment_id, product_id=product_id)
            await switch_state(pay_object, chat_data, from_user)
            return web.Response(status=200)
    return web.Response(status=401)
