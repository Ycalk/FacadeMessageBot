from aiomax.types.updates import MessageCallbackUpdate
from aiomax.types.attachment_requests import InlineKeyboardAttachmentRequest
from aiomax.types.keyboard import CallbackButton, Keyboard, LinkButton
from aiomax.types import TextFormat, ButtonIntent, NewMessageBody
from aiomax.methods import AnswerCallback
from aiomax import Bot
from bot.bot import state_machine
from bot.utils import (
    Texts, 
    UserState, 
    Config,
    attempts_limit_reached,
    messages_limit_reached,
    messages_time_out_reached,
)
from shared_models.database import User


async def send_message_handler(update: MessageCallbackUpdate, bot: Bot) -> None:
    # Создаем пользователя если он новый
    await User.update_or_create(
        defaults={
            "first_name": update.callback.user.first_name,
            "last_name": update.callback.user.last_name,
            "username": update.callback.user.username,
        },
        max_id=update.callback.user.user_id,
    )
    
    # Проверяем глобальную блокировку сбора сообщений
    if Config.MESSAGE_COLLECTION_STOPPED:
        await bot(
            AnswerCallback(
                callback_id=update.callback.callback_id,
                message=NewMessageBody(
                    text=Texts.Messages.message_collection_stopped,
                    format=TextFormat.MARKDOWN,
                    notify=True,
                    attachments=[],
                ),
            )
        )
        return

    # Проверяем лимиты пользователя
    if await attempts_limit_reached(update.callback.user.user_id):
        await bot(
            AnswerCallback(
                callback_id=update.callback.callback_id,
                message=NewMessageBody(
                    text=Texts.Messages.attempts_limit,
                    format=TextFormat.MARKDOWN,
                    notify=True,
                    attachments=[],
                ),
            )
        )
        return
        
    if await messages_limit_reached(update.callback.user.user_id):
        await bot(
            AnswerCallback(
                callback_id=update.callback.callback_id,
                message=NewMessageBody(
                    text=Texts.Messages.messages_limit,
                    format=TextFormat.MARKDOWN,
                    notify=True,
                    attachments=[],
                ),
            )
        )
        return
        
    if await messages_time_out_reached(update.callback.user.user_id):
        await bot(
            AnswerCallback(
                callback_id=update.callback.callback_id,
                message=NewMessageBody(
                    text=Texts.Messages.messages_time_out,
                    format=TextFormat.MARKDOWN,
                    notify=True,
                    attachments=[],
                ),
            )
        )
        return

    # Все проверки пройдены - просим ввести сообщение
    await bot(
        AnswerCallback(
            callback_id=update.callback.callback_id,
            message=NewMessageBody(
                notify=True,
                text=Texts.Messages.get_message,
                format=TextFormat.MARKDOWN,
                attachments=[],
            ),
        )
    )

    await state_machine.set_state(update.callback.user.user_id, UserState.GET_MESSAGE)


async def send_message_filter(update: MessageCallbackUpdate) -> bool:
    return (
        update.callback.payload == "send_message"
        and await state_machine.get_state(update.callback.user.user_id)
        == UserState.SEND_MESSAGE
    )
