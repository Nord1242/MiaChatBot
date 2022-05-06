import asyncio
import jinja2
import aiohttp_jinja2

from loader import bot, registry, engine, async_sessionmaker, redis_connect, influx, objects_queue, config
from handlers import dp
from utils.delete_outdated_paydata import delete_old_pay
from utils.reset_reports import delete_report

from web_app import extra_router
from windows import registry_dialog
from database.base import Base
from middlewares import setup_middleware
from aiohttp import web
from aiogram.dispatcher.webhook.aiohttp_server import SimpleRequestHandler
from aiogram_dialog.tools import render_preview


async def main():
    await registry_dialog(registry)
    await setup_middleware(async_sessionmaker, redis_connect)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    if not influx.health_check():
        raise ChildProcessError
    influx.start()
    print(config.webhook.domain + config.webhook.path)
    await bot.set_webhook(
        url=config.webhook.domain + config.webhook.path,
        drop_pending_updates=True,
        allowed_updates=dp.resolve_used_update_types()
    )
    # Creating an aiohttp application
    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('web_app/templates'))
    app.add_routes(extra_router)
    SimpleRequestHandler(dispatcher=dp, bot=bot, objects_queue=objects_queue).register(app, path=config.webhook.path)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=config.webapp.host, port=config.webapp.port)
    await site.start()
    asyncio.create_task(delete_old_pay())
    asyncio.create_task(delete_report())
    # Running it forever
    await asyncio.Event().wait()
    # await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), objects_queue=objects_queue)


if __name__ == '__main__':
    asyncio.run(main())
