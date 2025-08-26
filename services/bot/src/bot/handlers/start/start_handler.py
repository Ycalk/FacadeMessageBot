from aiomax.types.updates import BotStartedUpdate
from aiomax.types.attachment_requests import (
    InlineKeyboardAttachmentRequest,
    ImageAttachmentRequest,
)
from aiomax.types import PhotoAttachmentRequestPayload, AttachmentRequest
from aiomax.types.keyboard import CallbackButton, Keyboard, LinkButton
from aiomax.types import TextFormat, ButtonIntent
from aiomax.methods import SendMessage
from aiomax import Bot
from bot.bot import state_machine
from bot.utils import Texts, UserState, Config


async def start_handler(update: BotStartedUpdate, bot: Bot) -> None:
    attachments: list[AttachmentRequest] = [
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
                            text=Texts.Buttons.send_message,
                            payload="send_message",
                            intent=ButtonIntent.POSITIVE,
                        )
                    ],
                ]
            )
        ),
    ]
    if Config.START_MESSAGE_IMAGE_TOKEN:
        attachments.append(
            ImageAttachmentRequest(
                payload=PhotoAttachmentRequestPayload(
                    url=None, photos=None, token=Config.START_MESSAGE_IMAGE_TOKEN
                )
            )
        )
    await bot(
        SendMessage(
            user_id=update.user.user_id,
            text=Texts.Messages.start,
            text_format=TextFormat.MARKDOWN,
            attachments=attachments,
        )
    )
    # Устанавливаем состояние пользователя на SEND_MESSAGE
    # Сначала реакция на кнопку "Отправить сообщение" ->
    # подтверждение условий использования (если пользователь новый) ->
    # Отправка сообщения о том, что сообщение пройдет модерацию ->
    # реакция на кнопку "Написать сообщение"
    await state_machine.set_state(update.user.user_id, UserState.SEND_MESSAGE)
