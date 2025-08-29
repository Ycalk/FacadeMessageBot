from maxapi.types import BotStarted, MessageCreated, CallbackButton, LinkButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.enums.parse_mode import ParseMode
from maxapi.types import InputMedia
from maxapi import Bot
from bot.utils import Texts, Config
from typing import Union


async def start_handler(event: Union[BotStarted, MessageCreated], bot: Bot) -> None:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        LinkButton(
            text=Texts.Buttons.terms_of_use,
            url=Config.TERMS_OF_USE_URL,
        )
    )
    keyboard.row()
    keyboard.add(
        CallbackButton(
            text=Texts.Buttons.send_message,
            payload="send_message",
        )
    )

    # Создаем изображение для стартового сообщения
    image_attachment = InputMedia(path="/home/bot/app/test.png")

    attachments = [keyboard.as_markup(), image_attachment]

    await bot.send_message(
        user_id=event.user.user_id if hasattr(event, 'user') else event.message.sender.user_id,
        text=Texts.Messages.start,
        parse_mode=ParseMode.MARKDOWN,
        attachments=attachments,
    )
