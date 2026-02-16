from maxapi import Router, F

from bot.handlers.send_message import send_message_handler
from bot.handlers.confirm_city import confirm_city
from bot.handlers.choose_background import choose_background
from bot.handlers.preview import send_to_moderation
from bot.handlers.use_profile_name import use_profile_name
from bot.handlers.back_handler import back_button

callbacks_router = Router(router_id='callbacks')


@callbacks_router.message_callback(F.callback.payload == 'send_message')
async def _send_message(event):
    await send_message_handler(event)


@callbacks_router.message_callback(F.callback.payload == 'new_message')
async def _new_message(event):
    await send_message_handler(event)


@callbacks_router.message_callback(
    F.callback.payload.in_(['confirm_city', 'try_again_city'])
)
async def _confirm_city(event):
    await confirm_city(event)


@callbacks_router.message_callback(F.callback.payload.startswith('background_'))
async def _choose_background(event):
    await choose_background(event)


@callbacks_router.message_callback(F.callback.payload == 'send_to_moderation')
async def _send_to_moderation(event):
    await send_to_moderation(event)


@callbacks_router.message_callback(F.callback.payload == 'use_profile_name')
async def _use_profile_name(event):
    await use_profile_name(event)


# Универсальная кнопка "Назад"
@callbacks_router.message_callback(F.callback.payload == 'back')
async def _back(event):
    await back_button(event)
