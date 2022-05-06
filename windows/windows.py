import datetime

from states.all_state import MenuStates, ThemeDialogStates, RandomDialogStates, BuyStates, AdminStates

from aiogram_dialog import Dialog, Window, DialogManager, ChatEvent
from aiogram_dialog.widgets.kbd import Button, Group, SwitchTo, Back, Next, Select, ScrollingGroup, Column, Row, \
    ListGroup, Checkbox, Url, ManagedCheckboxAdapter, Radio
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import MessageInput

from handlers.admin.distribution_message import distribution_message, get_send_data

from handlers.user.user_theme_dialog import create_dialog, join_in_dialog, suggested_themes, text_join_in_dialog, \
    who_cancel_dialog, dialog
from handlers.user.dialog_utils import cancel_search, cancel_dialog, report
from handlers.user.random_user import search_random_user
from handlers.user.buy_subscription import buy_subscription, get_subscriptions, get_data_for_buy, get_top
from handlers.user.user import get_profile_data, when_checked, check_changed, get_sub_data, checks_restrictions, \
    check_top, buy_sub, write_theme, unban, time_ban_info, get_captcha, check_captcha, ban_info, timeout
from handlers.user.router import return_menu, start_buy_sub, return_to_search_theme, go_in_sub_data, go_in_create_theme
import operator
from aiogram_dialog.widgets.text import Jinja

#

# ✖≡

admin_window = Dialog(
    Window(
        Const("Добро пожаловать в меню админа"),
        SwitchTo(Const("Рассылка сообщения"), id="distribution_message", state=AdminStates.distribution_message),
        SwitchTo(Const("Реклама в конец диалога"), id="add_end_dialog", state=AdminStates.add_end_dialog),
        state=AdminStates.admin_menu
    ),
    Window(
        Const("Вставь сообщение"),
        MessageInput(distribution_message),
        state=AdminStates.distribution_message
    ),
    Window(
        Const("Вставь сообщение"),
        MessageInput(distribution_message),
        state=AdminStates.add_end_dialog
    ),
    Window(
        Format("Сообщение пришло: {success} {text}\nЗаблокировали бота: {unsuccess} {unsuc_text}"),
        SwitchTo(Const("В меню админа"), state=AdminStates.admin_menu, id="return_admin_menu"),
        state=AdminStates.success_send,
        getter=get_send_data

    )
)

menu_window = Dialog(
    Window(
        Jinja(
            "Добро пожаловать в систему Mia!\nПрошу пройти капчу, для подтверждения того, что вы являетесь человеком 👀\n"
            "\nНеобходимо выбрать точно такой же шар {{captcha}}\n У вас осталось <code>{{counter}} попыт{{ending}}</code>"),
        Group(
            Select(
                Format("{item[0]}"),
                id="captcha",
                item_id_getter=operator.itemgetter(1),
                items="captcha_balls",
                on_click=check_captcha
            ), width=4),
        getter=get_captcha,
        state=MenuStates.captcha

    ),
    Window(
        Format('⛔️ Вы были забанены в боте по причине:\n└{user_ban}'),
        getter=ban_info,
        state=MenuStates.ban),
    Window(
        Format(
            "⛔️ Вы были забанены в боте по причине:\n└{user_ban}\n\nУ вас обнаружена подписка, поэтому у вас есть шанс всё исправить! 🥳"),
        Select(
            Format("{item[0]}"),
            id="unban_start",
            item_id_getter=operator.itemgetter(1),
            items="unban",
            on_click=buy_subscription
        ),
        getter=unban,
        state=MenuStates.ban_sub),
    Window(
        Format(
            '⛔️ Вы были временно забанены в боте по причине:\n└{user_ban}\n\nПопробуйте через {min} минут{end} ⏳'),
        getter=time_ban_info,
        state=MenuStates.time_ban,
    ),
    Window(
        Const("🏠️ Вы в главном меню"),
        Checkbox(
            Const("✕ Профиль"),
            Const("≡ Профиль"),
            id="check",
            default=False,
            on_state_changed=check_changed,
        ),
        Group(
            Button(Format("Ник: {login}"), id="login"),
            Button(Const("Подписка ❌"), id="buy_sub", on_click=start_buy_sub,
                   when=lambda data, w, m: data["sub"] is None),
            Button(Const("Подписка ✅"), id="show_sub_data", on_click=go_in_sub_data,
                   when=lambda data, w, m: data["sub"]),
            when=when_checked,
            width=2
        ),
        Button(Const('💬 Темы для диалога'), id="dialog_menu", on_click=return_to_search_theme),
        Button(Const('🔎 Поиск собеседника'), id="random_user", on_click=search_random_user),
        state=MenuStates.main_menu,
        getter=get_profile_data
    ),
    Window(
        Const(
            "В данный момент вы не находитесь в диалоге с собеседником.\n"
            "Выберите один из пунктов ниже, чтобы найти его"),
        Row(
            Button(Const('💬 Темы для диалога'), id="dialog_menu", on_click=return_to_search_theme),
            Button(Const('🔎 Поиск собеседника'), id="random_user",
                   on_click=search_random_user),
        ),
        SwitchTo(Const("🏠️ В главное меню"), id="return_to_main_menu", state=MenuStates.main_menu),
        state=MenuStates.not_companion
    )
)

