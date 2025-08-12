from aiomax.types.updates import MessageCallbackUpdate
from aiomax.types import NewMessageBody, TextFormat
from aiomax.methods import AnswerCallback
from aiomax.types.attachment_requests import InlineKeyboardAttachmentRequest
from aiomax.types.keyboard import CallbackButton, Keyboard
from aiomax.types import ButtonIntent
from ...utils import Texts, UserState
from aiomax import Bot
from shared_models.database import User
from bot.bot import state_machine


async def confirm_terms_of_use(update: MessageCallbackUpdate, bot: Bot) -> None:
    await bot(
        AnswerCallback(
            callback_id=update.callback.callback_id,
            message=NewMessageBody(
                notify=True,
                text=Texts.Messages.write_message,
                format=TextFormat.MARKDOWN,
                attachments=[
                    InlineKeyboardAttachmentRequest(
                        payload=Keyboard(
                            buttons=[
                                [
                                    CallbackButton(
                                        text=Texts.Buttons.write_message,
                                        payload="write_message",
                                        intent=ButtonIntent.POSITIVE,
                                    )
                                ],
                            ]
                        )
                    )
                ],
            ),
        )
    )

    state_machine.set_state(update.callback.user.user_id, UserState.WRITE_MESSAGE)
    await User.update_or_create(
        defaults={
            "first_name": update.callback.user.first_name,
            "last_name": update.callback.user.last_name,
            "username": update.callback.user.username,
        },
        max_id=update.callback.user.user_id,
    )

    state_machine.set_state(update.callback.user.user_id, UserState.WRITE_MESSAGE)


def confirm_terms_of_use_filter(update: MessageCallbackUpdate) -> bool:
    return (
        update.callback.payload == "confirm_terms_of_use"
        and state_machine.get_state(update.callback.user.user_id)
        == UserState.CONFIRM_TERMS_OF_USE
    )
