import random
import string
import hashlib
import urllib.parse
import pyshorteners as pyshorteners

from aioredis.client import Redis
from database.models import Users
from repositories.pay_repo import PayRepo
from repositories.product_repo import ProductRepo
from typing import Any
from aiogram_dialog import DialogManager, StartMode
from states.all_state import MenuStates, BuyStates
from loader import config
from aiogram_dialog.widgets.kbd import ManagedRadioAdapter
from aiogram.types import CallbackQuery
from repositories.repo import SQLAlchemyRepo
from repositories.product_repo import ProductRepo
from aiogram_dialog.context.context import Context


async def get_subscriptions(dialog_manager: DialogManager, **kwargs):
    repo: SQLAlchemyRepo = dialog_manager.data.get('repo')
    products_repo: ProductRepo = repo.get_repo(ProductRepo)
    all_products = await products_repo.get_all_product()
    subscriptions = []
    text = None
    for product in all_products:
        if product.product_id != 'top' and product.product_id != 'unbanned':
            activity = product.activity_day
            if product.product_id == 'year':
                text = "Год"
                activity = 1
            elif product.product_id == 'day':
                text = 'День'
            else:
                text = 'Дней'
            subscriptions.append((f'{activity} {text} - {int(product.amount)}₽', product.product_id))
    return {
        "subscriptions": subscriptions,
        "text": text,
    }


# async def buy_subscription(call: CallbackQuery, widget: Any, dialog_manager: DialogManager, sub_id: str):zzz
async def buy_subscription(call: CallbackQuery, widget: Any, dialog_manager: DialogManager, product_id: str):
    event: CallbackQuery = dialog_manager.event
    repo: SQLAlchemyRepo = dialog_manager.data.get('repo')
    intent_id = dialog_manager.current_context().id
    chat = event.message.chat.dict()
    from_user = event.from_user.dict()
    product = await repo.get_repo(ProductRepo).get_product(product_id)
    payment_id = random.randrange(100, 10000000000000)
    # pay_data = {
    #     "amount": int(product.amount),
    #     "payment": payment_id,
    #     "shop": config.buy.project_id,
    #     "currency": "RUB",
    #     "desc": product.desc,
    #     "secret_key": config.buy.secret_key,
    # }
    pay_data = {"merchant_id": config.buy.project_id,
                "pay_id": payment_id,
                "amount": int(product.amount),
                "currency": "RUB",
                "desc": product.desc,
                "secret_key": config.buy.secret_key}
    sing_data = [pay_data["currency"], pay_data["amount"], pay_data["secret_key"], pay_data["merchant_id"],
                 pay_data["pay_id"]]
    sign = hashlib.md5(":".join(map(str, sing_data)).encode('utf-8')).hexdigest()
    await repo.get_repo(PayRepo).add_pay(user_id=call.from_user.id, intent_id=intent_id, payment_id=payment_id,
                                         user_data={"from_user": from_user, "chat": chat},
                                         product_data={"desc": product.desc, "amount": product.amount,
                                                       "days": product.activity_day, "product_id": product.product_id})
    # dialog_manager.current_context().dialog_data.update(product_id=product_id, payment_id=payment_id)
    state = dialog_manager.current_context().state
    await dialog_manager.start(BuyStates.start_buy,
                               data={"product_id": product_id,
                                     "payment_id": payment_id,
                                     "state": state.__str__(),
                                     "sign": sign,
                                     "pay_data": pay_data})


async def get_data_for_buy(dialog_manager: DialogManager, **kwargs):
    text = ""
    s = pyshorteners.Shortener()
    pay_data: dict = dialog_manager.current_context().start_data.get('pay_data')
    sing = dialog_manager.current_context().start_data.get('sign')
    payment_id = dialog_manager.current_context().start_data.get('payment_id')
    product_id = dialog_manager.current_context().start_data.get('product_id')
    url_params = f"?merchant_id={pay_data['merchant_id']}" + f"&pay_id={payment_id}" + f"&amount={pay_data['amount']}" \
                 + f"&sign={sing}" + f"&description={pay_data['desc']}"
    code_params = urllib.parse.quote_plus(url_params)
    return {
        "product_desc": "ss",
        "url": f"{config.webhook.domain}/buy?params=" + code_params,
        "amount": pay_data['amount'],
    }

