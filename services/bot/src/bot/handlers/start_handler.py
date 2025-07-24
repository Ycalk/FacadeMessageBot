from aiomax.types.updates import BotStartedUpdate
from aiomax.types.attachment_requests import InlineKeyboardAttachmentRequest
from aiomax.types.keyboard import CallbackButton, Keyboard
from aiomax.types import TextFormat, ButtonIntent
from aiomax.methods import SendMessage
from ..bot import bot
from ..utils import Texts


async def start_handler(update: BotStartedUpdate):
    attachments = [
        InlineKeyboardAttachmentRequest(
            payload=Keyboard(
                buttons=[
                    [
                        CallbackButton(
                            text="Подтвердить",
                            payload="confirm_start",
                            intent=ButtonIntent.POSITIVE,
                        )
                    ]
                ]
            )
        )
    ]

    await bot(
        SendMessage(
            user_id=update.user.user_id,
            text=Texts.Messages.start,
            text_format=TextFormat.MARKDOWN,
        )
    )

    await bot(
        SendMessage(
            user_id=update.user.user_id,
            text=Texts.Messages.ask_confirm,
            text_format=TextFormat.MARKDOWN,
            attachments=attachments,
        )
    )
