import asyncio
from loader import bot, registry, engine, async_sessionmaker
from handlers import dp
from windows import dialog_window
from database.base import Base
from middlewares import setup_middleware
from loader import influx, objects_queue


async def main():
    setup_middleware(async_sessionmaker)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    if not influx.health_check():
        raise ChildProcessError
    influx.start()
    registry.register(dialog_window)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), objects_queue=objects_queue)


if __name__ == '__main__':
    asyncio.run(main())
