from maxapi import Bot
from maxapi.types import MessageCreated, CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from core.logger import get_logger

from bot.instance import get_context
from bot.states import UserStates
from bot.texts import Texts
from core.config import Config

logger = get_logger(__name__)


async def get_message(event: MessageCreated, bot: Bot) -> None:
    user_id = event.message.sender.user_id
    text = event.message.body.text

    if not text or len(text) > Config.MAX_MESSAGE_LENGTH or len(text) < 1:
        await bot.send_message(
            user_id=user_id,
            text=Texts.Messages.invalid_message_text,
        )
        return

    if any(char not in Config.ALLOWED_CHARACTERS for char in text):
        await bot.send_message(
            user_id=user_id,
            text=Texts.Messages.invalid_message_alphabet,
        )
        return

    ctx = get_context(user_id)
    await ctx.update_data(message=text)

    # Переходим к запросу имени
    # Проверяем, есть ли first_name в профиле пользователя
    first_name = getattr(event.message.sender, "first_name", None)

    keyboard = InlineKeyboardBuilder()

    if first_name:
        # Если есть имя в профиле - предлагаем использовать его
        keyboard.add(
            CallbackButton(text=first_name, payload="use_profile_name")
        )
        keyboard.add(
            CallbackButton(text=Texts.Buttons.back, payload="back")
        )
        await bot.send_message(
            user_id=user_id,
            text=Texts.Messages.get_name_with_name_from_profile,
            attachments=[keyboard.as_markup()],
        )
    else:
        # Если имени нет - просто запрашиваем
        keyboard.add(
            CallbackButton(text=Texts.Buttons.back, payload="back")
        )
        await bot.send_message(
            user_id=user_id,
            text=Texts.Messages.get_name,
            attachments=[keyboard.as_markup()],
        )

    await ctx.set_state(UserStates.get_name)