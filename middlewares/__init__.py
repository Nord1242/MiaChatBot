from .start_connection import GetConnectionToDB
from .repository import Repository
from .exists_user import ExistsUser
from .log_updates import LogUpdatesMiddleware
from .online import OnlineMiddleware


from loader import dp, async_sessionmaker
from sqlalchemy.orm import sessionmaker


def setup_middleware(sm: sessionmaker):
    dp.update.middleware(GetConnectionToDB(sm))
    dp.update.middleware(Repository())
    dp.update.middleware(ExistsUser())
    dp.update.middleware(LogUpdatesMiddleware())
    dp.update.middleware()
