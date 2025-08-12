from aiomax.types.updates import MessageCallbackUpdate
from aiomax.types import TextFormat, NewMessageBody
from aiomax.methods import AnswerCallback, SendMessage
from aiomax import Bot
from bot.bot import state_machine
from bot.utils import (
    Texts,
    UserState,
    attempts_limit_reached,
    messages_limit_reached,
    messages_time_out_reached,
)


async def write_message_handler(update: MessageCallbackUpdate, bot: Bot) -> None:
    # Реакция на сообщение о том, что сообщение пройдет модерацию
    await bot(
        AnswerCallback(
            callback_id=update.callback.callback_id,
            message=NewMessageBody(
                notify=True,
                text=Texts.Messages.write_message,
                format=TextFormat.MARKDOWN,
                attachments=[],
            ),
        )
    )
    # Проверяем, достиг ли пользователь лимита попыток отправки сообщений
    # или лимита количества сообщений
    # Если достигнут, то отправляем соответствующее сообщение и выходим
    if await attempts_limit_reached(update.callback.user.user_id):
        await bot(
            AnswerCallback(
                callback_id=update.callback.callback_id,
                message=NewMessageBody(
                    text=Texts.Messages.attempts_limit,
                    attachments=[],
                    notify=True,
                    format=TextFormat.MARKDOWN,
                ),
            )
        )
        return
    if await messages_limit_reached(update.callback.user.user_id):
        await bot(
            SendMessage(
                user_id=update.callback.user.user_id,
                text=Texts.Messages.messages_limit,
            )
        )
        return
    if await messages_time_out_reached(update.callback.user.user_id):
        await bot(
            SendMessage(
                user_id=update.callback.user.user_id,
                text=Texts.Messages.messages_time_out,
            )
        )
        return

    # Начинаем сбор послания пользователя
    # Сначала спрашиваем сообщение, которое пользователь хочет отправить
    await bot(
        SendMessage(
            user_id=update.callback.user.user_id,
            text=Texts.Messages.get_message,
        )
    )
    state_machine.set_state(update.callback.user.user_id, UserState.GET_MESSAGE)


def write_message_filter(update: MessageCallbackUpdate) -> bool:
    return (
        update.callback.payload == "write_message"
        and state_machine.get_state(update.callback.user.user_id)
        == UserState.WRITE_MESSAGE
    )
