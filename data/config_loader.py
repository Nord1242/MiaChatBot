from dataclasses import dataclass
from environs import Env


@dataclass
class Admin:
    id: int


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
    password: str


@dataclass
class Buy:
    api_id: str
    api_key: str
    project_id: int
    secret_key: str
    url: str


@dataclass
class WebHook:
    domain: str
    path: str


@dataclass
class WebApp:
    host: str
    port: int


@dataclass
class Config:
    admin: Admin
    bot: Bot
    db: DB
    influxdb: InfluxDB
    webhook: WebHook
    webapp: WebApp
    buy: Buy
    redis: Redis


def load_config():
    env = Env()
    env.read_env()
    return Config(
        bot=Bot(token=env.str("BOT_TOKEN")),
        admin=Admin(
            id=env.int("ADMIN_ID")
        ),
        db=DB(
            host=env.str("DB_HOST"),
            db_name=env.str("DB_NAME"),
            user=env.str("DB_USER"),
            password=env.str("DB_PASS")
        ),
        webhook=WebHook(
            domain=env.str("WEBHOOK_HOST"),
            path=f"/bot-webhook/{env.str('BOT_TOKEN')}"
        ),
        influxdb=InfluxDB(
            host=env.str("INFLUXDB_HOST"),
            org=env.str("INFLUXDB_ORG"),
            token=env.str("INFLUXDB_TOKEN"),

        ),
        buy=Buy(
            api_id=env.str("API_ID"),
            api_key=env.str("API_KEY"),
            project_id=env.int("SHOP"),
            secret_key=env.str("SECRET_KEY"),
            url=env.str("BUY_URL")
        ),
        webapp=WebApp(
            host=env.str("APP_HOST"),
            port=env.int("APP_PORT")

        ),
        redis=Redis(
            host=env.str("REDIS_HOST"),
            password=env.str("REDIS_PASSWORD")
        )
    )
