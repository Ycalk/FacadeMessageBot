from aiomax.types.updates import MessageCallbackUpdate
from aiomax.types.attachment_requests import InlineKeyboardAttachmentRequest
from aiomax.types.keyboard import CallbackButton, Keyboard, LinkButton
from aiomax.types import TextFormat, ButtonIntent, NewMessageBody
from aiomax.methods import AnswerCallback
from aiomax import Bot
from bot.bot import state_machine
from bot.utils import Texts, UserState, Config
from shared_models.database import User


async def send_message_handler(update: MessageCallbackUpdate, bot: Bot) -> None:
    if await User.get_or_none(max_id=update.callback.user.user_id) is None:
        await bot(
            AnswerCallback(
                callback_id=update.callback.callback_id,
                message=NewMessageBody(
                    notify=True,
                    text=Texts.Messages.ask_confirm,
                    format=TextFormat.MARKDOWN,
                    attachments=[
                        InlineKeyboardAttachmentRequest(
                            payload=Keyboard(
                                buttons=[
                                    [
                                        LinkButton(
                                            text=Texts.Buttons.terms_of_use,
                                            url=Config.TERMS_OF_USE_URL,
                                        )
                                    ],
                                    [
                                        CallbackButton(
                                            text=Texts.Buttons.confirm_terms_of_use,
                                            payload="confirm_terms_of_use",
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

        state_machine.set_state(
            update.callback.user.user_id, UserState.CONFIRM_TERMS_OF_USE
        )
    else:
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


def send_message_filter(update: MessageCallbackUpdate) -> bool:
    return (
        update.callback.payload == "send_message"
        and state_machine.get_state(update.callback.user.user_id)
        == UserState.SEND_MESSAGE
    )
