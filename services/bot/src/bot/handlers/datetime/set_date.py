from aiomax.types.updates import MessageCallbackUpdate
from aiomax.types import NewMessageBody, TextFormat
from aiomax.methods import AnswerCallback
from ...utils import Texts, UserState
from ...bot import bot, state_machine
from datetime import datetime


async def set_date(update: MessageCallbackUpdate):
    await bot(
        AnswerCallback(
            callback_id=update.callback.callback_id,
            message=NewMessageBody(
                text=Texts.Messages.choose_time,
                attachments=[],
                notify=True,
                format=TextFormat.MARKDOWN,
            ),
        )
    )
    state_machine.update_context(
        update.callback.user.user_id, date=update.callback.payload
    )
    state_machine.set_state(update.callback.user.user_id, UserState.SET_TIME)


def set_date_filter(update: MessageCallbackUpdate) -> bool:
    try:
        datetime.strptime(update.callback.payload, "%d.%m.%Y")  # type: ignore
        return (
            state_machine.get_state(update.callback.user.user_id) == UserState.SET_DATE
        )
    except ValueError:
        return False
