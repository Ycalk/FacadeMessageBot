from aiomax.types.updates import MessageCallbackUpdate
from aiomax.types import NewMessageBody, TextFormat
from aiomax.methods import AnswerCallback, SendMessage
from ..utils import Texts, UserState
from ..bot import bot, state_machine


async def confirm_start(update: MessageCallbackUpdate):
    await bot(
        AnswerCallback(
            callback_id=update.callback.callback_id,
            message=NewMessageBody(
                text=Texts.Messages.confirm_start,
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
    state_machine.set_state(update.callback.user.user_id, UserState.GET_MESSAGE)


def confirm_start_filter(update: MessageCallbackUpdate) -> bool:
    return (
        update.callback.payload == "confirm_start"
        and state_machine.get_state(update.callback.user.user_id)
        == UserState.CONFIRM_START
    )