dialog_theme_window = Dialog(
    # Window(
    #     Const("Добро пожаловать в меню диалогов! 💬\n\n"
    #           "Проявите инициативу, создав интересную тему для пользователей нашей системы или выберите "
    #           "её из списка доступных, выбор за вами."),
    #     Group(
    #         SwitchTo(Const("🗃 Выбрать тему"), id="search_chat", state=ThemeDialogStates.search_theme),
    #         width=2
    #     ),
    #
    #     state=ThemeDialogStates.dialog_menu,
    # ),
    Window(
        Const("⬇️ Выберите тему ниже"),
        Row(Button(Const("💎💎💎💎💎💎💎 Топ темы 💎💎💎💎💎💎💎"), id="top")),
        Group(
            Select(
                Format("{item[0]}"),
                id="top_themes",
                item_id_getter=operator.itemgetter(1),
                items="top_button",
                on_click=join_in_dialog,

            ),
            width=2),
        Row(Button(Const("💎💎💎💎💎💎💎 Топ темы 💎💎💎💎💎💎💎"), id="top")),
        ScrollingGroup(
            Select(
                Format("{item[0]}"),
                id="users_themes",
                item_id_getter=operator.itemgetter(1),
                items="themes_buttons",
                on_click=join_in_dialog,
            ),
            id="themes_menu",
            width=2,
            height=10
        ),
        Button(Const("📝 Создать тему"), id="create_chat", on_click=checks_restrictions),
        Button(Const("🏠 В главное меню"), id="return_to_main_menu", on_click=return_menu),
        getter=suggested_themes,
        state=ThemeDialogStates.search_theme
    ),
    # Window(
    #     Format(
    #         "Вы исчерпали количество доступных тем 😔\nСоздать новую можно через\n"
    #         "{hour} час{hour_end} {minutes} минут{minutes_end}⏳\n"
    #         "\nНе хотите ждать?\nСнимите ограничение уже сейчас, приобретя премиум доступ!"
    #         "\nОзнакомится с доступным списком привилегий, можно по кнопке\nниже👇🏻"),
    #     Button(Const("💎 Приобрести подписку"), id="buy_sub", on_click=start_buy_sub),
    #     SwitchTo(Const("💬 В меню диалогов"), id="return_to_menu", state=ThemeDialogStates.dialog_menu),
    #     state=ThemeDialogStates.timeout,
    #     getter=timeout
    # ),
    Window(
        Const("Введите название темы"),
        Select(
            Format("{item[0]}"),
            id="top_buttons",
            item_id_getter=operator.itemgetter(1),
            items="product_button",
            on_click=buy_subscription,
            when=lambda data, w, m: not data['top']
        ),
        SwitchTo(Const("💬 К выбору тем"), state=ThemeDialogStates.search_theme, id="return_to_menu"),
        Row(
            Checkbox(
                Const("⚪️ Поднять в топ 💎"),
                Const("🔘 Поднять в топ 💎"),
                id="check_top",
                default=True,
                on_state_changed=check_top,
            ), when=lambda data, w, m: data['top'] is True),
        MessageInput(create_dialog),
        state=ThemeDialogStates.write_theme,
        getter=get_top
    ),
    Window(
        Const("🕵️‍♂️ Ожидайте собеседника"),
        Button(Const("🚫 Отменить поиск"), id="cancel", on_click=cancel_search),
        state=ThemeDialogStates.waiting_user_theme
    ),
    Window(
        Format("{text}"),
        MessageInput(dialog),
        SwitchTo(Const("🛑 Завершить диалог"), id="cancel_dialog", on_click=cancel_dialog,
                 state=ThemeDialogStates.cancel_theme),
        state=ThemeDialogStates.in_dialog_theme,
        getter=text_join_in_dialog

    ),
    Window(
        Format("{text}"),
        Row(Button(Const("💬 К выбору тем"), id="return_to_dialog_menu", on_click=return_to_search_theme),
            SwitchTo(Const("📢 Пожаловаться"), id="report", state=ThemeDialogStates.set_report)),
        state=ThemeDialogStates.cancel_theme,
        getter=who_cancel_dialog
    ),
    Window(
        Format("{text}"),
        Column(
            Select(
                Format("{item[0]}"),
                id="report",
                item_id_getter=operator.itemgetter(1),
                items="report_button",
                on_click=report,
            )),
        Back(Const("🔙 Назад")),
        getter=who_cancel_dialog,
        state=ThemeDialogStates.set_report
    ),
    Window(
        Const("📨 Жалоба была отправлена!\n\nСпасибо что делаете нашего бота лучше ☺️"),
        Button(Const("💬 К выбору тем"), id="return_to_dialog_menu", on_click=return_to_search_theme),
        state=ThemeDialogStates.report
    )

)

