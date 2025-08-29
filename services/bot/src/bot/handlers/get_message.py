from maxapi.types import MessageCreated
from maxapi.types.attachments.buttons import MessageButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.enums.parse_mode import ParseMode
from maxapi import Bot
from bot.utils import Texts, UserState, Config
from bot.bot import state_machine


async def get_message(event: MessageCreated, bot: Bot) -> None:
    if not event.message or not event.message.from_user:
        return

    # Валидация текста сообщения
    if (
        not event.message.text
        or len(event.message.text) > Config.MAX_MESSAGE_LENGTH
        or len(event.message.text) < 1
    ):
        await bot.send_message(
            user_id=event.message.from_user.user_id,
            text=Texts.Messages.invalid_message_text,
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    if any(char not in Config.ALLOWED_CHARACTERS for char in event.message.text):
        await bot.send_message(
            user_id=event.message.from_user.user_id,
            text=Texts.Messages.invalid_message_alphabet,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Следующий шаг - запрос имени пользователя
    attachments = []
    if event.message.from_user.first_name and len(event.message.from_user.first_name) > 0:
        # Если имя пользователя есть, добавляем кнопку с именем
        keyboard = InlineKeyboardBuilder()
        keyboard.add(
            MessageButton(text=event.message.from_user.first_name)
        )
        attachments = [keyboard.as_markup()]

    await bot.send_message(
        user_id=event.message.from_user.user_id,
        text=Texts.Messages.get_name_with_name_from_profile
        if attachments
        else Texts.Messages.get_name,
        parse_mode=ParseMode.MARKDOWN,
        notify=True,
        attachments=attachments,
    )

    # Устанавливаем состояние пользователя на получение имени
    await state_machine.set_state(event.message.from_user.user_id, UserState.GET_NAME)
    # Обновляем контекст пользователя: сохраняем текст сообщения
    await state_machine.update_context(
        event.message.from_user.user_id, message=event.message.text
    )


async def get_message_filter(event: MessageCreated) -> bool:
    if not event.message or not event.message.from_user:
        return False
    return (
        await state_machine.get_state(event.message.from_user.user_id)
        == UserState.GET_MESSAGE
    )
