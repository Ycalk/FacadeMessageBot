from aiomax.types.updates import MessageCallbackUpdate
from aiomax.types import (
    InlineKeyboardAttachmentRequest,
    TextFormat,
    Keyboard,
    NewMessageBody,
    CallbackButton,
    ButtonIntent,
)
from aiomax import Bot
from aiomax.methods import AnswerCallback, SendMessage
from bot.utils import Texts, UserState
from bot.bot import state_machine


async def get_photo_solution(update: MessageCallbackUpdate, bot: Bot) -> None:
    get_photo = update.callback.payload == "get_photo"
    message = state_machine.get_context(update.callback.user.user_id, "message")
    if not message:
        await bot(
            SendMessage(
                user_id=update.callback.user.user_id,
                text=Texts.Messages.missing_fields,
                text_format=TextFormat.MARKDOWN,
                attachments=[],
            )
        )
        return

    await bot(
        AnswerCallback(
            callback_id=update.callback.callback_id,
            message=NewMessageBody(
                text=Texts.Messages.confirm_fields_with_instruction.format(
                    message=message,
                    name=state_machine.get_context(update.callback.user.user_id, "name")
                    or "",
                    city=state_machine.get_context(update.callback.user.user_id, "city")
                    or "",
                    get_photo="Да" if get_photo else "Нет",
                ),
                format=TextFormat.MARKDOWN,
                notify=True,
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
            ),
        )
    )

    state_machine.set_state(update.callback.user.user_id, UserState.CONFIRM_FIELDS)
    state_machine.update_context(update.callback.user.user_id, get_photo=get_photo)


def get_photo_solution_filter(update: MessageCallbackUpdate) -> bool:
    return (
        update.callback.payload in ("get_photo", "cancel")
        and state_machine.get_state(update.callback.user.user_id)
        == UserState.GET_PHOTO_SOLUTION
    )
