from aiomax.types.updates import MessageCreatedUpdate
from aiomax.types import (
    InlineKeyboardAttachmentRequest,
    TextFormat,
    Keyboard,
    MessageButton,
)
from aiomax import Bot
from aiomax.methods import SendMessage
from bot.utils import Texts, UserState, Config
from bot.bot import state_machine, name_validator


async def get_message(update: MessageCreatedUpdate, bot: Bot) -> None:
    if not update.message or not update.message.sender:
        return

    # Валидация текста сообщения
    if (
        not update.message.body.text
        or len(update.message.body.text) > Config.MAX_MESSAGE_LENGTH
        or len(update.message.body.text) < 1
    ):
        await bot(
            SendMessage(
                user_id=update.message.sender.user_id,
                text=Texts.Messages.invalid_message_text,
                text_format=TextFormat.MARKDOWN,
            )
        )
        return
    if any(char not in Config.ALPHABET for char in update.message.body.text):
        await bot(
            SendMessage(
                user_id=update.message.sender.user_id,
                text=Texts.Messages.invalid_message_alphabet,
                text_format=TextFormat.MARKDOWN,
            )
        )
        return

    # Следующий шаг - запрос имени пользователя

    if await name_validator(update.message.sender.first_name):
        # Если имя пользователя валидно, добавляем кнопку с именем
        attachments = [
            InlineKeyboardAttachmentRequest(
                payload=Keyboard(
                    buttons=[
                        [
                            MessageButton(text=update.message.sender.first_name),
                        ]
                    ]
                )
            )
        ]
    else:
        attachments = []
    await bot(
        SendMessage(
            user_id=update.message.sender.user_id,
            text=Texts.Messages.get_name_with_name_from_profile
            if attachments
            else Texts.Messages.get_name,
            text_format=TextFormat.MARKDOWN,
            notify=True,
            attachments=attachments,
        ),
    )

    # Устанавливаем состояние пользователя на получение имени
    state_machine.set_state(update.message.sender.user_id, UserState.GET_NAME)
    # Обновляем контекст пользователя: сохраняем текст сообщения
    state_machine.update_context(
        update.message.sender.user_id, message=update.message.body.text
    )


def get_message_filter(update: MessageCreatedUpdate) -> bool:
    if not update.message or not update.message.sender:
        return False
    return (
        state_machine.get_state(update.message.sender.user_id) == UserState.GET_MESSAGE
    )
