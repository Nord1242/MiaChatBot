from aiogram.dispatcher.fsm.state import StatesGroup, State


class DialogState(StatesGroup):
    main_menu = State()
    dialog_menu = State()
    search_theme = State()
    write_theme = State()
    waiting_user = State()
    in_dialog = State()
    cancel = State()
