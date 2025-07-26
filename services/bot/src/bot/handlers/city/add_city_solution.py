from aiomax.types.updates import MessageCallbackUpdate
from aiomax.types import (
    InlineKeyboardAttachmentRequest,
    TextFormat,
    Keyboard,
    NewMessageBody,
    CallbackButton,
    ButtonIntent,
    RequestGeoLocationButton,
)
from aiomax.methods import AnswerCallback
from ...utils import Texts, UserState
from ...bot import bot, state_machine


async def add_city_solution(update: MessageCallbackUpdate):
    if update.callback.payload == "add_city":
        await bot(
            AnswerCallback(
                callback_id=update.callback.callback_id,
                message=NewMessageBody(
                    text=Texts.Messages.add_city,
                    format=TextFormat.MARKDOWN,
                    notify=True,
                    attachments=[
                        InlineKeyboardAttachmentRequest(
                            payload=Keyboard(
                                buttons=[
                                    [
                                        RequestGeoLocationButton(
                                            text="Определить автоматически", quick=False
                                        ),
                                    ]
                                ]
                            )
                        )
                    ],
                ),
            )
        )

        state_machine.set_state(update.callback.user.user_id, UserState.GET_CITY)

    elif update.callback.payload == "cancel":
        await bot(
            AnswerCallback(
                callback_id=update.callback.callback_id,
                message=NewMessageBody(
                    text=Texts.Messages.get_photo_solution,
                    format=TextFormat.MARKDOWN,
                    notify=True,
                    attachments=[
                        InlineKeyboardAttachmentRequest(
                            payload=Keyboard(
                                buttons=[
                                    [
                                        CallbackButton(
                                            text="Да",
                                            payload="get_photo",
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
            update.callback.user.user_id, UserState.GET_PHOTO_SOLUTION
        )
        state_machine.update_context(update.callback.user.user_id, city=None)


def add_city_solution_filter(update: MessageCallbackUpdate) -> bool:
    return (
        update.callback.payload in ("add_city", "cancel")
        and state_machine.get_state(update.callback.user.user_id)
        == UserState.ADD_CITY_SOLUTION
    )
