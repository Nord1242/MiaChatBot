# import aiohttp
#
# from aiohttp import web
# from loader import bot, registry
# from aiogram_dialog.manager.bg_manager import BgManager
# from aiogram.types import Chat, User
# from states.all_state import AllStates
# from aiogram_dialog.context.stack import DEFAULT_STACK_ID
# from loader import config, extra_router
# from .get_repo import get_repo
# from repositories.pay_repo import PayRepo
#
#
#
#
# @extra_router.post("/check-pay")
# async def post_handler(request):
#     request_data = await request.json()
#     user_id = request_data["user_id"]
#     payment_id = request_data["payment_id"]
#     status = await check_pay(payment_id)
#     if status == 'success':
#         pay_repo: PayRepo = await get_repo(PayRepo)
#         user = await pay_repo.get_pay(user_id)
#         chat = Chat(**user.user_data["chat"])
#         from_user = User(**user.user_data["from_user"])
#         bg_manager = BgManager(chat=chat, user=from_user, stack_id=DEFAULT_STACK_ID, intent_id=user.intent_id, bot=bot,
#                                registry=registry, load=True)
#         await bg_manager.switch_to(AllStates.successful_payment)
#
#         return web.Response(status=200)
