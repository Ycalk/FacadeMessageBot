from aiomax.types.updates import BotStartedUpdate
from aiomax.types.attachment_requests import InlineKeyboardAttachmentRequest
from aiomax.types.keyboard import CallbackButton, Keyboard
from aiomax.types import TextFormat, ButtonIntent
from aiomax.methods import SendMessage
from aiomax import Bot
from bot.bot import state_machine
from bot.utils import Texts, UserState
from shared_models.database import User


async def start_handler(update: BotStartedUpdate, bot: Bot) -> None:
    await bot(
        SendMessage(
            user_id=update.user.user_id,
            text=Texts.Messages.start,
            text_format=TextFormat.MARKDOWN,
        )
    )
    if User.get_or_none(max_id=update.user.user_id) is None:
        await bot(
            SendMessage(
                user_id=update.user.user_id,
                text=Texts.Messages.ask_confirm,
                text_format=TextFormat.MARKDOWN,
                attachments=[
                    InlineKeyboardAttachmentRequest(
                        payload=Keyboard(
                            buttons=[
                                [
                                    CallbackButton(
                                        text=Texts.Buttons.confirm_start,
                                        payload="confirm_start",
                                        intent=ButtonIntent.POSITIVE,
                                    )
                                ]
                            ]
                        )
                    )
                ],
            )
        )

        state_machine.set_state(update.user.user_id, UserState.CONFIRM_START)
