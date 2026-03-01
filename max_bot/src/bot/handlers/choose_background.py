"""Обработчик выбора фона для сообщения."""

import asyncio
from functools import partial

from maxapi.enums.parse_mode import ParseMode
from maxapi.types import MessageCallback, CallbackButton
from maxapi.types.input_media import InputMediaBuffer
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from core.logger import get_logger

from bot.instance import get_context, send_message, send_photo_message
from bot.states import UserStates
from bot.texts import Texts
from bot.handlers.wrong_step import reply_wrong_step_for_callback
from services.backgrounds import BACKGROUND_IDS, generate_text_preview_bytes

logger = get_logger(__name__)


def _escape_markdown(text: str) -> str:
    """Экранирует markdown-символы в пользовательском вводе."""
    if not text:
        return ""
    escape_chars = "\\`*_[]()"
    return "".join(f"\\{ch}" if ch in escape_chars else ch for ch in text)


async def choose_background(callback: MessageCallback) -> None:
    """Обработка выбора фона."""
    user_id = callback.callback.user.user_id
    payload = callback.callback.payload
    ctx = get_context(user_id)
    current_state = await ctx.get_state()

    if current_state != str(UserStates.choose_background):
        await reply_wrong_step_for_callback(callback)
        return

    if not payload.startswith("background_"):
        return

    try:
        background_id = int(payload.split("_")[1])
        if background_id not in BACKGROUND_IDS:
            return
    except (ValueError, IndexError):
        return

    # Сразу меняем состояние — блокируем повторные нажатия на время генерации
    await ctx.set_state(UserStates.preview)
    await ctx.update_data(frame_id=background_id)
    data = await ctx.get_data()
    message_text = data.get("message", "")
    name = data.get("name", "")
    city = data.get("city", "")

    # Сообщаем пользователю что идёт генерация
    await send_message(user_id=user_id, text="⏳ Создаём превью...")

    # Генерируем превью в памяти (без сохранения на диск — файл сохраним только при отправке на модерацию)
    loop = asyncio.get_event_loop()
    preview_bytes = await loop.run_in_executor(
        None,
        partial(generate_text_preview_bytes, background_id, message_text, name, city),
    )

    keyboard = InlineKeyboardBuilder()
    keyboard.row(CallbackButton(text=Texts.Buttons.send_to_moderation, payload="send_to_moderation"))
    keyboard.row(CallbackButton(text=Texts.Buttons.edit_fields, payload="edit_greeting"))

    preview_text = Texts.Messages.preview_format.format(
        message=_escape_markdown(message_text),
        name=_escape_markdown(name),
        city=_escape_markdown(city),
    )

    if preview_bytes is not None:
        await send_photo_message(
            user_id=user_id,
            text=preview_text,
            parse_mode=ParseMode.MARKDOWN,
            attachments=[
                InputMediaBuffer(
                    buffer=preview_bytes,
                    filename="preview.png",
                ),
                keyboard.as_markup(),
            ],
        )
    else:
        logger.warning(f"Не удалось сгенерировать превью для фона {background_id}")
        await send_message(
            user_id=user_id,
            text=preview_text,
            parse_mode=ParseMode.MARKDOWN,
            attachments=[keyboard.as_markup()],
        )
