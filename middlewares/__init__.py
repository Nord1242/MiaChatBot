from .start_connection import GetConnectionToDB
from .repository import Repository
from .exists_user import ExistsUser
from .log_updates import LogUpdatesMiddleware
from .online import OnlineMiddleware
from .states_middleware import StateMiddleware

from loader import dp
from sqlalchemy.orm import sessionmaker


def setup_middleware(sm: sessionmaker):
    dp.update.middleware(GetConnectionToDB(sm))
    dp.update.middleware(Repository())
    dp.message.middleware(ExistsUser())
    dp.callback_query.middleware(StateMiddleware())
    dp.update.middleware(LogUpdatesMiddleware())
    dp.update.middleware(OnlineMiddleware())
