from data.config_loader import DB
from slugify import slugify


def make_connection_string(db: DB):
    result_string = (
        f"postgresql+asyncpg://{db.user}:{db.password}@{db.host}/{db.db_name}"
    )
    return result_string
