from dataclasses import dataclass
from environs import Env


@dataclass
class Bot:
    token: str


@dataclass
class DB:
    host: str
    db_name: str
    user: str
    password: str


@dataclass
class InfluxDB:
    host: str
    org: str
    token: str


@dataclass
class Redis:
    host: str





@dataclass
class Config:
    bot: Bot
    db: DB
    influxdb: InfluxDB
    redis: Redis

def load_config():
    env = Env()
    env.read_env()
    return Config(
        bot=Bot(token=env.str("BOT_TOKEN")),
        db=DB(
            host=env.str("DB_HOST"),
            db_name=env.str("DB_NAME"),
            user=env.str("DB_USER"),
            password=env.str("DB_PASS")
        ),
        # redis_for_online=RedisForOnline(),
        influxdb=InfluxDB(
            host=env.str("INFLUXDB_HOST"),
            org=env.str("INFLUXDB_ORG"),
            token=env.str("INFLUXDB_TOKEN"),

        ),
        redis=Redis(
            host=env.str("REDIS_HOST")
        )
    )
