from states.dialog_state import AllStates
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Group, Row, SwitchTo, Back, Next, Select, ScrollingGroup
from aiogram_dialog.widgets.text import Const, Format, Case
from aiogram_dialog.widgets.input import MessageInput
from handlers.user_dialog_v2 import create_dialog, cancel_search, join_in_dialog, suggested_themes, \
    text_join_in_dialog, cancel_dialog, get_user_id, who_cancel_dialog, dialog
import operator

dialog_window = Dialog(
    Window(
        Const("Вы в главном меню"),
        SwitchTo(Const('Меню диалогов'), id="dialog_menu", state=AllStates.dialog_menu, on_click=get_user_id),
        state=AllStates.main_menu,
    ),
    Window(
        Const("Вы в меню диалогов. Выберите пункт который вас интересует"),
        Group(
            SwitchTo(Const("Создать тему"), id="create_chat", state=AllStates.write_theme),
            SwitchTo(Const("Выбрать тему"), id="search_chat", state=AllStates.search_theme),
            Back(Const("В главное меню")),
            width=2
        ),

        state=AllStates.dialog_menu,
    ),
    Window(
        Const("Введите название темы"),
        Back(Const("Вернуться в меню диалогов")),
        MessageInput(create_dialog),
        state=AllStates.write_theme,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Ожидайте пользователя"),
        SwitchTo(Const("Отменить поиск"), id="cancel", state=AllStates.dialog_menu, on_click=cancel_search),
        state=AllStates.waiting_user
    ),
    Window(
        Const("Выберите тему ниже"),
        Select(
            Format("{item[0]}"),
            id="users_themes",
            item_id_getter=operator.itemgetter(1),
            items="themes_buttons",
            on_click=join_in_dialog,
        ),
        SwitchTo(Const("Вернуться в меню диалогов"), id="return_in_dialog_menu", state=AllStates.dialog_menu),
        getter=suggested_themes,
        state=AllStates.search_theme
    ),
    Window(
        Format("{text}"),
        MessageInput(dialog),
        SwitchTo(Const("Завершить диалог"), id="cancel_dialog", state=AllStates.cancel, on_click=cancel_dialog),
        state=AllStates.in_dialog,
        getter=text_join_in_dialog

    ),
    Window(
        Format("{text}"),
        SwitchTo(Const("Вернуться в меню диалогов"), id="return_in_dialog_menu", state=AllStates.dialog_menu),
        state=AllStates.cancel,
        getter=who_cancel_dialog
    )

)
