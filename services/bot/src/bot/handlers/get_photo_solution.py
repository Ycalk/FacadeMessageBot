from aiomax.types.updates import MessageCallbackUpdate
from aiomax.types import (
    TextFormat,
    NewMessageBody,
)
from aiomax import Bot
from aiomax.methods import AnswerCallback, SendMessage
from shared_models.database import Message
from bot.utils import Texts


async def get_photo_solution(update: MessageCallbackUpdate, bot: Bot) -> None:
    if not isinstance(update.callback.payload, str):
        return
    try:
        action, message_id = update.callback.payload.split(":", 1)
        message_id = int(message_id)
    except ValueError:
        return

    message = await Message.get_or_none(id=message_id).prefetch_related("user")
    if (
        not message
        or not message.show_time_start
        or not message.show_time_end
        or message.user.max_id != update.callback.user.user_id
    ):
        return

    if action == "accept_get_photo":
        message.send_photo = True
    elif action == "reject_get_photo":
        message.send_photo = False
    else:
        return

    await message.save()

    await bot(
        AnswerCallback(
            callback_id=update.callback.callback_id,
            message=NewMessageBody(
                text=None,
                format=TextFormat.MARKDOWN,
                notify=True,
                attachments=[],
            ),
        )
    )
    await bot(
        SendMessage(
            user_id=update.callback.user.user_id,
            text=Texts.Messages.confirm_send_photo
            if message.send_photo
            else Texts.Messages.reject_send_photo,
        )
    )


def get_photo_solution_filter(update: MessageCallbackUpdate) -> bool:
    return isinstance(update.callback.payload, str) and (
        update.callback.payload.startswith("accept_get_photo")
        or update.callback.payload.startswith("reject_get_photo")
    )
