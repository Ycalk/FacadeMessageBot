from maxapi.types import MessageCallback, MessageCreated, CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder

from bot.texts import Texts


def build_restart_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(CallbackButton(text='Начать заново', payload='new_message'))
    return keyboard


async def reply_wrong_step_for_callback(event: MessageCallback) -> None:
    keyboard = build_restart_keyboard()
    await event.message.answer(
        text=Texts.Messages.wrong_step,
        attachments=[keyboard.as_markup()],
    )


async def reply_wrong_step_for_message(event: MessageCreated) -> None:
    keyboard = build_restart_keyboard()
    await event.message.answer(
        text=Texts.Messages.wrong_step,
        attachments=[keyboard.as_markup()],
    )
