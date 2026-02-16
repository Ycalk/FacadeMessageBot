from maxapi import Bot
from maxapi.types import MessageCreated, CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from core.logger import get_logger

from bot.instance import get_context, cities_client
from bot.states import UserStates
from bot.texts import Texts

logger = get_logger(__name__)


async def get_city(event: MessageCreated, bot: Bot) -> None:
    user_id = event.message.sender.user_id
    text = event.message.body.text

    if not text or len(text.strip()) < 1:
        keyboard = InlineKeyboardBuilder()
        keyboard.add(CallbackButton(text=Texts.Buttons.back, payload="back"))
        await bot.send_message(
            user_id=user_id,
            text="Пожалуйста, введите название города.",
            attachments=[keyboard.as_markup()],
        )
        return

    city_input = text.strip()

    # Валидация через cities service
    search_result = await cities_client.search_cities(city_input, limit=1)
    if not search_result or not search_result.cities:
        # Город не найден - просим ввести заново
        keyboard = InlineKeyboardBuilder()
        keyboard.add(CallbackButton(text=Texts.Buttons.back, payload="back"))
        await bot.send_message(
            user_id=user_id,
            text=f"Город '{city_input}' не найден. Пожалуйста, введите корректное название города.",
            attachments=[keyboard.as_markup()],
        )
        return

    # Используем найденный город
    city = search_result.cities[0].name

    ctx = get_context(user_id)
    await ctx.update_data(city=city)

    keyboard = InlineKeyboardBuilder()
    keyboard.add(CallbackButton(text="Подтвердить", payload="confirm_city"))
    keyboard.add(CallbackButton(text=Texts.Buttons.back, payload="back"))

    await bot.send_message(
        user_id=user_id,
        text=Texts.Messages.confirm_city.format(city=city),
        attachments=[keyboard.as_markup()],
    )

    await ctx.set_state(UserStates.confirm_city)