# async def get_subscriptions(dialog_manager: DialogManager, **kwargs):
#     repo: SQLAlchemyRepo = dialog_manager.data.get('repo')
#     products_repo: ProductRepo = repo.get_repo(ProductRepo)
#     all_products = await products_repo.get_all_product()
#     subscriptions = []
#     text = None
#     for product in all_products:
#         if product.product_id != 'top' and product.product_id != 'unbanned':
#             activity = product.activity_day
#             if product.product_id == 'year':
#                 text = "Год"
#                 activity = 1
#             elif product.product_id == 'day':
#                 text = 'День'
#             else:
#                 text = 'Дней'
#             subscriptions.append((f'{activity} {text} - {int(product.amount)}₽', product.product_id))
#     return {
#         "subscriptions": subscriptions,
#         "text": text,
#     }
#
#
# # async def buy_subscription(call: CallbackQuery, widget: Any, dialog_manager: DialogManager, sub_id: str):zzz
# async def buy_subscription(call: CallbackQuery, widget: Any, dialog_manager: DialogManager, product_id: str):
#     event: CallbackQuery = dialog_manager.event
#     repo: SQLAlchemyRepo = dialog_manager.data.get('repo')
#     intent_id = dialog_manager.current_context().id
#     chat = event.message.chat.dict()
#     from_user = event.from_user.dict()
#     product = await repo.get_repo(ProductRepo).get_product(product_id)
#     payment_id = random.randrange(100, 10000000000000)
#     pay_data = {
#         "amount": int(product.amount),
#         "payment": payment_id,
#         "shop": config.buy.project_id,
#         "currency": "RUB",
#         "desc": product.desc,
#         "secret_key": config.buy.secret_key,
#     }
#     sing_data = [data for data in pay_data.values()]
#     sign = hashlib.md5("|".join(map(str, sing_data)).encode('utf-8')).hexdigest()
#     await repo.get_repo(PayRepo).add_pay(user_id=call.from_user.id, intent_id=intent_id, payment_id=payment_id,
#                                          user_data={"from_user": from_user, "chat": chat},
#                                          product_data={"desc": product.desc, "amount": product.amount,
#                                                        "days": product.activity_day, "product_id": product.product_id})
#     # dialog_manager.current_context().dialog_data.update(product_id=product_id, payment_id=payment_id)
#     state = dialog_manager.current_context().state
#     await dialog_manager.start(BuyStates.start_buy,
#                                data={"product_id": product_id,
#                                      "payment_id": payment_id,
#                                      "state": state.__str__(),
#                                      "sign": sign,
#                                      "pay_data": pay_data})
#
#
# async def get_data_for_buy(dialog_manager: DialogManager, **kwargs):
#     text = ""
#     s = pyshorteners.Shortener()
#     pay_data: dict = dialog_manager.current_context().start_data.get('pay_data')
#     sing = dialog_manager.current_context().start_data.get('sign')
#     payment_id = dialog_manager.current_context().start_data.get('payment_id')
#     product_id = dialog_manager.current_context().start_data.get('product_id')
#     url_params = f"?amount={pay_data['amount']}" + f"&payment={payment_id}" + f"&desc={pay_data['desc']}" \
#                                                                               f"" + f"&shop={pay_data['shop']}" + f"&sign={sing}"
#     code_params = urllib.parse.quote_plus(url_params)
#     return {
#         "product_desc": "ss",
#         "url": f"{config.webhook.domain}/buy?params=" + code_params,
#         "amount": pay_data['amount'],
#     }

# @dp.pre_checkout_query()
# async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
#     await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
#
#
# @dp.message(content_types=[ContentType.SUCCESSFUL_PAYMENT])
# async def process_pay(message: Message, dialog_manager: DialogManager, **kwargs):
#     payload = dialog_manager.current_context().dialog_data.get("payload")
#     if message.successful_payment.invoice_payload == payload:
#         print(kwargs)
#         await dialog_manager.start(state=AllStates.buy_done, mode=StartMode.RESET_STACK)
