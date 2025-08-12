from aiomax.types.updates import MessageCallbackUpdate
from aiomax.types import (
    NewMessageBody,
    TextFormat,
    InlineKeyboardAttachmentRequest,
    Keyboard,
    CallbackButton,
    ButtonIntent,
)
from aiomax.methods import AnswerCallback, SendMessage
from aiomax import Bot
from bot.utils import Texts, UserState
from bot.bot import state_machine
from shared_models.database import Message, User
from shared_models.enums import MessageState
from bot.notification_processor.app import broker
from shared_models.messaging import (
    auto_moderator_queue,
    moderator_exchange,
    MessageInput,
)
from shared_models.messaging import Message as MessageSharedModel


async def confirm_fields(update: MessageCallbackUpdate, bot: Bot) -> None:
    if update.callback.payload == "start_over":
        # Пользователь хочет начать заново,
        # сбрасываем контекст и устанавливаем состояние на ввод сообщения
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
        user = await User.get_or_none(max_id=update.callback.user.user_id)
        message = state_machine.get_context(update.callback.user.user_id, "message")
        name = state_machine.get_context(update.callback.user.user_id, "name")
        city = state_machine.get_context(update.callback.user.user_id, "city")

        if not message or not name or not city or not user:
            # Если какое-то из полей пустое, отправляем сообщение об ошибке
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
                    text=Texts.Messages.confirm_fields.format(
                        message=message,
                        name=name,
                        city=city,
                    ),
                    attachments=[],
                    notify=True,
                    format=TextFormat.MARKDOWN,
                ),
            )
        )
        await bot(
            SendMessage(
                user_id=update.callback.user.user_id,
                text=Texts.Messages.start_moderation,
                attachments=[
                    InlineKeyboardAttachmentRequest(
                        payload=Keyboard(
                            buttons=[
                                [
                                    CallbackButton(
                                        text=Texts.Buttons.new_message,
                                        payload="new_message",
                                        intent=ButtonIntent.POSITIVE,
                                    )
                                ],
                            ],
                        )
                    )
                ],
            )
        )

        # Создаем новое сообщение с подтвержденными полями
        new_message = await Message.create(
            user=user,
            text=message,
            name=name,
            city=city,
            send_photo=True,
            state=MessageState.PENDING_AUTO_MODERATION,
        )

        # Отправляем новое сообщение в очередь авто-модерации
        await broker.publish(
            MessageInput(
                message=MessageSharedModel(
                    message_id=new_message.id,
                    text=new_message.text,
                    city=new_message.city,
                    name=new_message.name,
                    send_photo=new_message.send_photo,
                )
            ),
            auto_moderator_queue,
            moderator_exchange,
        )


def confirm_fields_filter(update: MessageCallbackUpdate) -> bool:
    return (
        update.callback.payload in ("confirm_fields", "start_over")
        and state_machine.get_state(update.callback.user.user_id)
        == UserState.CONFIRM_FIELDS
    )
