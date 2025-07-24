from aiomax.types.updates import MessageCallbackUpdate
from aiomax.types import NewMessageBody
from aiomax.methods import AnswerCallback
from ..utils import Texts
from ..bot import bot


async def confirm_start(update: MessageCallbackUpdate):
    await bot(
        AnswerCallback(
            callback_id=update.callback.callback_id,
            message=NewMessageBody(
                text=Texts.Messages.confirm_start,
                attachments=[],
            ),  # type: ignore
        )
    )


def confirm_start_filter(update: MessageCallbackUpdate) -> bool:
    return update.callback.payload == "confirm_start"
