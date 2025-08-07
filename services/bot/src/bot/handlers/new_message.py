from aiomax.types.updates import MessageCallbackUpdate
from aiomax.types import NewMessageBody, TextFormat
from aiomax.methods import AnswerCallback, SendMessage
from ..utils import Texts, UserState
from aiomax import Bot
from shared_models.database import User
from bot.bot import state_machine


async def new_message(update: MessageCallbackUpdate, bot: Bot) -> None:
    await bot(
        AnswerCallback(
            callback_id=update.callback.callback_id,
            message=NewMessageBody(
                text=None,
                attachments=[],
                notify=True,
                format=TextFormat.MARKDOWN,
            ),
        )
    )
    await bot(
        SendMessage(
            user_id=update.callback.user.user_id,
            text=Texts.Messages.get_message,
            text_format=TextFormat.MARKDOWN,
        )
    )
    await User.update_or_create(
        defaults={
            "first_name": update.callback.user.first_name,
            "last_name": update.callback.user.last_name,
            "username": update.callback.user.username,
        },
        max_id=update.callback.user.user_id,
    )

    state_machine.set_state(update.callback.user.user_id, UserState.GET_MESSAGE)


def new_message_filter(update: MessageCallbackUpdate) -> bool:
    return update.callback.payload == "new_message"
