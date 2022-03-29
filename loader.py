from aiogram import Bot, Dispatcher
from aiogram.dispatcher.fsm.storage.memory import MemoryStorage
from data.config_loader import Config, load_config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from aiogram_dialog import DialogRegistry
from database.database_utility import make_connection_string
from analytics import InfluxAnalyticsClient
from aiohttp import web
from queue import Queue
# from aiogram.dispatcher.fsm.storage.redis import RedisStorage
# import os

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

# collection statistics
objects_queue = Queue()
influx = InfluxAnalyticsClient(
    url=config.influxdb.host, token=config.influxdb.token, org=config.influxdb.org, objects_queue=objects_queue
)

# webhook settings
# WEBHOOK_HOST = f'https://{config.webhook.heroku_app_name}.herokuapp.com'
# WEBHOOK_PATH = f'/webhook/{config.bot.token}'
# WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'
#
#
# # webserver settings
# WEBAPP_HOST = '0.0.0.0'
# WEBAPP_PORT = os.getenv('PORT', default=8000)

# aiohttp
# app = web.Application()
