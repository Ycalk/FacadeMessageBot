from maxapi import Router, F

from bot.handlers.start import start_handler

system_router = Router(router_id='system')


@system_router.message_created(F.message.body.text == '/start')
async def _start_command(event):
    await start_handler(event, event.bot)


@system_router.bot_started()
async def _bot_started(event):
    await start_handler(event, event.bot)
