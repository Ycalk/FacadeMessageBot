from aiomax.types.updates import MessageCreatedUpdate
from aiomax.types import (
    InlineKeyboardAttachmentRequest,
    TextFormat,
    Keyboard,
    CallbackButton,
    ButtonIntent,
)
from aiomax.methods import SendMessage
from ..utils import Texts, UserState, Config
from ..bot import bot, state_machine


async def get_message(update: MessageCreatedUpdate):
    if (
        not update.message.body.text
        or len(update.message.body.text) > Config.MAX_MESSAGE_LENGTH
    ):
        await bot(
            SendMessage(
                user_id=update.message.sender.user_id,  # type: ignore
                text=Texts.Messages.invalid_message_text,
                text_format=TextFormat.MARKDOWN,
            )
        )
    attachments = [
        InlineKeyboardAttachmentRequest(
            payload=Keyboard(
                buttons=[
                    [
                        CallbackButton(
                            text="Да",
                            payload="add_name",
                            intent=ButtonIntent.POSITIVE,
                        ),
                        CallbackButton(
                            text="Нет",
                            payload="cancel",
                            intent=ButtonIntent.NEGATIVE,
                        ),
                    ]
                ]
            )
        )
    ]

    await bot(
        SendMessage(
            user_id=update.message.sender.user_id,  # type: ignore
            text=Texts.Messages.add_name,
            text_format=TextFormat.MARKDOWN,
            attachments=attachments,
        )
    )
    state_machine.set_state(update.message.sender.user_id, UserState.ADD_NAME_SOLUTION)  # type: ignore


def get_message_filter(update: MessageCreatedUpdate) -> bool:
    return (
        state_machine.get_state(update.message.sender.user_id) == UserState.GET_MESSAGE  # type: ignore
    )
