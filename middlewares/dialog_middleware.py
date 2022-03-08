import re
from pprint import pprint

from aiogram import BaseMiddleware, Bot
from aiogram.dispatcher.fsm.storage.base import BaseStorage, StorageKey
from typing import Any, Awaitable, Callable, Dict
from aiogram.types import Message
from states.dialog_state import DialogState


class DialogMiddleware(BaseMiddleware):

    def __init__(self):
        super().__init__()
        print('ss')

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]):
        # pattern = r"\w+:\w+"
        user_id = event.from_user.id
        print(f'В мидл вари сейчас {user_id}')
        bot = data['bot']
        fsm_storage = data['fsm_storage']
        state = data['state']
        state_user = await state.get_state()
        state_data = await state.get_data()
        try:
            companion = state_data['companion_id']
            companion_state = await fsm_storage.get_state(bot=bot, key=StorageKey(user_id=companion, chat_id=companion,
                                                                                  bot_id=bot.id))
            print(f'state_user: {state_user}\ncompanion_state: {companion_state}')
        except KeyError:
            pass
        # re.search(pattern, str(DialogState.in_dialog)).group()
        # if companion_state == state_user:
        #     await event.copy_to(companion)
        return await handler(event, data)
