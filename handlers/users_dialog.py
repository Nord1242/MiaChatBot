import asyncio
import re
from aiogram.dispatcher.fsm.context import FSMContext
from loader import dp, session
from aiogram import types, Bot
from aiogram.dispatcher.fsm.storage.base import BaseStorage, StorageKey
from states.dialog_state import DialogState
from keyboards.inline.dialog_keyboard import get_dialog_keyboard, Dialog, cancel_dialog, get_theme_keyboard, \
    gef_return_in_menu
from aiogram import F
from models.models import ThemeTable
from typing import Union
from middlewares import DialogMiddleware

PATTERN_RE = r"\w+:\w+"


class Choice(str):
    CREATOR = "create_dialog"
    JOIN = "join_in_dialog"
    CANCEL = "cancel_dialog"
    IN_DIALOG = "in_dialog"


@dp.message(commands={'start'})
async def start_dialog(message: types.Message, state: FSMContext, bot: Bot):
    await main_dialog_menu(message=message, state=state, bot=bot)


async def main_dialog_menu(message: Union[types.Message, types.CallbackQuery], state: FSMContext, bot: Bot, **kwargs):
    text = "Выберите кноку ниже"
    keyboard = get_dialog_keyboard()
    if isinstance(message, types.Message):
        await message.answer(text, reply_markup=keyboard)
    elif isinstance(message, types.CallbackQuery):
        call = message
        user_data = await state.get_data()
        try:
            cancel_message_id = user_data['cancel_message_id']
            await bot.delete_message(message_id=cancel_message_id, chat_id=call.from_user.id)
            await bot.send_message(text=text, reply_markup=keyboard, chat_id=call.from_user.id)
        except KeyError:
            await call.message.edit_text(text=text, reply_markup=keyboard)
        await state.clear()


async def check_dialog_theme(call: types.CallbackQuery, state: FSMContext, **kwargs):
    all_themes = ThemeTable.get_all_theme()
    user_themes = get_theme_keyboard(all_themes)
    await state.set_state(DialogState.search_theme)
    await call.message.edit_text(text="Выберите тему ниже либо отмените поиск", reply_markup=user_themes)


async def get_dialog_name(call: types.CallbackQuery, state: FSMContext, **kwargs):
    await state.set_state(DialogState.write_theme)
    await state.update_data(menu_id=call.message.message_id)
    return_keyboard = gef_return_in_menu()
    await call.message.edit_text(f'Введите название темы', reply_markup=return_keyboard)


async def cancel_user_dialog(call: types.CallbackQuery, state: FSMContext, callback_data: Dialog, bot: Bot,
                             fsm_storage: BaseStorage):
    return_keyboard = gef_return_in_menu()
    state_waiting_user = re.search(PATTERN_RE, str(DialogState.waiting_user)).group()
    if await state.get_state() == state_waiting_user:
        cancel_message_id = await call.message.edit_text('Вы отменили поиск', reply_markup=return_keyboard)
        await state.update_data(cancel_message_id=cancel_message_id.message_id)
        session.query(ThemeTable).filter(ThemeTable.telegram_user_id == call.from_user.id).delete()
        session.commit()
    else:
        user_data = await state.get_data()
        companion = user_data['companion_id']
        companion_data = await fsm_storage.get_data(bot=bot,
                                                    key=StorageKey(user_id=companion, chat_id=companion, bot_id=bot.id))
        await call.message.edit_text('Вы завершили диалог', reply_markup=return_keyboard)
        await bot.delete_message(message_id=companion_data['menu_id'], chat_id=companion)
        await bot.send_message(text='Собеседник завершил диалог', reply_markup=return_keyboard, chat_id=companion)

        await state.clear()
        await fsm_storage.set_state(bot=bot, key=StorageKey(chat_id=companion, user_id=companion, bot_id=bot.id),
                                    state=None)


@dp.callback_query(Dialog.filter(F.choice != Choice.IN_DIALOG))
async def navigate(call: types.CallbackQuery, callback_data: Dialog, state: FSMContext, bot: Bot,
                   fsm_storage: BaseStorage):
    current_level = callback_data.dict().get('level')
    levels = {
        0: main_dialog_menu,
        1: check_dialog_theme,
        2: get_dialog_name,
        3: cancel_user_dialog,
    }
    current_level_function = levels[current_level]
    await current_level_function(call, state=state, callback_data=callback_data, bot=bot, fsm_storage=fsm_storage)


@dp.message(DialogState.write_theme)
async def create_dialog(message: types.Message, state: FSMContext, bot: Bot):
    theme_name = message.text
    await state.set_state(DialogState.waiting_user)
    new_theme = ThemeTable(theme_name=theme_name,
                           telegram_user_id=message.from_user.id)
    session.add(new_theme)
    session.commit()
    await state.set_state(DialogState.waiting_user)
    keyboard = cancel_dialog(message.from_user.id)
    user_data = await state.get_data()
    await bot.edit_message_text(f"Ожидайте пользователя", reply_markup=keyboard, message_id=user_data['menu_id'],
                                chat_id=message.from_user.id)


@dp.callback_query(Dialog.filter(F.choice == Choice.IN_DIALOG))
async def dialog(call: types.CallbackQuery, fsm_storage: BaseStorage, callback_data: Dialog, bot: Bot,
                 state: FSMContext):
    companion = callback_data.dict().get('user_id')
    user_id = call.from_user.id
    await state.update_data(companion_id=companion)
    storage_kwargs = {
        'storage_key': {
            'user_id': companion,
            'chat_id': companion,
            'bot_id': bot.id},
        'state_none': None,
        'state_in_dialog': DialogState.in_dialog
    }
    companion_state = await fsm_storage.get_state(bot=bot, key=StorageKey(**storage_kwargs['storage_key']))
    companion_data = await fsm_storage.get_data(bot=bot, key=StorageKey(**storage_kwargs['storage_key']))
    await fsm_storage.update_data(bot=bot, key=StorageKey(**storage_kwargs['storage_key']),
                                  data={'companion_id': call.from_user.id})
    state_wait = re.search(PATTERN_RE, str(DialogState.waiting_user)).group()
    if companion_state != str(state_wait):
        await call.message.edit_text("Пользователь уже нашел собеседника или отменил тему ")
        return
    session.query(ThemeTable).filter(ThemeTable.telegram_user_id == companion).delete()
    session.commit()
    await state.set_state(DialogState.in_dialog)
    await fsm_storage.set_state(bot=bot, key=StorageKey(**storage_kwargs['storage_key']),
                                state=storage_kwargs['state_in_dialog'])
    companion_keyboard = cancel_dialog(user_id=companion)
    keyboard = cancel_dialog(user_id=user_id)
    menu_id = await call.message.edit_text(text='Вы зашли в диалог! Чтобы выйти из него то нажмите кнопку ниже',
                                           reply_markup=keyboard)
    await state.update_data(menu_id=menu_id.message_id)
    await bot.delete_message(chat_id=companion, message_id=companion_data['menu_id'])
    menu_id = await bot.send_message(chat_id=companion, text='Пользователь найден',
                                     reply_markup=companion_keyboard)
    await fsm_storage.update_data(bot=bot, key=StorageKey(user_id=companion, chat_id=companion, bot_id=bot.id), data={
        'menu_id': menu_id.message_id
    })
