from states.dialog_state import DialogState
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Group, Row, SwitchTo, Back, Next, Select
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import MessageInput
from handlers.user_dialog_v2 import create_dialog, delete_theme, on_user_theme, suggested_themes
import operator



dialog_window = Dialog(
    Window(
        Const("Вы в главном меню"),
        SwitchTo(Const('Меню диалогов'), id="dialog_menu", state=DialogState.dialog_menu),
        state=DialogState.main_menu,
    ),
    Window(
        Const("Вы в меню диалогов. Выберите пункт который вас интересует"),
        Group(
            SwitchTo(Const("Создать тему"), id="create_chat", state=DialogState.write_theme),
            SwitchTo(Const("Выбрать тему"), id="search_chat", state=DialogState.search_theme),
            Back(Const("В главное меню")),
            width=2
        ),

        state=DialogState.dialog_menu,
    ),
    Window(
        Const("Введите название темы"),
        Back(Const("Вернуться в меню диалогов")),
        MessageInput(create_dialog),
        state=DialogState.write_theme,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Ожидайте пользователя"),
        SwitchTo(Const("Отменить поиск"), id="cancel", state=DialogState.dialog_menu, on_click=delete_theme),
        state=DialogState.waiting_user
    ),
    Window(
        Const("Выберите тему ниже"),
        Select(
            Format("{item[0]}"),
            id="users_themes",
            item_id_getter=operator.itemgetter(1),
            items="themes_buttons",
            on_click=on_user_theme,
        ),
        getter=suggested_themes,
        state=DialogState.search_theme





    )

)
