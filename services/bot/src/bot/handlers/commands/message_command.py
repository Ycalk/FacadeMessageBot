from aiomax.types.updates import MessageCreatedUpdate
from aiomax.types import TextFormat
from aiomax.methods import SendMessage
from aiomax import Bot
from bot.utils import Texts
from shared_models.database import Message, User


async def message_command_handler(update: MessageCreatedUpdate, bot: Bot) -> None:
    if not update.message or not update.message.sender:
        return

    user = await User.get_or_none(max_id=update.message.sender.user_id)

    messages = (
        (await Message.filter(user_id=user.id).order_by("-created_at").all())
        if user is not None
        else []
    )

    if len(messages) == 0:
        await bot(
            SendMessage(
                user_id=update.message.sender.user_id,
                text=Texts.Messages.no_messages,
                text_format=TextFormat.MARKDOWN,
            )
        )
        return
    for message in messages:
        await bot(
            SendMessage(
                user_id=update.message.sender.user_id,
                text=Texts.Messages.fields.format(
                    message=message.text,
                    name=message.name or "",
                    city=message.city or "",
                    get_photo="Да" if message.send_photo else "Нет",
                    date=message.show_at.strftime("%d.%m.%Y")
                    if message.show_at is not None
                    else "",
                    time=message.show_at.strftime("%H:%M")
                    if message.show_at is not None
                    else "",
                    status=str(message.state),
                ),
                text_format=TextFormat.MARKDOWN,
            )
        )


def message_command_filter(update: MessageCreatedUpdate) -> bool:
    return (
        update.message is not None
        and update.message.sender is not None
        and update.message.body.text is not None
        and update.message.body.text == "/messages"
    )
