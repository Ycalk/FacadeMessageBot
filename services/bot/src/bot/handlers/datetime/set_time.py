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
from datetime import datetime


def get_time(time_str: str) -> str | None:
    formats = [
        "%H:%M",
        "%H.%M",
        "%H-%M",
        "%H %M",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(time_str.strip(), fmt).strftime("%H:%M")
        except ValueError:
            continue
    return None


async def set_time(update: MessageCreatedUpdate, bot: Bot) -> None:
    if not update.message or not update.message.sender:
        return
    time = get_time(update.message.body.text) if update.message.body.text else None
    if not time:
        await bot(
            SendMessage(
                user_id=update.message.sender.user_id,
                text=Texts.Messages.invalid_time_format,
                text_format=TextFormat.MARKDOWN,
            )
        )
        return
    else:
        message = state_machine.get_context(update.message.sender.user_id, "message")
        date = state_machine.get_context(update.message.sender.user_id, "date")
        get_photo = state_machine.get_context(
            update.message.sender.user_id, "get_photo"
        )
        if not message or not date or not time or (get_photo is None):
            await bot(
                SendMessage(
                    user_id=update.message.sender.user_id,
                    text=Texts.Messages.missing_fields,
                    text_format=TextFormat.MARKDOWN,
                    attachments=[],
                )
            )
            return
        await bot(
            SendMessage(
                user_id=update.message.sender.user_id,
                text=Texts.Messages.confirm_fields.format(
                    message=message,
                    name=state_machine.get_context(
                        update.message.sender.user_id, "name"
                    )
                    or "",
                    city=state_machine.get_context(
                        update.message.sender.user_id, "city"
                    )
                    or "",
                    get_photo="Да" if get_photo else "Нет",
                    date=date,
                    time=time,
                ),
                text_format=TextFormat.MARKDOWN,
                attachments=[
                    InlineKeyboardAttachmentRequest(
                        payload=Keyboard(
                            buttons=[
                                [
                                    CallbackButton(
                                        text="Подтвердить",
                                        payload="confirm_fields",
                                        intent=ButtonIntent.POSITIVE,
                                    ),
                                    CallbackButton(
                                        text="Начать заново",
                                        payload="start_over",
                                        intent=ButtonIntent.DEFAULT,
                                    ),
                                ]
                            ]
                        )
                    )
                ],
            )
        )
        state_machine.set_state(update.message.sender.user_id, UserState.CONFIRM_FIELDS)
        state_machine.update_context(update.message.sender.user_id, time=time)


def set_time_filter(update: MessageCreatedUpdate) -> bool:
    if not update.message or not update.message.sender:
        return False
    return state_machine.get_state(update.message.sender.user_id) == UserState.SET_TIME
