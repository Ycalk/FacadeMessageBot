from aiomax.types.updates import MessageCreatedUpdate
from aiomax.types import (
    InlineKeyboardAttachmentRequest,
    TextFormat,
    Keyboard,
    CallbackButton,
    ButtonIntent,
)
from aiomax import Bot
from aiomax.methods import SendMessage
from ...utils import Texts, UserState
from ...bot import state_machine


async def get_name(update: MessageCreatedUpdate, bot: Bot) -> None:
    if not update.message or not update.message.sender:
        return

    if not update.message.body.text or len(update.message.body.text) < 1:
        await bot(
            SendMessage(
                user_id=update.message.sender.user_id,
                text=Texts.Messages.invalid_name_text,
                text_format=TextFormat.MARKDOWN,
            )
        )
        return

    await bot(
        SendMessage(
            user_id=update.message.sender.user_id,
            text=Texts.Messages.add_city_solution,
            text_format=TextFormat.MARKDOWN,
            attachments=[
                InlineKeyboardAttachmentRequest(
                    payload=Keyboard(
                        buttons=[
                            [
                                CallbackButton(
                                    text="Да",
                                    payload="add_city",
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
            ],
        )
    )

    state_machine.set_state(update.message.sender.user_id, UserState.ADD_CITY_SOLUTION)
    state_machine.update_context(
        update.message.sender.user_id, name=update.message.body.text
    )


def get_name_filter(update: MessageCreatedUpdate) -> bool:
    if not update.message or not update.message.sender:
        return False
    return state_machine.get_state(update.message.sender.user_id) == UserState.GET_NAME
