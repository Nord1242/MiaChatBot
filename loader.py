from aiogram import Bot, Dispatcher
from aiogram.dispatcher.fsm.storage.memory import MemoryStorage
from sqlalchemy import create_engine
from data.config import BOT_TOKEN, CONNECT_TO_DB
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

storage = MemoryStorage()
dp = Dispatcher(storage=storage)
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
engine = create_engine(CONNECT_TO_DB, echo=False, )
if not database_exists(engine.url):
    create_database(engine.url)
engine.connect()
Session = sessionmaker(bind=engine)
session = Session()
