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
    attachments.append(
             Attachment(
                 type=AttachmentType.IMAGE,
                 payload=PhotoAttachmentPayload(
                     photo_id="vhxt8mbo7Nr/ZML0L9lARPhHOktooq/sCrktUyfo4uv2VSDDiELO0A==",
                     token="wV1K6tUTXXXPjdIVQi/6KGBn/6eYNRSOYDYiaNRTfeNWTYtNA34JOvAm6CN7Q3rQ19c4zENQuxBY/wfv1GPkLo1rI5n6SKYnKQ5cHRY+tZlJOizFUClP9dM+EGdxeIPdzHvGxkonaQm6SHQI9/ZVzXSlqUNEBgYNb7dSOFjHZ+W4/cnONAlU4Q==",
                     url=""
                 ),
                 bot=bot
             )
         )
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
        user_id=event.user.user_id if hasattr(event, 'user') else event.message.sender.user_id,
        text=Texts.Messages.start,
        parse_mode=ParseMode.MARKDOWN,
        attachments=attachments,
    )
