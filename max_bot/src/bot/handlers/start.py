from typing import Union
from core.logger import get_logger

from maxapi import Bot
from maxapi.types import BotStarted, MessageCreated, CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder

from bot.texts import Texts

logger = get_logger(__name__)


async def start_handler(event: Union[BotStarted, MessageCreated], bot: Bot) -> None:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        CallbackButton(
            text=Texts.Buttons.send_message,
            payload="send_message",
        )
    )

    user_id = (
        event.user.user_id
        if hasattr(event, "user")
        else event.message.sender.user_id
    )

    await bot.send_message(
        user_id=user_id,
        text=Texts.Messages.start,
        attachments=[keyboard.as_markup()],
    )