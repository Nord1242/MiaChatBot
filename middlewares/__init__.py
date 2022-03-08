from keyboards.inline.dialog_keyboard import Dialog
from .dialog_middleware import DialogMiddleware
# from .storage_kwargs import StorageKwargs
from aiogram.dispatcher.fsm.storage.base import BaseStorage
from loader import dp, bot


def setup_middleware():
    dp.message.middleware(DialogMiddleware())
    # dp.message.middleware(StorageKwargs())
