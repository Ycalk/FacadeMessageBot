from aiomax.types.updates import MessageCreatedUpdate
from aiomax.types import TextFormat
from aiomax.methods import SendMessage
from aiomax import Bot
from bot.utils import (
    Texts,
    Config,
    UserState,
    attempts_limit_reached,
    messages_limit_reached,
    messages_time_out_reached,
)
from bot.bot import state_machine
from shared_models.database import User


async def create_command_handler(update: MessageCreatedUpdate, bot: Bot) -> None:
    if not update.message or not update.message.sender:
        return

    user = await User.get_or_none(max_id=update.message.sender.user_id)
    if not user:
        return

    if Config.MESSAGE_COLLECTION_STOPPED:
        await bot(
            SendMessage(
                user_id=update.message.sender.user_id,
                text=Texts.Messages.message_collection_stopped,
            )
        )
        return

    # Проверяем, достиг ли пользователь лимита попыток отправки сообщений
    # или лимита количества сообщений
    # Если достигнут, то отправляем соответствующее сообщение и выходим
    if await attempts_limit_reached(update.message.sender.user_id):
        await bot(
            SendMessage(
                user_id=update.message.sender.user_id,
                text=Texts.Messages.attempts_limit,
            )
        )
        return
    if await messages_limit_reached(update.message.sender.user_id):
        await bot(
            SendMessage(
                user_id=update.message.sender.user_id,
                text=Texts.Messages.messages_limit,
            )
        )
        return
    if await messages_time_out_reached(update.message.sender.user_id):
        await bot(
            SendMessage(
                user_id=update.message.sender.user_id,
                text=Texts.Messages.messages_time_out,
            )
        )
        return

    await bot(
        SendMessage(
            user_id=update.message.sender.user_id,
            text=Texts.Messages.get_message,
            text_format=TextFormat.MARKDOWN,
        )
    )
    state_machine.set_state(update.message.sender.user_id, UserState.GET_MESSAGE)


def create_command_filter(update: MessageCreatedUpdate) -> bool:
    return (
        update.message is not None
        and update.message.sender is not None
        and update.message.body.text is not None
        and update.message.body.text == "/create"
    )
