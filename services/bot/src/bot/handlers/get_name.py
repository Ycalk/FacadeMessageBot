import logging
from maxapi.types import MessageCreated
from maxapi.enums.parse_mode import ParseMode
from maxapi import Bot
from bot.utils import Texts, UserState
from bot.bot import state_machine

logger = logging.getLogger(__name__)


async def get_name(event: MessageCreated, bot: Bot) -> None:
    if not event.message or not event.message.sender:
        logger.debug("get_name: Нет сообщения или отправителя")
        return
        
    # Проверяем состояние пользователя
    current_state = await state_machine.get_state(event.message.sender.user_id)
    if current_state != UserState.GET_NAME:
        logger.debug(f"get_name: Неверное состояние {current_state} для пользователя {event.message.sender.user_id}, пропускаем")
        return
        
    logger.debug(f"get_name: Обработка имени от пользователя {event.message.sender.user_id}: '{event.message.body.text}'")

    # Проверяем что имя не пустое
    if not event.message.body.text or len(event.message.body.text) < 1:
        logger.debug(f"get_name: Пустое имя от пользователя {event.message.sender.user_id}")
        await bot.send_message(
            user_id=event.message.sender.user_id,
            text=Texts.Messages.invalid_name_text,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    logger.debug(f"get_name: Имя принято, переходим к получению города для пользователя {event.message.sender.user_id}")
    await bot.send_message(
        user_id=event.message.sender.user_id,
        text=Texts.Messages.add_city_without_geo,
        parse_mode=ParseMode.MARKDOWN,
    )

    # Устанавливаем состояние пользователя на получение города
    await state_machine.set_state(event.message.sender.user_id, UserState.GET_CITY)
    # Обновляем контекст пользователя: сохраняем имя пользователя
    await state_machine.update_context(
        event.message.sender.user_id, name=event.message.body.text.capitalize()
    )


async def get_name_filter(event: MessageCreated) -> bool:
    if not event.message or not event.message.sender:
        return False
    result = (
        await state_machine.get_state(event.message.sender.user_id)
        == UserState.GET_NAME
    )
    logger.debug(f"get_name_filter: Пользователь {event.message.sender.user_id}, результат фильтра: {result}")
    return result
