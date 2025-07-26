from aiomax.types.updates import MessageCallbackUpdate
from aiomax.types import NewMessageBody, TextFormat
from aiomax.methods import AnswerCallback
from ..utils import Texts, UserState
from ..bot import bot, state_machine


async def confirm_fields(update: MessageCallbackUpdate):
    if update.callback.payload == "start_over":
        await bot(
            AnswerCallback(
                callback_id=update.callback.callback_id,
                message=NewMessageBody(
                    text=Texts.Messages.get_message,
                    attachments=[],
                    notify=True,
                    format=TextFormat.MARKDOWN,
                ),
            )
        )
        state_machine.set_state(update.callback.user.user_id, UserState.GET_MESSAGE)
        state_machine.clear_context(update.callback.user.user_id)

    elif update.callback.payload == "confirm_fields":
        message = state_machine.get_context(update.callback.user.user_id, "message")
        date = state_machine.get_context(update.callback.user.user_id, "date")
        time = state_machine.get_context(update.callback.user.user_id, "time")
        get_photo = state_machine.get_context(update.callback.user.user_id, "get_photo")

        if not message or not date or not time or (get_photo is None):
            await bot(
                AnswerCallback(
                    callback_id=update.callback.callback_id,
                    message=NewMessageBody(
                        text=Texts.Messages.missing_fields,
                        attachments=[],
                        notify=True,
                        format=TextFormat.MARKDOWN,
                    ),
                )
            )
            return
        await bot(
            AnswerCallback(
                callback_id=update.callback.callback_id,
                message=NewMessageBody(
                    text=Texts.Messages.fields.format(
                        message=message,
                        name=state_machine.get_context(
                            update.callback.user.user_id, "name"
                        )
                        or "",
                        city=state_machine.get_context(
                            update.callback.user.user_id, "city"
                        )
                        or "",
                        get_photo="Да" if get_photo else "Нет",
                        date=date,
                        time=time,
                    ),
                    attachments=[],
                    notify=True,
                    format=TextFormat.MARKDOWN,
                ),
            )
        )


def confirm_fields_filter(update: MessageCallbackUpdate) -> bool:
    return (
        update.callback.payload in ("confirm_fields", "start_over")
        and state_machine.get_state(update.callback.user.user_id)
        == UserState.CONFIRM_FIELDS
    )
