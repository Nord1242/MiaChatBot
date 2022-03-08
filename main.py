from loader import bot
from handlers import dp


def main():
    # setup_middleware()
    dp.run_polling(bot)


if __name__ == '__main__':
    main()
