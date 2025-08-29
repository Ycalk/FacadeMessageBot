import logging
from maxapi.types import MessageCreated
from maxapi.types.attachments.buttons import MessageButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.enums.parse_mode import ParseMode
from maxapi import Bot
from bot.utils import Texts, UserState, Config
from bot.bot import state_machine

logger = logging.getLogger(__name__)


async def get_message(event: MessageCreated, bot: Bot) -> None:
    if not event.message or not event.message.sender:
        logger.debug("get_message: Нет сообщения или отправителя")
        return
        
    # Проверяем состояние пользователя
    current_state = await state_machine.get_state(event.message.sender.user_id)
    if current_state != UserState.GET_MESSAGE:
        logger.debug(f"get_message: Неверное состояние {current_state} для пользователя {event.message.sender.user_id}, пропускаем")
        return
        
    logger.debug(f"get_message: Обработка сообщения от пользователя {event.message.sender.user_id}: '{event.message.body.text}'")

    # Валидация текста сообщения
    if (
        not event.message.body.text
        or len(event.message.body.text) > Config.MAX_MESSAGE_LENGTH
        or len(event.message.body.text) < 1
    ):
        logger.debug(f"get_message: Невалидное сообщение от пользователя {event.message.sender.user_id}: длина {len(event.message.body.text) if event.message.body.text else 0}")
        await bot.send_message(
            user_id=event.message.sender.user_id,
            text=Texts.Messages.invalid_message_text,
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    if any(char not in Config.ALLOWED_CHARACTERS for char in event.message.body.text):
        logger.debug(f"get_message: Недопустимые символы в сообщении от пользователя {event.message.sender.user_id}")
        await bot.send_message(
            user_id=event.message.sender.user_id,
            text=Texts.Messages.invalid_message_alphabet,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Следующий шаг - запрос имени пользователя
    attachments = []
    if event.message.sender.first_name and len(event.message.sender.first_name) > 0:
        # Если имя пользователя есть, добавляем кнопку с именем
        keyboard = InlineKeyboardBuilder()
        keyboard.add(
            MessageButton(text=event.message.sender.first_name)
        )
        attachments = [keyboard.as_markup()]

    logger.debug(f"get_message: Сообщение принято, переходим к получению имени для пользователя {event.message.sender.user_id}")
    await bot.send_message(
        user_id=event.message.sender.user_id,
        text=Texts.Messages.get_name_with_name_from_profile
        if attachments
        else Texts.Messages.get_name,
        parse_mode=ParseMode.MARKDOWN,
        notify=True,
        attachments=attachments,
    )

    # Устанавливаем состояние пользователя на получение имени
    await state_machine.set_state(event.message.sender.user_id, UserState.GET_NAME)
    # Обновляем контекст пользователя: сохраняем текст сообщения
    await state_machine.update_context(
        event.message.sender.user_id, message=event.message.body.text
    )


async def get_message_filter(event: MessageCreated) -> bool:
    if not event.message or not event.message.sender:
        return False
    result = (
        await state_machine.get_state(event.message.sender.user_id)
        == UserState.GET_MESSAGE
    )
    logger.debug(f"get_message_filter: Пользователь {event.message.sender.user_id}, результат фильтра: {result}")
    return result
