import base64
from logging import Logger
from faststream.rabbit import RabbitRouter
from shared_models.messaging import (
    bot_message_shown_queue,
    bot_exchange,
    MessageShown,
)
from maxapi import Bot
from maxapi.types.attachments.buttons import CallbackButton
from maxapi.types.input_media import InputMediaBuffer
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.enums.parse_mode import ParseMode
from maxapi.enums.upload_type import UploadType

from faststream import Context
from shared_models.enums import MessageState
from shared_models.database import Message
from bot.utils import Texts


message_shown_router = RabbitRouter()


async def send_user_message(
    bot: Bot,
    user_id: int,
    text: str,
    attachments=None,
):
    """Отправка сообщения пользователю."""
    await bot.send_message(
        user_id=user_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        attachments=attachments or [],
    )


@message_shown_router.subscriber(bot_message_shown_queue, bot_exchange)
async def moderation_result_handler(
    message_shown: MessageShown,
    logger: Logger = Context(),
    bot: Bot = Context(),
) -> None:
    message = await Message.get_or_none(
        id=message_shown.message.message_id
    ).prefetch_related("user")

    if not message:
        logger.warning(f"Message with ID {message_shown.message.message_id} not found.")
        return

    message.state = MessageState.SHOWN
    await message.save()

    if message_shown.photo_base64 and message.send_photo and False:
        # Загружаем фото 
        photo_data = base64.b64decode(message_shown.photo_base64)
        photo_media = InputMediaBuffer(
            buffer=photo_data,
            filename="Фото на память.jpg"
        )
        
        # Создаем клавиатуру
        keyboard = InlineKeyboardBuilder()
        keyboard.add(
            CallbackButton(
                text=Texts.Buttons.new_message,
                payload="new_message_no_edit",
            )
        )
        
        await send_user_message(
            bot,
            message.user.max_id,
            Texts.Messages.photo_sent,
            attachments=[photo_media, keyboard.as_markup()],
        )
    else:
        await send_user_message(
            bot, message.user.max_id, Texts.Messages.photo_sent_without_picture
        )
