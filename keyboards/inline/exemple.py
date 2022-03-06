from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class LevelTable(CallbackData, prefix='level_table'):
    level_id: int


def get_level_keyboard(array) -> InlineKeyboardMarkup:
    markup = InlineKeyboardBuilder()
    level_button = list()
    for lv in array:
        level_button.append(
            InlineKeyboardButton(
                text=f'{lv.name} - {lv.price} ₽',
                callback_data=LevelTable(level_id=lv.id).pack()
            )
        )

    markup.add(*level_button)
    markup.adjust(1, repeat=True)
    return markup.as_markup(resize_keyboard=True)