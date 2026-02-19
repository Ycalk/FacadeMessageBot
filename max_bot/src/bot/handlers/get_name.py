from maxapi import Bot
from maxapi.types import MessageCreated
from core.logger import get_logger

from bot.instance import get_context, name_validator
from bot.states import UserStates
from bot.steps import show_add_city
from bot.texts import Texts

logger = get_logger(__name__)


async def get_name(event: MessageCreated, bot: Bot) -> None:
    user_id = event.message.sender.user_id
    name = event.message.body.text

    if not name or len(name) < 1:
        await bot.send_message(
            user_id=user_id,
            text=Texts.Messages.invalid_name_text,
        )
        return

    if not await name_validator(name):
        await bot.send_message(
            user_id=user_id,
            text=Texts.Messages.invalid_name_text,
        )
        return

    ctx = get_context(user_id)
    await ctx.update_data(name=name.strip().capitalize())

    await show_add_city(user_id)
    await ctx.set_state(UserStates.get_city)
