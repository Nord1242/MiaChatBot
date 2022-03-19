from aiogram import Bot, Dispatcher
from aiogram.dispatcher.fsm.storage.memory import MemoryStorage
from data.config_loader import Config, load_config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from aiogram_dialog import DialogRegistry
from database.database_utility import make_connection_string
from aiogram.dispatcher.fsm.storage.redis import RedisStorage

# loadconfig
config: Config = load_config()

# registration the bot and its components
# storage = RedisStorage.from_url(f"redis://{config.redis.host}")
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
registry = DialogRegistry(dp)
bot = Bot(token=config.bot.token, parse_mode="HTML")

# database
engine = create_async_engine(make_connection_string(config.db), future=True)
async_sessionmaker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

