from aiohttp import web
from loader import bot, registry
from aiogram_dialog.manager.bg_manager import BgManager
from aiogram_dialog.manager.protocols import DialogRegistryProto
from aiogram.types import Chat, User
from states.all_state import AllStates
from aiogram_dialog.context.stack import DEFAULT_STACK_ID
from loader import async_sessionmaker
from aiohttp.web import middleware
from repositories.repo import SQLAlchemyRepo
from repositories.pay_repo import PayRepo

extra_router = web.RouteTableDef()


@extra_router.post("/check-pay")
async def post_handler(request):
    async with async_sessionmaker() as session:
        async with session.begin():
            repos = SQLAlchemyRepo(session=session)
            user = await repos.get_repo(PayRepo).get_pay(user_id=455559956)
    print("Зашел")
    chat = Chat(**user.user_data["chat"])
    from_user = User(**user.user_data["from_user"])
    bg_manager = BgManager(chat=chat, user=from_user, stack_id=DEFAULT_STACK_ID, intent_id=user.intent_id, bot=bot,
                           registry=registry, load=True)
    await bg_manager.switch_to(AllStates.main_menu)
    return web.Response(status=200)
