"""
Единый источник правды для отображения каждого шага флоу.

Каждая функция show_* полностью описывает один экран: текст + клавиатура.
Используется и при прямом прохождении флоу, и при навигации «Назад».
"""

from maxapi.enums.parse_mode import ParseMode
from maxapi.types import CallbackButton, LinkButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder

from bot.instance import send_message
from bot.texts import Texts
from core.config import Config
from services.backgrounds import get_available_backgrounds


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
    """Шаг выбора шаблона/фона."""
    backgrounds = await get_available_backgrounds()
    keyboard = InlineKeyboardBuilder()
    for i in range(0, len(backgrounds) - 1, 3):
        row_buttons = []
        for j in range(3):
            if i + j < len(backgrounds):
                bg = backgrounds[i + j]
                row_buttons.append(
                    CallbackButton(text=str(bg.id), payload=f"background_{bg.id}")
                )
        keyboard.row(*row_buttons)
    last_bg = backgrounds[-1]
    keyboard.row(
        CallbackButton(text=str(last_bg.id), payload=f"background_{last_bg.id}"),
        CallbackButton(text=Texts.Buttons.back, payload="back"),
    )
    await send_message(
        user_id=user_id,
        text=Texts.Messages.choose_background_prompt,
        attachments=[keyboard.as_markup()],
    )