random_dialog_windows = Dialog(
    Window(
        Const("🕵️‍♂️ Ожидайте собеседника"),
        Button(Const("🚫 Отменить поиск"), id="cancel", on_click=cancel_search),
        state=RandomDialogStates.waiting_user
    ),
    Window(
        Const(
            "Пользователь найден! 👀\nЧтобы завершить диалог, нажмите кнопку ниже или воспользуйтесь командой: /stop"),
        MessageInput(dialog),
        SwitchTo(Const("🛑 Завершить диалог"), id="cancel_random_dialog", on_click=cancel_dialog,
                 state=RandomDialogStates.cancel),
        state=RandomDialogStates.in_dialog,
    ),
    Window(
        Format("{text}"),
        Row(Button(Const('🔎 Найти следующего собеседника'), id="random_user", on_click=search_random_user),
            SwitchTo(Const("📢 Пожаловаться"), id="report", state=RandomDialogStates.set_report)),
        Button(Const("🏠️ В главное меню"), id="return_to_main_menu", on_click=return_menu),
        state=RandomDialogStates.cancel,
        getter=who_cancel_dialog
    ),
    Window(
        Format("{text}"),
        Column(
            Select(
                Format("{item[0]}"),
                id="report",
                item_id_getter=operator.itemgetter(1),
                items="report_button",
                on_click=report,
            )),
        Back(Const("🔙 Назад")),
        getter=who_cancel_dialog,
        state=RandomDialogStates.set_report
    ),
    Window(
        Const("📨 Жалоба была отправлена!\n\nСпасибо что делаете нашего бота лучше ☺️"),
        Button(Const("🏠 В главное меню"), id="return_to_main_menu", on_click=return_menu),
        state=RandomDialogStates.report
    )
)

buy_sub = Dialog(
    Window(
        Format("{text}"),
        Button(Const("️🏠️ В главное меню"), id="return_to_menu", on_click=return_menu),
        state=BuyStates.show_sub_info,
        getter=get_sub_data
    ),
    Window(
        Const("🔥 Плюсы наличия подписки:\n"
              "- отсутствует ограничение на количество создаваемых тем;\n"
              "- сокращение шанса словить бан в нашей системе;\n"
              "- в случае бана вашего аккаунта, <b>есть возможность разбана.</b>\n\n"
              "⚠️ На подписку не распространяется:\n"
              "└ продвижение вашей темы в топ;\n"
              "└ разбан вашего аккаунта в системе.\n\n"

              "Подписка выдаётся после проведения успешной оплаты ✅"),
        Column(
            Select(
                Format("{item[0]}"),
                id="subscriptions_buttons",
                item_id_getter=operator.itemgetter(1),
                items="subscriptions",
                on_click=buy_subscription
            ),
            Button(Const("🏠️ В главное меню"), id='return_to_menu', on_click=return_menu)
        ),
        parse_mode="html",
        getter=get_subscriptions,
        state=BuyStates.buy_subscription
    ),
    Window(
        Format('💵 Стоимость товара: {amount}₽'),
        Url(
            Const('💳 Оплатить товар'),
            Format('{url}'),
        ),
        Back(Const("🔙 Назад"), when=buy_sub),
        Button(Const("🔙 Назад"), on_click=go_in_create_theme, when=write_theme, id="return_to_write"),
        getter=get_data_for_buy,
        state=BuyStates.start_buy
    ),
    Window(
        Const("Оплата прошла успешно, теперь вы можете комфортно общаться с пользователями нашей системы 😎"),
        Button(Const("🏠️ В главное меню"), id="return_to_main_menu", on_click=return_menu),
        state=BuyStates.successful_payment,
    ),
)
