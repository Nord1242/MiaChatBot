import sqlalchemy
from aiogram import Bot, Dispatcher
from data.config_loader import Config, load_config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from aiogram_dialog import DialogRegistry
from database.database_utility import make_connection_string
from utils.analytics import InfluxAnalyticsClient
from aiohttp import web
from queue import Queue
from aiogram.dispatcher.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aioredis import Redis

# import os

# loadconfig
config: Config = load_config()

# redis
redis_connect = Redis.from_url(config.redis.host, password=config.redis.password)
storage = RedisStorage(redis_connect, key_builder=DefaultKeyBuilder(with_destiny=True))
# storage = MemoryStorage()

dp = Dispatcher(storage=storage)
registry = DialogRegistry(dp)
bot = Bot(token=config.bot.token, parse_mode="HTML")

# database
engine = create_async_engine(make_connection_string(config.db), future=True)
async_sessionmaker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
metadata = sqlalchemy.MetaData(bind=engine)

# collection statistics
objects_queue = Queue()
influx = InfluxAnalyticsClient(
    url=config.influxdb.host, token=config.influxdb.token, org=config.influxdb.org, objects_queue=objects_queue
)

# web app
extra_router = web.RouteTableDef()
