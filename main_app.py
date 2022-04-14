import asyncio

from loader import bot, registry, engine, async_sessionmaker
from handlers import dp
from handlers.rout.check_payment import extra_router
from windows import dialog_window
from database.base import Base
from middlewares import setup_middleware
from loader import influx, objects_queue, config
from aiohttp import web
from aiogram.dispatcher.webhook.aiohttp_server import SimpleRequestHandler, setup_application


async def main():
    registry.register(dialog_window)
    setup_middleware(async_sessionmaker)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    if not influx.health_check():
        raise ChildProcessError
    influx.start()
    # await bot.set_webhook(
    #     url=config.webhook.domain + config.webhook.path,
    #     drop_pending_updates=True,
    #     allowed_updates=dp.resolve_used_update_types()
    # )
    # # Creating an aiohttp application
    # app = web.Application()
    # app.add_routes(extra_router)
    # SimpleRequestHandler(dispatcher=dp, bot=bot, objects_queue=objects_queue).register(app, path=config.webhook.path)
    # runner = web.AppRunner(app)
    # await runner.setup()
    # site = web.TCPSite(runner, host=config.webapp.host, port=config.webapp.port)
    # await site.start()
    # # Running it forever
    # await asyncio.Event().wait()
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), objects_queue=objects_queue)


if __name__ == '__main__':
    asyncio.run(main())
