from aiomax.types.updates import MessageCallbackUpdate
from aiomax import Bot
from aiomax.types import (
    NewMessageBody,
    TextFormat,
    InlineKeyboardAttachmentRequest,
    Keyboard,
    CallbackButton,
    ButtonIntent,
    RequestGeoLocationButton,
)
from aiomax.methods import AnswerCallback
from ...utils import Texts, UserState
from ...bot import state_machine


async def confirm_city(update: MessageCallbackUpdate, bot: Bot) -> None:
    if update.callback.payload == "confirm_city":
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

    elif update.callback.payload == "try_again_city":
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

    elif update.callback.payload == "write_city":
        await bot(
            AnswerCallback(
                callback_id=update.callback.callback_id,
                message=NewMessageBody(
                    text=Texts.Messages.add_city_without_geo,
                    format=TextFormat.MARKDOWN,
                    notify=True,
                    attachments=[],
                ),
            )
        )

        state_machine.set_state(update.callback.user.user_id, UserState.GET_CITY)


def confirm_city_filter(update: MessageCallbackUpdate) -> bool:
    return (
        update.callback.payload in ("confirm_city", "write_city", "try_again_city")
        and state_machine.get_state(update.callback.user.user_id)
        == UserState.CONFIRM_CITY
    )
