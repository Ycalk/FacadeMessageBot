import logging
from maxapi.types import MessageCreated, CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.enums.parse_mode import ParseMode
from maxapi import Bot
from bot.utils import Texts, UserState
from bot.bot import state_machine, city_extractor, cities_client

logger = logging.getLogger(__name__)


async def get_city(event: MessageCreated, bot: Bot) -> None:
    if not event.message or not event.message.sender:
        logger.debug("get_city: Нет сообщения или отправителя")
        return
        
    # Проверяем состояние пользователя
    current_state = await state_machine.get_state(event.message.sender.user_id)
    if current_state != UserState.GET_CITY:
        logger.debug(f"get_city: Неверное состояние {current_state} для пользователя {event.message.sender.user_id}, пропускаем")
        return
        
    logger.debug(f"get_city: Обработка города от пользователя {event.message.sender.user_id}: '{event.message.body.text}'")

    # Пользователь ввел текстовое сообщение с названием города
    # Проверяем, что текст сообщения не пустой
    if not event.message.body.text:
        logger.debug(f"get_city: Пустое сообщение от пользователя {event.message.sender.user_id}")
        await bot.send_message(
            user_id=event.message.sender.user_id,
            text=Texts.Messages.city_not_found,
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    else:
        # Ищем города в cities service
        logger.debug(f"get_city: Поиск города '{event.message.body.text}' через cities service")
        search_result = await cities_client.search_cities(event.message.body.text, limit=5)

        if search_result and search_result.cities:
            city = search_result.cities[0].name
            logger.debug(f"get_city: Найден город через cities service: {city}")
        else:
            # Если cities service не доступен или не найдено совпадений, используем старую логику
            city = city_extractor.extract_from_text(event.message.body.text)
            logger.debug(f"get_city: Используем city_extractor, найден: {city}")
        
        # Создаем клавиатуру с кнопками
        keyboard = InlineKeyboardBuilder()
        keyboard.add(CallbackButton(
            text="Подтвердить",
            payload="confirm_city",
        ))
        keyboard.add(CallbackButton(
            text="Ввести заново",
            payload="try_again_city",
        ))
        
        logger.debug(f"get_city: Предлагаем подтвердить город '{city}' пользователю {event.message.sender.user_id}")
        await bot.send_message(
            user_id=event.message.sender.user_id,
            text=Texts.Messages.confirm_city.format(city=city),
            parse_mode=ParseMode.MARKDOWN,
            attachments=[keyboard.as_markup()],
        )
        
        await state_machine.set_state(
            event.message.sender.user_id, UserState.CONFIRM_CITY
        )
        await state_machine.update_context(event.message.sender.user_id, city=city)


async def get_city_filter(event: MessageCreated) -> bool:
    if not event.message or not event.message.sender:
        return False
    result = (
        await state_machine.get_state(event.message.sender.user_id)
        == UserState.GET_CITY
    )
    logger.debug(f"get_city_filter: Пользователь {event.message.sender.user_id}, результат фильтра: {result}")
    return result
