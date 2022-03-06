from aiogram.dispatcher.fsm.context import FSMContext
from loader import dp, session
from aiogram import types
from states.dialog_state import DialogState
from keyboards.inline.dialog_keyboard import get_dialog_keyboard, Dialog, cancel_dialog, EndDialog, \
    get_theme_keyboard
from aiogram import F
from models.models import ThemeTable
from typing import Union


class Choice(str):
    CREATOR = "create_dialog"
    JOIN = "join_in_dialog"
    CANCEL = "cancel_dialog"


@dp.message(commands={'dialog'})
async def start_dialog(message: types.Message):
    await main_dialog_menu(message)


async def main_dialog_menu(message: Union[types.Message, types.CallbackQuery], **kwargs):
    text = "Выберите кноку ниже"
    keyboard = get_dialog_keyboard()
    if isinstance(message, types.Message):
        await message.answer(text, reply_markup=keyboard)
    elif isinstance(message, types.CallbackQuery):
        call = message
        await call.message.edit_text(text=text,reply_markup=keyboard)


async def check_dialog_theme(call: types.CallbackQuery):
    all_themes = ThemeTable.get_all_theme()
    user_themes = get_theme_keyboard(all_themes)
    await call.message.edit_text(text="Выберите тему ниже либо отмените поиск", reply_markup=user_themes)


@dp.callback_query(Dialog.filter())
async def navigate(call: types.CallbackQuery, callback_data: Dialog):
    current_level = callback_data.dict().get('level')
    levels = {
        0: main_dialog_menu,
        1: check_dialog_theme
    }
    current_level_function = levels[current_level]
    await current_level_function(call)


@dp.callback_query(Dialog.filter(F.choice == Choice.CREATOR))
async def get_dialog_name(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(DialogState.write_theme)
    await call.message.edit_text(f'Введите название темы')


@dp.message(DialogState.write_theme)
async def create_dialog(message: types.Message, state: FSMContext):
    theme_name = message.text
    await state.set_state(DialogState.waiting_user)
    new_theme = ThemeTable(theme_name=theme_name,
                           telegram_user_id=message.from_user.id)
    session.add(new_theme)
    session.commit()
    keyboard = cancel_dialog()
    await message.answer(f"Ожидайте пользователя", reply_markup=keyboard)


@dp.callback_query(DialogState.waiting_user, EndDialog.filter(F.status == Choice.CANCEL))
async def cancel_user_dialog(call: types.CallbackQuery, state: FSMContext):
    session.query(ThemeTable).filter(ThemeTable.telegram_user_id == call.from_user.id).delete()
    session.commit()
    if DialogState.waiting_user:
        await call.message.edit_text('Вы отменили поиск!\nДля создание или поиска диалога введите /dialog')
    elif DialogState.in_dialog:
        await call.message.edit_text('Вы завершили диалог!\nДля создание или поиска диалога введите /dialog')
    await state.clear()
