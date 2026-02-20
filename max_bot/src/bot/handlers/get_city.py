from maxapi import Bot
from maxapi.types import MessageCreated
from core.logger import get_logger

from bot.instance import get_context, cities_client
from bot.states import UserStates
from bot.steps import show_confirm_city
from bot.texts import Texts

logger = get_logger(__name__)


async def get_city(event: MessageCreated, bot: Bot) -> None:
    user_id = event.message.sender.user_id
    text = event.message.body.text

    if not text or len(text.strip()) < 1:
        await bot.send_message(
            user_id=user_id,
            text="Пожалуйста, введите название города.",
        )
        return

    city_input = text.strip()

    # Валидация через cities service
    search_result = await cities_client.search_cities(city_input, limit=1)
    if not search_result or not search_result.cities:
        # Город не найден - просим ввести заново
        await bot.send_message(
            user_id=user_id,
            text=f"Город '{city_input}' не найден. Пожалуйста, введите корректное название города.",
        )
        return

    # Используем найденный город
    city = search_result.cities[0].name

    ctx = get_context(user_id)
    await ctx.update_data(city=city)

    await show_confirm_city(user_id, city)
    await ctx.set_state(UserStates.confirm_city)
