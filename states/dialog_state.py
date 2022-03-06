from aiogram.dispatcher.fsm.state import StatesGroup, State


class DialogState(StatesGroup):
    write_theme = State()
    waiting_user = State()
    in_dialog = State()
