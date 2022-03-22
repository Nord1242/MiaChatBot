from aiogram.dispatcher.fsm.state import StatesGroup, State


class AllStates(StatesGroup):
    buy_subscription = State()
    buy_done = State()

    main_menu = State()
    dialog_menu = State()

    search_theme = State()
    write_theme = State()
    waiting_user = State()
    in_dialog = State()
    cancel = State()

    start_reg = State()

    form_done = State()
