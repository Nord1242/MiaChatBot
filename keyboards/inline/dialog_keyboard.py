from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class Dialog(CallbackData, prefix="start_dialog"):
    choice: str = None
    level: int = None
    user_id: int = None


def get_dialog_keyboard():
    markup = InlineKeyboardBuilder()
    level = 0
    markup.add(
        InlineKeyboardButton(
            text="Найти собеседника",
            callback_data=Dialog(choice="create_dialog", level=level + 2).pack()),
        InlineKeyboardButton(
            text="Присоединиться к диалогу",
            callback_data=Dialog(choice="join_in_dialog", level=level + 1).pack())
    )
    markup.adjust(1, repeat=True)
    return markup.as_markup(resize_keyboard=True)


def cancel_dialog(user_id):
    markup = InlineKeyboardBuilder()
    level = 2
    markup.add(
        InlineKeyboardButton(
            text="Отменить",
            callback_data=Dialog(status="cancel_dialog", user_id=user_id, level=level+1).pack()
        )
    )
    markup.adjust(1, repeat=True)
    return markup.as_markup(resize_keyboard=True)


def gef_return_in_menu():
    level = 3
    markup = InlineKeyboardBuilder()
    markup.add(
        InlineKeyboardButton(
            text='Вернуться в меню диалога',
            callback_data=Dialog(level=level - 3).pack(
            )
        ))
    markup.adjust(1, repeat=True)
    return markup.as_markup(resize_keyboard=True)


def get_theme_keyboard(themes):
    markup = InlineKeyboardBuilder()
    level = 1
    user_themes = list()
    for theme in themes:
        user_themes.append(
            InlineKeyboardButton(
                text=theme.theme_name,
                callback_data=Dialog(user_id=int(theme.telegram_user_id), choice="in_dialog", level=level+2).pack()
            )
        )
    markup.add(*user_themes)
    markup.adjust(1, repeat=True)
    markup.add(
        InlineKeyboardButton(
            text='Вернуться в меню диалога',
            callback_data=Dialog(level=level - 1).pack(
            )
        ))
    markup.adjust(1, repeat=True)
    return markup.as_markup(resize_keyboard=True)
