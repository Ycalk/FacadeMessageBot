from aiomax.types.updates import MessageCreatedUpdate
from aiomax.types import (
    InlineKeyboardAttachmentRequest,
    TextFormat,
    Keyboard,
    MessageButton,
)
from aiomax import Bot
from aiomax.methods import SendMessage
from bot.utils import Texts, UserState, Config
from bot.bot import state_machine, name_validator


async def get_message(update: MessageCreatedUpdate, bot: Bot) -> None:
    if not update.message or not update.message.sender:
        return
    if (
        not update.message.body.text
        or len(update.message.body.text) > Config.MAX_MESSAGE_LENGTH
        or len(update.message.body.text) < 1
    ):
        await bot(
            SendMessage(
                user_id=update.message.sender.user_id,
                text=Texts.Messages.invalid_message_text,
                text_format=TextFormat.MARKDOWN,
            )
        )
        return

    if await name_validator(update.message.sender.first_name):
        attachments = [
            InlineKeyboardAttachmentRequest(
                payload=Keyboard(
                    buttons=[
                        [
                            MessageButton(text=update.message.sender.first_name),
                        ]
                    ]
                )
            )
        ]
    else:
        attachments = []
    await bot(
        SendMessage(
            user_id=update.message.sender.user_id,
            text=Texts.Messages.get_name_with_name_from_profile
            if attachments
            else Texts.Messages.get_name,
            text_format=TextFormat.MARKDOWN,
            notify=True,
            attachments=attachments,
        ),
    )

    state_machine.set_state(update.message.sender.user_id, UserState.GET_NAME)


def get_message_filter(update: MessageCreatedUpdate) -> bool:
    if not update.message or not update.message.sender:
        return False
    return (
        state_machine.get_state(update.message.sender.user_id) == UserState.GET_MESSAGE
    )
