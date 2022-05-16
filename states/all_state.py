from aiogram.dispatcher.fsm.state import StatesGroup, State


class AdminStates(StatesGroup):
    admin_menu = State()
    add_end_dialog = State()
    distribution_message = State()
    success_send = State()


class MenuStates(StatesGroup):
    captcha = State()
    main_menu = State()
    not_companion = State()
    gender = State()
    ban_sub = State()
    ban = State()
    time_ban = State()


class ThemeDialogStates(StatesGroup):
    choose_cat = State()
    set_report = State()
    report = State()
    timeout = State()
    dialog_menu = State()
    search_theme = State()
    write_theme = State()
    waiting_user_theme = State()
    in_dialog_theme = State()
    cancel_theme = State()


class RandomDialogStates(StatesGroup):
    get_gender = State()
    get_menu_gender = State()
    set_report = State()
    report = State()
    report = State()
    waiting_user = State()
    in_dialog = State()
    cancel = State()


class BuyStates(StatesGroup):
    show_sub_info = State()
    buy_subscription = State()
    start_buy = State()
    check_buy = State()
    successful_payment = State()
    unsuccessful_payment = State()
