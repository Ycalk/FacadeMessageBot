from aiomax.types.updates import MessageCallbackUpdate
from aiomax.types import (
    InlineKeyboardAttachmentRequest,
    TextFormat,
    Keyboard,
    NewMessageBody,
    CallbackButton,
    ButtonIntent,
)
from aiomax.methods import AnswerCallback, SendMessage
from ..utils import Texts, UserState
from ..bot import bot, state_machine


def get_date_attachment() -> InlineKeyboardAttachmentRequest:
    return InlineKeyboardAttachmentRequest(
        payload=Keyboard(
            buttons=[
                [
                    CallbackButton(
                        text="30 августа",
                        payload="30.08.2025",
                        intent=ButtonIntent.DEFAULT,
                    )
                ],
                [
                    CallbackButton(
                        text="31 августа",
                        payload="31.08.2025",
                        intent=ButtonIntent.DEFAULT,
                    )
                ],
            ]
        )
    )


async def get_photo_solution(update: MessageCallbackUpdate):
    if update.callback.payload == "get_photo":
        await bot(
            AnswerCallback(
                callback_id=update.callback.callback_id,
                message=NewMessageBody(
                    text=Texts.Messages.get_photo_confirm,
                    format=TextFormat.MARKDOWN,
                    notify=True,
                    attachments=[],
                ),
            )
        )
        await bot(
            SendMessage(
                user_id=update.callback.user.user_id,
                text=Texts.Messages.choose_date,
                attachments=[get_date_attachment()],
            )
        )
        state_machine.update_context(update.callback.user.user_id, get_photo=True)
        state_machine.set_state(update.callback.user.user_id, UserState.SET_DATE)

    elif update.callback.payload == "cancel":
        await bot(
            AnswerCallback(
                callback_id=update.callback.callback_id,
                message=NewMessageBody(
                    text=Texts.Messages.get_photo_cancel,
                    format=TextFormat.MARKDOWN,
                    notify=True,
                    attachments=[],
                ),
            )
        )

        await bot(
            SendMessage(
                user_id=update.callback.user.user_id,
                text=Texts.Messages.choose_date,
                attachments=[get_date_attachment()],
            )
        )
        state_machine.update_context(update.callback.user.user_id, get_photo=False)
        state_machine.set_state(update.callback.user.user_id, UserState.SET_DATE)


def get_photo_solution_filter(update: MessageCallbackUpdate) -> bool:
    return (
        update.callback.payload in ("get_photo", "cancel")
        and state_machine.get_state(update.callback.user.user_id)
        == UserState.GET_PHOTO_SOLUTION
    )
