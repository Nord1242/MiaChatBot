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
class Redis:
    host: str


@dataclass
class Config:
    bot: Bot
    db: DB
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
        redis=Redis(
            host=env.str("REDIS_HOST")
        )
    )
