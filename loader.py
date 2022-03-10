from aiogram import Bot, Dispatcher
from aiogram.dispatcher.fsm.storage.memory import MemoryStorage
from sqlalchemy import create_engine
from data.config import BOT_TOKEN, CONNECT_TO_DB
from sqlalchemy.orm import sessionmaker
from aiogram_dialog import DialogRegistry

# registration the bot and its components
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
registry = DialogRegistry(dp)
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")

# database
engine = create_engine(CONNECT_TO_DB, echo=False, )
Session = sessionmaker(bind=engine)
session = Session()
