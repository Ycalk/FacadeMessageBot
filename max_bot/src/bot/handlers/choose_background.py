"""Обработчик выбора фона для сообщения."""

from maxapi.types import MessageCallback, CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from core.logger import get_logger

from bot.instance import get_context
from bot.states import UserStates
from bot.texts import Texts
from bot.handlers.wrong_step import reply_wrong_step_for_callback

logger = get_logger(__name__)


async def choose_background(callback: MessageCallback) -> None:
    """Обработка выбора фона."""
    user_id = callback.callback.user.user_id
    payload = callback.callback.payload
    ctx = get_context(user_id)
    current_state = await ctx.get_state()

    if current_state != str(UserStates.choose_background):
        await reply_wrong_step_for_callback(callback)
        return

    # Проверяем что payload в формате background_N
    if not payload.startswith('background_'):
        return

    try:
        background_id = int(payload.split('_')[1])
        if background_id < 1 or background_id > 10:
            return
    except (ValueError, IndexError):
        return

    # Сохраняем выбранный фон как int (для БД frame_id)
    await ctx.update_data(frame_id=background_id)

    # Получаем все данные для предпросмотра
    data = await ctx.get_data()
    message_text = data.get("message", "")
    name = data.get("name", "")
    city = data.get("city", "")

    # Показываем предпросмотр в новом формате
    preview_text = Texts.Messages.preview_format.format(
        message=message_text,
        name=name,
        city=city,
    )

    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        CallbackButton(text=Texts.Buttons.send_to_moderation, payload="send_to_moderation")
    )
    keyboard.add(
        CallbackButton(text=Texts.Buttons.edit_fields, payload="edit_greeting")
    )
    keyboard.add(
        CallbackButton(text=Texts.Buttons.back, payload="back")
    )

    await callback.message.answer(
        text=preview_text,
        attachments=[keyboard.as_markup()],
    )

    await ctx.set_state(UserStates.preview)
