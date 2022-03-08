# from pprint import pprint
#
# from aiogram import BaseMiddleware
# from aiogram.types import Message
# from aiogram import Bot
# from aiogram.dispatcher.fsm.storage.base import BaseStorage, StorageKey
# from typing import Any, Awaitable, Callable, Dict
# from aiogram.types import Message
#
# from keyboards.inline.dialog_keyboard import Dialog
# from states.dialog_state import DialogState
#
#
# class StorageKwargs(BaseMiddleware):
#     def __init__(self):
#         super().__init__()
#
#     async def __call__(
#             self,
#             handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
#             event: Message,
#             data: Dict[str, Any]):
#         pprint(data)
#         bot = data['bot']
#         # data['storage_key'] = {
#         #     'user_id': companion,
#         #     'chat_id': companion,
#         #     'bot_id': bot.id},
#         # data['state_none'] = None
#         # data['state_in_dialog'] = DialogState.in_dialog
#         await handler(event, data)
