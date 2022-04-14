import asyncio
import aiohttp


async def main():
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:8443/check-pay',
                                json={"ss": 29423212}) as rest:
            print(await rest.json(content_type=None))

if __name__ == '__main__':
    asyncio.run(main())

# from aiogram import types
# from loader import dp, bot, registry
# from states import all_state
#
# chat=types.Chat(id=455559956, type='private', title=None, username='nord3212', first_name='Пупа', last_name=None, photo=None, bio=None, has_private_forwards=None, description=None, invite_link=None, pinned_message=None, permissions=None, slow_mode_delay=None, message_auto_delete_time=None, has_protected_content=None, sticker_set_name=None, can_set_sticker_set=None, linked_chat_id=None, location=None)
# user = types.User(id=455559956, is_bot=False, first_name='Пупа', last_name=None, username='nord3212', language_code='ru', can_join_groups=None, can_read_all_group_messages=None, supports_inline_queries=None)
# from aiogram_dialog.manager.bg_manager import BgManager
# intent_id='tVxg97'
# stack_id=''
#
#
# async def main():
#     nigger = BgManager(chat=chat, user=user, stack_id=stack_id, intent_id=intent_id, bot=bot, registry=registry)
#     nigger.switch_to(A)
#
#
# asyncio.run(main())