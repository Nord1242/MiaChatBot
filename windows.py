from states.all_state import AllStates

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button, Group, SwitchTo, Back, Next, Select, ScrollingGroup, Column, Row, \
    ListGroup, Checkbox, Radio
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import MessageInput

from handlers.user.user_dialog import create_dialog, cancel_search, join_in_dialog, suggested_themes, \
    text_join_in_dialog, cancel_dialog, who_cancel_dialog, dialog, return_menu
from handlers.user.random_user import search_random_user
from handlers.user.buy_subscription import buy_subscription, get_subscriptions
from handlers.user.user import check_profile_in_base, get_login, reg_done, when_checked, \
    show_info_profile, show_button_reg
import operator
from aiogram_dialog.manager.protocols import LaunchMode
from typing import Dict

#


# ✖≡
dialog_window = Dialog(
    Window(
        Const("Вы в главном меню"),
        ListGroup(
            Checkbox(
                Format("✕ {item}"),
                Format("≡ {item}"),
                id="check",
            ),
            Group(
                Group(
                    Button(Format("Ник: {data[login]}"), id="login"),
                    Button(Const("👥 Контакты"), id="show_contacts"),
                    SwitchTo(Const("❌ Подписка"), id="buy_sub", state=AllStates.buy_subscription,
                             when=lambda data, w, m: data["data"]["sub"] is None),
                    when=show_info_profile,
                    width=2
                ),
                SwitchTo(Const("Регистрация"), id="registration", state=AllStates.start_reg,
                         when=show_button_reg),
                when=when_checked,
            ),
            id="lg",
            item_id_getter=str,
            items=["Профиль"],

        ),
        SwitchTo(Const('🔎 Случайный собеседник'), id="random_user", on_click=search_random_user,
                 state=AllStates.waiting_user),
        SwitchTo(Const('💬 Меню диалогов'), id="dialog_menu", state=AllStates.dialog_menu),
        state=AllStates.main_menu,
        getter=check_profile_in_base
    ),
    Window(
        Const("Введите ваш логин"),
        MessageInput(get_login),
        state=AllStates.start_reg,
    ),
    Window(
        Format("{text}"),
        SwitchTo(Const("ℹ️ В главное меню"), id='return_to_menu', state=AllStates.main_menu),
        getter=reg_done,
        state=AllStates.form_done

    ),
    Window(
        Const("Выберите срок подписки"),
        Column(
            Select(
                Format("{item[0]}"),
                id="subscriptions_buttons",
                item_id_getter=operator.itemgetter(1),
                items="subscriptions",
                on_click=buy_subscription
            ),
            SwitchTo(Const("ℹ️ В главное меню"), id='return_to_menu', state=AllStates.main_menu)
        ),
        getter=get_subscriptions,
        state=AllStates.buy_subscription
    ),
    Window(
        Const("Вы купили товар"),
        SwitchTo(Const("ℹ️ В главное меню"), id="return_to_main_menu", state=AllStates.main_menu),

        state=AllStates.buy_done
    ),

    Window(
        Const("Вы в меню диалогов. Выберите пункт который вас интересует"),
        Group(
            SwitchTo(Const("Создать тему"), id="create_chat", state=AllStates.write_theme),
            SwitchTo(Const("Выбрать тему"), id="search_chat", state=AllStates.search_theme),
            SwitchTo(Const("ℹ️ В главное меню"), id="return_to_main_menu", state=AllStates.main_menu),
            width=2
        ),

        state=AllStates.dialog_menu,
    ),
    Window(
        Const("Введите название темы"),
        Back(Const("Вернуться в меню диалогов")),
        MessageInput(create_dialog),
        state=AllStates.write_theme,
    ),
    Window(
        Const("🕵️‍♂️ Ожидайте собеседника"),
        Button(Const("Отменить поиск"), id="cancel", on_click=cancel_search),
        state=AllStates.waiting_user
    ),
    Window(
        Const("Выберите тему ниже"),
        ScrollingGroup(
            Select(
                Format("{item[0]}"),
                id="users_themes",
                item_id_getter=operator.itemgetter(1),
                items="themes_buttons",
                on_click=join_in_dialog,
            ),
            id="themes_menu",
            width=10,
            height=2
        ),
        SwitchTo(Const("Вернуться в меню диалогов"), id="return_to_dialog_menu", state=AllStates.dialog_menu),
        getter=suggested_themes,
        state=AllStates.search_theme
    ),
    Window(
        Format("{text}"),
        MessageInput(dialog),
        Button(Const("Завершить диалог"), id="cancel_dialog", on_click=cancel_dialog),
        state=AllStates.in_dialog,
        getter=text_join_in_dialog

    ),
    Window(
        Format("{text}"),
        Button(Format("{button}"), id="return_to_dialog_menu", on_click=return_menu),
        state=AllStates.cancel,
        getter=who_cancel_dialog
    )

)
