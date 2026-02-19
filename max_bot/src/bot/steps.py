"""
Единый источник правды для отображения каждого шага флоу.

Каждая функция show_* полностью описывает один экран: текст + клавиатура.
Используется и при прямом прохождении флоу, и при навигации «Назад».
"""

from maxapi.enums.parse_mode import ParseMode
from maxapi.types import CallbackButton, LinkButton
from maxapi.types.input_media import InputMediaBuffer
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder

from bot.instance import send_message, send_photo_message
from bot.texts import Texts
from core.config import Config
from core.logger import get_logger
from services.backgrounds import BACKGROUND_IDS, get_backgrounds_preview_path

logger = get_logger(__name__)

# Кэш байтов backgrounds.png — читаем с диска один раз
_backgrounds_preview_cache: bytes | None = None


def _get_backgrounds_preview_bytes() -> bytes | None:
    global _backgrounds_preview_cache
    if _backgrounds_preview_cache is None:
        path = get_backgrounds_preview_path()
        if path is not None:
            _backgrounds_preview_cache = path.read_bytes()
            logger.info("backgrounds.png закэширован в памяти")
    return _backgrounds_preview_cache


async def show_start(user_id: int) -> None:
    """Приветственный экран с курсивным дисклеймером и кнопками."""
    keyboard = InlineKeyboardBuilder()
    if Config.TERMS_OF_USE_URL:
        keyboard.row(
            LinkButton(text=Texts.Buttons.conditions, url=Config.TERMS_OF_USE_URL)
        )
    keyboard.row(
        CallbackButton(text=Texts.Buttons.send_message, payload="send_message")
    )
    await send_message(
        user_id=user_id,
        text=Texts.Messages.start,
        attachments=[keyboard.as_markup()],
        parse_mode=ParseMode.MARKDOWN,
    )


async def show_moderation_warning(user_id: int) -> None:
    """Экран предупреждения о модерации."""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        CallbackButton(text=Texts.Buttons.write_greeting, payload="write_greeting")
    )
    await send_message(
        user_id=user_id,
        text=Texts.Messages.moderation_warning,
        attachments=[keyboard.as_markup()],
    )


async def show_get_message(user_id: int) -> None:
    """Шаг ввода текста поздравления."""
    keyboard = InlineKeyboardBuilder()
    keyboard.add(CallbackButton(text=Texts.Buttons.back, payload="back"))
    await send_message(
        user_id=user_id,
        text=Texts.Messages.get_message,
        attachments=[keyboard.as_markup()],
    )


async def show_get_name(user_id: int, first_name: str | None = None) -> None:
    """Шаг ввода имени / подписи (с опциональной кнопкой профиля)."""
    keyboard = InlineKeyboardBuilder()
    if first_name:
        keyboard.add(CallbackButton(text=first_name, payload="use_profile_name"))
    keyboard.add(CallbackButton(text=Texts.Buttons.back, payload="back"))
    text = (
        Texts.Messages.get_name_with_name_from_profile
        if first_name
        else Texts.Messages.get_name
    )
    await send_message(
        user_id=user_id,
        text=text,
        attachments=[keyboard.as_markup()],
    )


async def show_add_city(user_id: int) -> None:
    """Шаг ввода города."""
    keyboard = InlineKeyboardBuilder()
    keyboard.add(CallbackButton(text=Texts.Buttons.back, payload="back"))
    await send_message(
        user_id=user_id,
        text=Texts.Messages.add_city,
        attachments=[keyboard.as_markup()],
    )


async def show_confirm_city(user_id: int, city: str) -> None:
    """Шаг подтверждения найденного города."""
    keyboard = InlineKeyboardBuilder()
    keyboard.add(CallbackButton(text="Подтвердить", payload="confirm_city"))
    keyboard.add(CallbackButton(text=Texts.Buttons.back, payload="back"))
    await send_message(
        user_id=user_id,
        text=Texts.Messages.confirm_city.format(city=city),
        attachments=[keyboard.as_markup()],
    )


async def show_choose_background(user_id: int) -> None:
    """Шаг выбора фона: одно общее превью + три кнопки."""
    preview_bytes = _get_backgrounds_preview_bytes()
    if preview_bytes is not None:
        await send_photo_message(
            user_id=user_id,
            attachments=[
                InputMediaBuffer(buffer=preview_bytes, filename="backgrounds.png")
            ],
        )
    else:
        logger.warning("Превью фонов (backgrounds.png) не найдено, отправляем только кнопки")

    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        *[
            CallbackButton(text=f"Фон {bg_id}", payload=f"background_{bg_id}")
            for bg_id in BACKGROUND_IDS
        ]
    )
    keyboard.row(CallbackButton(text=Texts.Buttons.back, payload="back"))
    await send_message(
        user_id=user_id,
        text=Texts.Messages.choose_background_prompt,
        attachments=[keyboard.as_markup()],
    )
