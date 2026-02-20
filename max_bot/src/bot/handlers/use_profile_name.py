"""Обработчик использования имени из профиля пользователя."""

from maxapi.types import MessageCallback
from core.logger import get_logger

from bot.instance import get_context, name_validator
from bot.states import UserStates
from bot.texts import Texts

logger = get_logger(__name__)


async def use_profile_name(callback: MessageCallback) -> None:
    """Использует имя из профиля пользователя."""
    user_id = callback.callback.user.user_id
    first_name = getattr(callback.callback.user, "first_name", None)

    if not first_name:
        # Если имени нет (не должно произойти, но на всякий случай)
        await callback.message.answer(text=Texts.Messages.get_name)
        return

    # Валидируем имя из профиля
    if not await name_validator(first_name):
        await callback.message.answer(
            text=Texts.Messages.invalid_name_text + "\nПожалуйста, введите имя вручную.",
        )
        return

    # Сохраняем имя из профиля
    ctx = get_context(user_id)
    await ctx.update_data(name=first_name.strip().capitalize())

    await callback.message.answer(
        text=Texts.Messages.add_city,
    )

    await ctx.set_state(UserStates.get_city)
