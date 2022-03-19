import asyncio
from database.models import ThemeTable
from loader import bot, registry, engine, async_sessionmaker
from handlers import dp
from windows import dialog_window
from sqlalchemy_utils import database_exists, create_database
from database.base import Base
from middlewares import setup_middleware


async def main():
    setup_middleware(async_sessionmaker)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    registry.register(dialog_window)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.run(main())
