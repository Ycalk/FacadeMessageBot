from aiomax.types.updates import MessageCallbackUpdate
from aiomax import Bot
from aiomax.types import (
    NewMessageBody,
    TextFormat,
    InlineKeyboardAttachmentRequest,
    Keyboard,
    CallbackButton,
    ButtonIntent,
    RequestGeoLocationButton,
    LinkButton,
)
from aiomax.methods import AnswerCallback
from bot.utils import Texts, UserState, Config
from bot.bot import state_machine


async def confirm_city(update: MessageCallbackUpdate, bot: Bot) -> None:
    if update.callback.payload == "confirm_city":
        # Проверяем, что все необходимые поля заполнены
        message = state_machine.get_context(update.callback.user.user_id, "message")
        name = state_machine.get_context(update.callback.user.user_id, "name")
        city = state_machine.get_context(update.callback.user.user_id, "city")

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

        state_machine.set_state(update.callback.user.user_id, UserState.CONFIRM_FIELDS)

    elif update.callback.payload == "try_again_city":
        # Пользователь ввел город вручную, но захотел попробовать определить снова
        await bot(
            AnswerCallback(
                callback_id=update.callback.callback_id,
                message=NewMessageBody(
                    text=Texts.Messages.add_city,
                    format=TextFormat.MARKDOWN,
                    notify=True,
                    attachments=[
                        InlineKeyboardAttachmentRequest(
                            payload=Keyboard(
                                buttons=[
                                    [
                                        RequestGeoLocationButton(
                                            text="Определить автоматически", quick=False
                                        ),
                                    ]
                                ]
                            )
                        )
                    ],
                ),
            )
        )

        state_machine.set_state(update.callback.user.user_id, UserState.GET_CITY)

    elif update.callback.payload == "write_city":
        # Город определился автоматически, но пользователь хочет ввести его вручную
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

        state_machine.set_state(update.callback.user.user_id, UserState.GET_CITY)


def confirm_city_filter(update: MessageCallbackUpdate) -> bool:
    return (
        update.callback.payload in ("confirm_city", "write_city", "try_again_city")
        and state_machine.get_state(update.callback.user.user_id)
        == UserState.CONFIRM_CITY
    )
