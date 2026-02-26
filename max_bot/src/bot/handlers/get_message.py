from maxapi import Bot
from maxapi.types import MessageCreated
from core.logger import get_logger

from bot.instance import get_context
from bot.states import UserStates
from bot.steps import show_get_name
from bot.texts import Texts
from core.config import Config
from services.blacklist import is_blacklisted
from services.message_input_logs import log_get_message_input
from services.mistral_moderator import moderate_with_mistral
from services.text_validator import is_text_allowed

logger = get_logger(__name__)


async def get_message(event: MessageCreated, bot: Bot) -> None:
    user_id = event.message.sender.user_id
    text = event.message.body.text
    await log_get_message_input(
        user_max_id=user_id,
        text=text or "",
    )

    if not text or len(text) > Config.MAX_MESSAGE_LENGTH or len(text) < 1:
        await bot.send_message(
            user_id=user_id,
            text=Texts.Messages.invalid_message_text,
        )
        return

    if not is_text_allowed(text):
        await bot.send_message(
            user_id=user_id,
            text=Texts.Messages.invalid_message_alphabet,
        )
        return

    # Быстрая проверка по чёрному списку (до Mistral — бесплатно и мгновенно)
    if is_blacklisted(text):
        logger.info(f"Текст отклонён чёрным списком: {text!r}")
        await bot.send_message(user_id=user_id, text=Texts.Messages.message_rejected_by_ai)
        return

    # Предварительная автомодерация текста через Mistral
    moderation_result = await moderate_with_mistral(text=text, name="", city="")
    if not moderation_result.get("approved", True):
        logger.info(f"Текст отклонён Mistral на этапе ввода: {moderation_result.get('reason', '')}")
        await bot.send_message(user_id=user_id, text=Texts.Messages.message_rejected_by_ai)
        return

    ctx = get_context(user_id)
    await ctx.update_data(message=text)

    first_name = getattr(event.message.sender, "first_name", None)
    await show_get_name(user_id, first_name)
    await ctx.set_state(UserStates.get_name)
