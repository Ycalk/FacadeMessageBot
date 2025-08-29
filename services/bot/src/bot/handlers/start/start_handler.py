from maxapi.types import BotStarted, MessageCreated, CallbackButton, LinkButton, Attachment, PhotoAttachmentPayload
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.enums.parse_mode import ParseMode
from maxapi.enums.attachment import AttachmentType
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
    
    attachments = [keyboard.as_markup()]
    
    if Config.START_MESSAGE_IMAGE_TOKEN and Config.START_MESSAGE_IMAGE_ID:
        # attachments.append(
        #     Attachment(
        #         type=AttachmentType.IMAGE,
        #         payload=PhotoAttachmentPayload(
        #             photo_id=Config.START_MESSAGE_IMAGE_ID,
        #             token=Config.START_MESSAGE_IMAGE_TOKEN,
        #             url=Config.
        #         ),
        #         bot=bot
        #     )
        # )
        pass

    await bot.send_message(
        user_id=event.user.user_id,
        text=Texts.Messages.start,
        parse_mode=ParseMode.MARKDOWN,
        attachments=attachments,
    )
