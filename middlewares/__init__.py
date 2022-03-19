from .start_connection import GetConnectionToDB
from .repository import Repository

from loader import dp, async_sessionmaker
from sqlalchemy.orm import sessionmaker


def setup_middleware(sm: sessionmaker):
    dp.update.middleware(GetConnectionToDB(sm))
    dp.update.middleware(Repository())
