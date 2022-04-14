from aiogram.dispatcher.fsm.state import StatesGroup, State


class AllStates(StatesGroup):

    main_menu = State()
    dialog_menu = State()

    search_theme = State()
    write_theme = State()
    waiting_user = State()
    in_dialog = State()
    cancel = State()

    buy_subscription = State()
    start_buy = State()
    check_buy = State()
    successful_payment = State()
    unsuccessful_payment = State()


