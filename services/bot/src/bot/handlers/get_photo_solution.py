from maxapi.types import MessageCallback
from shared_models.database import Message
from bot.utils import Texts


async def get_photo_solution(callback: MessageCallback) -> None:
    if not isinstance(callback.payload, str):
        return
    try:
        action, message_id = callback.payload.split(":", 1)
        message_id = int(message_id)
    except ValueError:
        return

    message = await Message.get_or_none(id=message_id).prefetch_related("user")
    if (
        not message
        or not message.show_time_start
        or not message.show_time_end
        or message.user.max_id != callback.from_user.user_id
    ):
        return

    if action == "accept_get_photo":
        message.send_photo = True
    elif action == "reject_get_photo":
        message.send_photo = False
    else:
        return

    await message.save()

    await callback.message.answer(
        text=Texts.Messages.confirm_send_photo
        if message.send_photo
        else Texts.Messages.reject_send_photo,
    )


def get_photo_solution_filter(callback: MessageCallback) -> bool:
    return isinstance(callback.payload, str) and (
        callback.payload.startswith("accept_get_photo")
        or callback.payload.startswith("reject_get_photo")
    )
