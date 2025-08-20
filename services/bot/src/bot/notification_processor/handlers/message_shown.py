import base64
from logging import Logger
from faststream.rabbit import RabbitRouter
from shared_models.messaging import (
    bot_message_shown_queue,
    bot_exchange,
    MessageShown,
)
from aiomax import Bot
from aiomax.types import (
    PhotoAttachmentRequestPayload,
    ImageAttachmentRequest,
    AttachmentRequest,
    InputFile,
    UploadType,
    TextFormat,
)
from faststream import Context
from shared_models.enums import MessageState
from aiomax.methods import SendMessage
from shared_models.database import Message
from bot.utils import Texts


message_shown_router = RabbitRouter()


async def send_user_message(
    bot: Bot,
    user_id: int,
    text: str,
    attachments: list[AttachmentRequest] | None = None,
):
    """Отправка сообщения пользователю."""
    await bot(
        SendMessage(
            user_id=user_id,
            text=text,
            text_format=TextFormat.MARKDOWN,
            attachments=attachments,
        )
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

    if message_shown.photo_base64 and message.send_photo:
        photo = InputFile(
            data=base64.b64decode(message_shown.photo_base64),
            filename="Фото на память.jpg",
            upload_type=UploadType.IMAGE,
        )
        token = await bot.upload(photo)
        await send_user_message(
            bot,
            message.user.max_id,
            Texts.Messages.photo_sent,
            attachments=[
                ImageAttachmentRequest(
                    payload=PhotoAttachmentRequestPayload(
                        url=None, token=token, photos=None
                    )
                )
            ],
        )
    else:
        await send_user_message(
            bot, message.user.max_id, Texts.Messages.photo_sent_without_picture
        )
