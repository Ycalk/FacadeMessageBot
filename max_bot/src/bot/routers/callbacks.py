from maxapi import Router, F
from maxapi.enums.parse_mode import ParseMode

from bot.instance import antispam, send_message
from bot.texts import Texts
from bot.handlers.send_message import send_message_handler
from bot.handlers.write_greeting import write_greeting_handler
from bot.handlers.confirm_city import confirm_city
from bot.handlers.choose_background import choose_background
from bot.handlers.preview import send_to_moderation
from bot.handlers.use_profile_name import use_profile_name
from bot.handlers.back_handler import back_button
from bot.handlers.want_photo import want_photo_yes_handler, want_photo_no_handler
from bot.handlers.edit_greeting import edit_greeting_handler
from services.app_settings import get_accepting_messages

callbacks_router = Router(router_id='callbacks')


async def _check_spam(event) -> bool:
    """Проверяет антиспам. Возвращает True если заблокирован."""
    user_id = event.callback.user.user_id
    if not await antispam.record_action(user_id):
        await event.message.answer(text=Texts.Messages.spam_blocked)
        return True
    return False


async def _check_accepting(event) -> bool:
    """Проверяет приём сообщений. Возвращает True если приём закрыт."""
    user_id = event.callback.user.user_id
    if not await get_accepting_messages():
        await send_message(
            user_id=user_id,
            text=Texts.Messages.messages_not_accepting,
            parse_mode=ParseMode.MARKDOWN,
        )
        return True
    return False


@callbacks_router.message_callback(F.callback.payload == 'send_message')
async def _send_message(event):
    if await _check_accepting(event):
        return
    if await _check_spam(event):
        return
    await send_message_handler(event)


@callbacks_router.message_callback(F.callback.payload == 'new_message')
async def _new_message(event):
    if await _check_accepting(event):
        return
    if await _check_spam(event):
        return
    await send_message_handler(event)


@callbacks_router.message_callback(F.callback.payload == 'write_greeting')
async def _write_greeting(event):
    if await _check_accepting(event):
        return
    if await _check_spam(event):
        return
    await write_greeting_handler(event)


@callbacks_router.message_callback(
    F.callback.payload.in_(['confirm_city', 'try_again_city'])
)
async def _confirm_city(event):
    if await _check_accepting(event):
        return
    if await _check_spam(event):
        return
    await confirm_city(event)


@callbacks_router.message_callback(F.callback.payload.startswith('background_'))
async def _choose_background(event):
    if await _check_accepting(event):
        return
    if await _check_spam(event):
        return
    await choose_background(event)


@callbacks_router.message_callback(F.callback.payload == 'send_to_moderation')
async def _send_to_moderation(event):
    if await _check_accepting(event):
        return
    if await _check_spam(event):
        return
    await send_to_moderation(event)


@callbacks_router.message_callback(F.callback.payload == 'use_profile_name')
async def _use_profile_name(event):
    if await _check_accepting(event):
        return
    if await _check_spam(event):
        return
    await use_profile_name(event)


@callbacks_router.message_callback(F.callback.payload == 'edit_greeting')
async def _edit_greeting(event):
    if await _check_accepting(event):
        return
    if await _check_spam(event):
        return
    await edit_greeting_handler(event)


@callbacks_router.message_callback(F.callback.payload.startswith('want_photo_yes_'))
async def _want_photo_yes(event):
    if await _check_spam(event):
        return
    await want_photo_yes_handler(event)


@callbacks_router.message_callback(F.callback.payload.startswith('want_photo_no_'))
async def _want_photo_no(event):
    if await _check_spam(event):
        return
    await want_photo_no_handler(event)


# Универсальная кнопка "Назад"
@callbacks_router.message_callback(F.callback.payload == 'back')
async def _back(event):
    if await _check_accepting(event):
        return
    if await _check_spam(event):
        return
    await back_button(event)
