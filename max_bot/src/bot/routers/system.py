from maxapi import Router, F

from bot.handlers.start import start_handler

system_router = Router(router_id='system')


@system_router.message_created(F.message.body.text == '/start')
async def _start_command(event):
    await start_handler(event, event.bot)


@system_router.message_created(F.message.body.text == '/me')
async def _me_command(event):
    user_id = event.message.sender.user_id
    await event.message.answer(text=f"Ваш max_id: {user_id}")


@system_router.bot_started()
async def _bot_started(event):
    await start_handler(event, event.bot)
