from aiomax.types.updates import MessageCallbackUpdate
from aiomax.types import (
    InlineKeyboardAttachmentRequest,
    TextFormat,
    Keyboard,
    MessageButton,
    NewMessageBody,
    CallbackButton,
    ButtonIntent,
)
from aiomax.methods import AnswerCallback
from ...utils import Texts, UserState
from ...bot import bot, state_machine


async def add_name_solution(update: MessageCallbackUpdate):
    if update.callback.payload == "add_name":
        await bot(
            AnswerCallback(
                callback_id=update.callback.callback_id,
                message=NewMessageBody(
                    text=Texts.Messages.get_name,
                    format=TextFormat.MARKDOWN,
                    notify=True,
                    attachments=[
                        InlineKeyboardAttachmentRequest(
                            payload=Keyboard(
                                buttons=[
                                    [
                                        MessageButton(
                                            text=update.callback.user.first_name
                                        ),
                                    ]
                                ]
                            )
                        )
                    ],
                ),
            )
        )

        state_machine.set_state(update.callback.user.user_id, UserState.GET_NAME)

    elif update.callback.payload == "cancel":
        await bot(
            AnswerCallback(
                callback_id=update.callback.callback_id,
                message=NewMessageBody(
                    text=Texts.Messages.add_city_solution,
                    format=TextFormat.MARKDOWN,
                    notify=True,
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
                ),
            )
        )

        state_machine.set_state(
            update.callback.user.user_id, UserState.ADD_CITY_SOLUTION
        )
        state_machine.update_context(update.callback.user.user_id, name=None)


def add_name_solution_filter(update: MessageCallbackUpdate) -> bool:
    return (
        update.callback.payload in ("add_name", "cancel")
        and state_machine.get_state(update.callback.user.user_id)
        == UserState.ADD_NAME_SOLUTION
    )
