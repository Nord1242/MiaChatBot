from aiogram_dialog import DialogRegistry
from .windows import menu_window, buy_sub, dialog_theme_window, admin_window, random_dialog_windows


async def registry_dialog(registry: DialogRegistry):
    registry.register(admin_window)
    registry.register(menu_window)
    registry.register(buy_sub)
    registry.register(random_dialog_windows)
    registry.register(dialog_theme_window)
