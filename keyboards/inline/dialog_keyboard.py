from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class Dialog(CallbackData, prefix="start_dialog"):
    choice: str = None
    user_id: int = None


def cancel_dialog(user_id):
    markup = InlineKeyboardBuilder()
    markup.add(
        InlineKeyboardButton(
            text="Завершить диалог",
            callback_data=Dialog(status="cancel_dialog", user_id=user_id).pack()
        )
    )
    markup.adjust(1, repeat=True)
    return markup.as_markup(resize_keyboard=True)
