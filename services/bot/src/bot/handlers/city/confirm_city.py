from aiomax.types.updates import MessageCallbackUpdate
from aiomax import Bot
from aiomax.types import (
    NewMessageBody,
    TextFormat,
    InlineKeyboardAttachmentRequest,
    Keyboard,
    CallbackButton,
    ButtonIntent,
    LinkButton,
)
from aiomax.methods import AnswerCallback
from bot.utils import Texts, UserState, Config
from bot.bot import state_machine


async def confirm_city(update: MessageCallbackUpdate, bot: Bot) -> None:
    if update.callback.payload == "confirm_city":
        # Проверяем, что все необходимые поля заполнены
        message = await state_machine.get_context(
            update.callback.user.user_id, "message"
        )
        name = await state_machine.get_context(update.callback.user.user_id, "name")
        city = await state_machine.get_context(update.callback.user.user_id, "city")

        # Если какое-то из полей пустое, отправляем сообщение об ошибке
        if not message or not name or not city:
            await bot(
                AnswerCallback(
                    callback_id=update.callback.callback_id,
                    message=NewMessageBody(
                        text=Texts.Messages.missing_fields,
                        format=TextFormat.MARKDOWN,
                        notify=True,
                        attachments=[],
                    ),
                )
            )
            return
        await bot(
            # Отправляем сообщение с подтверждением полей
            AnswerCallback(
                callback_id=update.callback.callback_id,
                message=NewMessageBody(
                    text=Texts.Messages.confirm_fields_with_instruction.format(
                        message=message,
                        name=name,
                        city=city,
                    ),
                    format=TextFormat.MARKDOWN,
                    notify=True,
                    attachments=[
                        InlineKeyboardAttachmentRequest(
                            payload=Keyboard(
                                buttons=[
                                    [
                                        LinkButton(
                                            text=Texts.Buttons.processing_of_personal_data,
                                            url=Config.PROCESSING_OF_PERSONAL_DATA_URL,
                                        )
                                    ],
                                    [
                                        CallbackButton(
                                            text=Texts.Buttons.confirm_fields,
                                            payload="confirm_fields",
                                            intent=ButtonIntent.POSITIVE,
                                        ),
                                        CallbackButton(
                                            text=Texts.Buttons.start_over,
                                            payload="start_over",
                                            intent=ButtonIntent.DEFAULT,
                                        ),
                                    ],
                                ]
                            )
                        )
                    ],
                ),
            )
        )

        await state_machine.set_state(
            update.callback.user.user_id, UserState.CONFIRM_FIELDS
        )

    elif update.callback.payload == "try_again_city":
        # Пользователь хочет ввести город заново
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

        await state_machine.set_state(update.callback.user.user_id, UserState.GET_CITY)


async def confirm_city_filter(update: MessageCallbackUpdate) -> bool:
    current_state = await state_machine.get_state(update.callback.user.user_id)
    return (
        update.callback.payload in ("confirm_city", "try_again_city")
        and current_state in (UserState.CONFIRM_CITY, UserState.SELECT_CITY)
    )
