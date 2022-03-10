from loader import bot, registry, engine
from handlers import dp
from windows import dialog_window
from sqlalchemy_utils import database_exists, create_database


def main():
    if not database_exists(engine.url):
        create_database(engine.url)
    engine.connect()
    # setup_middleware()
    registry.register(dialog_window)
    dp.run_polling(bot)


if __name__ == '__main__':
    main()
