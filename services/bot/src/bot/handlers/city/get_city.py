from maxapi.types import MessageCreated, CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.enums.parse_mode import ParseMode
from maxapi import Bot
from bot.utils import Texts, UserState
from bot.bot import state_machine, city_extractor, cities_client


async def get_city(event: MessageCreated, bot: Bot) -> None:
    if not event.message or not event.message.from_user:
        return

    # Пользователь ввел текстовое сообщение с названием города
    # Проверяем, что текст сообщения не пустой
    if not event.message.text:
        await bot.send_message(
            user_id=event.message.from_user.user_id,
            text=Texts.Messages.city_not_found,
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    else:
        # Ищем города в cities service
        search_result = await cities_client.search_cities(event.message.text, limit=5)

        if search_result and search_result.cities:
            city = search_result.cities[0].name
        else:
            # Если cities service не доступен или не найдено совпадений, используем старую логику
            city = city_extractor.extract_from_text(event.message.text)
        
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
        
        await bot.send_message(
            user_id=event.message.from_user.user_id,
            text=Texts.Messages.confirm_city.format(city=city),
            parse_mode=ParseMode.MARKDOWN,
            attachments=[keyboard.as_markup()],
        )
        
        await state_machine.set_state(
            event.message.from_user.user_id, UserState.CONFIRM_CITY
        )
        await state_machine.update_context(event.message.from_user.user_id, city=city)


async def get_city_filter(event: MessageCreated) -> bool:
    if not event.message or not event.message.from_user:
        return False
    return (
        await state_machine.get_state(event.message.from_user.user_id)
        == UserState.GET_CITY
    )
