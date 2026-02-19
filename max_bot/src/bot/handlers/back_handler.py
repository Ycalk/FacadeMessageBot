"""Универсальный обработчик кнопки 'Назад' — маппинг состояний на шаги флоу."""

from core.logger import get_logger
from maxapi.types import MessageCallback

from bot.instance import get_context
from bot.states import UserStates
from bot.steps import (
    show_start,
    show_get_message,
    show_get_name,
    show_add_city,
    show_confirm_city,
    show_choose_background,
)

logger = get_logger(__name__)

# Маппинг: текущее состояние → предыдущее состояние
# None означает возврат на стартовый экран (вне FSM)
BACK_STATE_MAP: dict[str, UserStates | None] = {
    str(UserStates.get_message):       None,
    str(UserStates.get_name):          UserStates.get_message,
    str(UserStates.get_city):          UserStates.get_name,
    str(UserStates.confirm_city):      UserStates.get_city,
    str(UserStates.choose_background): UserStates.confirm_city,
    str(UserStates.preview):           UserStates.choose_background,
}


async def back_button(callback: MessageCallback) -> None:
    user_id = callback.callback.user.user_id
    ctx = get_context(user_id)
    current_state = await ctx.get_state()

    # Нет состояния или неизвестное → стартовый экран
    if not current_state or current_state not in BACK_STATE_MAP:
        if current_state:
            logger.warning(
                f"Неизвестное состояние {current_state} для пользователя {user_id}"
            )
        await ctx.clear()
        await show_start(user_id)
        return

    prev_state = BACK_STATE_MAP[current_state]
    data = await ctx.get_data()

    if prev_state is None:
        # Возврат на стартовый экран
        await ctx.clear()
        await show_start(user_id)

    elif prev_state == UserStates.get_message:
        await show_get_message(user_id)
        await ctx.set_state(UserStates.get_message)

    elif prev_state == UserStates.get_name:
        first_name = getattr(callback.callback.user, "first_name", None)
        await show_get_name(user_id, first_name)
        await ctx.set_state(UserStates.get_name)

    elif prev_state == UserStates.get_city:
        await show_add_city(user_id)
        await ctx.set_state(UserStates.get_city)

    elif prev_state == UserStates.confirm_city:
        city = data.get("city", "")
        await show_confirm_city(user_id, city)
        await ctx.set_state(UserStates.confirm_city)

    elif prev_state == UserStates.choose_background:
        await show_choose_background(user_id)
        await ctx.set_state(UserStates.choose_background)
