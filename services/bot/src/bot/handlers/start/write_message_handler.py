from aiomax.types.updates import MessageCallbackUpdate
from aiomax.types import TextFormat, NewMessageBody
from aiomax.methods import AnswerCallback, SendMessage
from aiomax import Bot
from bot.bot import state_machine
from bot.utils import Texts, UserState


async def write_message_handler(update: MessageCallbackUpdate, bot: Bot) -> None:
    await bot(
        AnswerCallback(
            callback_id=update.callback.callback_id,
            message=NewMessageBody(
                notify=True,
                text=Texts.Messages.write_message,
                format=TextFormat.MARKDOWN,
                attachments=[],
            ),
        )
    )
    await bot(
        SendMessage(
            user_id=update.callback.user.user_id,
            text=Texts.Messages.get_message,
        )
    )
    state_machine.set_state(update.callback.user.user_id, UserState.GET_MESSAGE)


def write_message_filter(update: MessageCallbackUpdate) -> bool:
    return (
        update.callback.payload == "write_message"
        and state_machine.get_state(update.callback.user.user_id)
        == UserState.WRITE_MESSAGE
    )
