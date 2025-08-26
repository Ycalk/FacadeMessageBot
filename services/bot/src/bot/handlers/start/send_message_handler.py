from aiomax.types.updates import MessageCallbackUpdate
from aiomax.types.attachment_requests import InlineKeyboardAttachmentRequest
from aiomax.types.keyboard import CallbackButton, Keyboard, LinkButton
from aiomax.types import TextFormat, ButtonIntent, NewMessageBody
from aiomax.methods import AnswerCallback
from aiomax import Bot
from bot.bot import state_machine
from bot.utils import Texts, UserState, Config
from shared_models.database import User


async def send_message_handler(update: MessageCallbackUpdate, bot: Bot) -> None:
    # Сразу просим ввести сообщение
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
    
    # Создаем пользователя если он новый
    await User.update_or_create(
        defaults={
            "first_name": update.callback.user.first_name,
            "last_name": update.callback.user.last_name,
            "username": update.callback.user.username,
        },
        max_id=update.callback.user.user_id,
    )


async def send_message_filter(update: MessageCallbackUpdate) -> bool:
    return (
        update.callback.payload == "send_message"
        and await state_machine.get_state(update.callback.user.user_id)
        == UserState.SEND_MESSAGE
    )
