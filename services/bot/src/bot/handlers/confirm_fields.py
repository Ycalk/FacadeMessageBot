from aiomax.types.updates import MessageCallbackUpdate
from aiomax.types import NewMessageBody, TextFormat
from aiomax.methods import AnswerCallback
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
        get_photo = state_machine.get_context(update.callback.user.user_id, "get_photo")
        name = state_machine.get_context(update.callback.user.user_id, "name")
        city = state_machine.get_context(update.callback.user.user_id, "city")

        if not message or (get_photo is None) or not user:
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
                        name=name or "",
                        city=city or "",
                        get_photo="Да" if get_photo else "Нет",
                    ),
                    attachments=[],
                    notify=True,
                    format=TextFormat.MARKDOWN,
                ),
            )
        )
        new_message = await Message.create(
            user=user,
            text=message,
            name=name,
            city=city,
            send_photo=get_photo,
            state=MessageState.PENDING_AUTO_MODERATION,
        )

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
