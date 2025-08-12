from aiomax.types.updates import MessageCreatedUpdate
from aiomax.types import TextFormat
from aiomax.methods import SendMessage
from aiomax import Bot
from bot.utils import Texts, UserState
from bot.bot import state_machine
from shared_models.database import User


async def create_command_handler(update: MessageCreatedUpdate, bot: Bot) -> None:
    if not update.message or not update.message.sender:
        return

    await bot(
        SendMessage(
            user_id=update.message.sender.user_id,
            text=Texts.Messages.get_message,
            text_format=TextFormat.MARKDOWN,
        )
    )
    await User.update_or_create(
        defaults={
            "first_name": update.message.sender.first_name,
            "last_name": update.message.sender.last_name,
            "username": update.message.sender.username,
        },
        max_id=update.message.sender.user_id,
    )

    state_machine.set_state(update.message.sender.user_id, UserState.GET_MESSAGE)


def create_command_filter(update: MessageCreatedUpdate) -> bool:
    return (
        update.message is not None
        and update.message.sender is not None
        and update.message.body.text is not None
        and update.message.body.text == "/create"
    )
