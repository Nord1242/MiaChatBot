from repositories.pay_repo import PayRepo
from typing import Any
from aiogram_dialog import DialogManager, StartMode
from states.all_state import AllStates
from loader import config
from aiogram.types import CallbackQuery
from repositories.repo import SQLAlchemyRepo
from aiogram_dialog.context.context import Context


async def cancel_pay(call: CallbackQuery, widget: Any, dialog_manager: DialogManager):
    repo: SQLAlchemyRepo = dialog_manager.data.get('repo')
    await repo.get_repo(PayRepo).delete_pay(user_id=call.from_user.id)


async def get_subscriptions(**kwargs):
    subscriptions = [
        ("1 день - 65₽", "day"),
        ("7 дней - 125₽", "week"),
        ("1 месяц - 199₽", "month"),
        ("1 год - 1999₽", "year")
    ]
    return {
        "subscriptions": subscriptions
    }


# async def buy_subscription(call: CallbackQuery, widget: Any, dialog_manager: DialogManager, sub_id: str):


async def buy_subscription(call: CallbackQuery, widget: Any, dialog_manager: DialogManager, product_id: str):
    event: CallbackQuery = dialog_manager.event
    repo: SQLAlchemyRepo = dialog_manager.data.get('repo')
    intent_id = dialog_manager.current_context().id
    chat = event.message.chat.dict()
    from_user = event.from_user.dict()
    await repo.get_repo(PayRepo).add_pay(user_id=call.from_user.id, intent_id=intent_id,
                                         user_data={"from_user": from_user, "chat": chat})
    dialog_manager.current_context().dialog_data.update(product_id=product_id, user_id=call.from_user.id)
    await dialog_manager.switch_to(AllStates.start_buy)


async def get_data_for_buy(dialog_manager: DialogManager, **kwargs):
    subscriptions = {
        "top": 'Темы в топ на 24 часа',
        "day": 'Описание дневной подписки',
        "week": 'Описание 7-ми дневной подписки',
        "month": 'Описание месячной подписки',
        "year": 'Описание годовой подписки',

    }
    user_id = dialog_manager.current_context().dialog_data.get('user_id')
    product_id = dialog_manager.current_context().dialog_data.get('product_id')
    url = config.buy.buy_url + f"{product_id}?" + f"user_id={user_id}"
    return {
        "product_desc": subscriptions[product_id],
        "url": url
    }

    #
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
