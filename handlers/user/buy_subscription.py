import datetime
from aiogram.types import CallbackQuery
from typing import Any
from aiogram.types import PreCheckoutQuery, Message, LabeledPrice
from aiogram_dialog import DialogManager, StartMode
from loader import config, bot, dp
from aiogram.types.message import ContentType
from states.all_state import AllStates
from dateutil.relativedelta import relativedelta
from aiogram.dispatcher.filters.callback_data import CallbackData

# class CancelBuy(CallbackData, prefix='cancel_buy'):


async def get_subscriptions(**kwargs):
    subscriptions = [
        ("1 день - 65₽", "day_id"),
        ("7 дней - 125₽", "week_id"),
        ("1 месяц - 199₽", "month_id"),
        ("1 год - 1999₽", "year_id")
    ]
    return {
        "subscriptions": subscriptions
    }


# async def buy_subscription(call: CallbackQuery, widget: Any, dialog_manager: DialogManager, sub_id: str):


async def buy_subscription(call: CallbackQuery, widget: Any, dialog_manager: DialogManager, sub_id: str):
    subscriptions = {
        "day_id": {"payload": "day_sub", "label": "Подписка на день", "description": "Приобрести подписку на 1 день",
                   "amount": 6500, "datatime": relativedelta(days=1)},
        "week_id": {"payload": "week_sub", "label": "Подписка на неделю",
                    "description": "Приобрести подписку на 7 дней",
                    "amount": 12500, "datatime": relativedelta(weeks=1)},
        "month_id": {"payload": "month_sub", "label": "Подписка на месяц",
                     "description": "Приобрести подписку на месяц",
                     "amount": 19900, "datatime": relativedelta(months=1)},
        "year_id": {"payload": "year_sub", "label": "Подписка на год",
                    "description": "Приобрести подписку на один год", "amount": 199900,
                    "datatime": relativedelta(year=1)}
    }
#     sub = subscriptions[sub_id]
#     payload = sub["payload"]
#     prices = LabeledPrice(label=sub["label"], amount=sub["amount"])
#     print(prices)
#     dialog_manager.current_context().dialog_data.update(payload=payload)
#     last_message_id = dialog_manager.current_stack().last_message_id
#     await bot.delete_message(chat_id=call.from_user.id, message_id=last_message_id)
# #
#
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
