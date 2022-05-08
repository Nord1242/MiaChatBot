from .start_connection import GetConnectionToDB
from .repository import Repository
from .exist_user import ExistsUser
from .log_updates import LogUpdatesMiddleware
from .online import OnlineMiddleware
from .redis_conn import GetConnectionToRedis
from .set_ban import SetUserBan
from .check_ban import CheckUserBan
from .check_user_time import CheckUserTime
from .captcha import CheckCaptcha
from .throttling import ThrottlingMiddleware
from .after_command import CancelDialog


from loader import dp
from sqlalchemy.orm import sessionmaker
from aioredis.client import Redis


async def setup_middleware(sm: sessionmaker, rc: Redis):
    dp.message.middleware(GetConnectionToRedis(rc))
    dp.message.middleware(GetConnectionToDB(sm))
    dp.message.middleware(Repository())
    dp.message.middleware(LogUpdatesMiddleware())
    dp.message.middleware(OnlineMiddleware())
    dp.message.middleware(ExistsUser())
    dp.message.middleware(CheckUserTime())
    dp.message.middleware(CheckUserBan())
    dp.message.middleware(CheckCaptcha())
    dp.message.middleware(SetUserBan())
    dp.message.middleware(ThrottlingMiddleware())
    dp.message.middleware(CancelDialog())

    dp.callback_query.middleware(GetConnectionToRedis(rc))
    dp.callback_query.middleware(GetConnectionToDB(sm))
    dp.callback_query.middleware(Repository())
    dp.callback_query.middleware(ExistsUser())
    dp.callback_query.middleware(CheckUserTime())
    dp.callback_query.middleware(SetUserBan())
    dp.callback_query.middleware(CheckUserBan())
    dp.callback_query.middleware(LogUpdatesMiddleware())
    dp.callback_query.middleware(OnlineMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())


