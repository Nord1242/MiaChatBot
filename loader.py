from aiogram import Bot, Dispatcher
from aiogram.dispatcher.fsm.storage.memory import MemoryStorage
from data.config_loader import Config, load_config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from aiogram_dialog import DialogRegistry

# loadconfig
config: Config = load_config()

# registration the bot and its components
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
registry = DialogRegistry(dp)
bot = Bot(token=config.bot.token, parse_mode="HTML")

# database
engine = create_async_engine(
    f"postgresql+asyncpg://{config.db.user}:{config.db.password}@{config.db.host}/{config.db.db_name}",
    future=True
)

# engine = create_engine(CONNECT_TO_DB, echo=False, )
# Session = sessionmaker(bind=engine)
# session = Session()
