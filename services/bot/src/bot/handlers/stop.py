from maxapi.types import BotStopped
from maxapi import Bot
from shared_models.database import User
from tortoise.transactions import in_transaction
from bot.bot import state_machine


async def stop_handler(event: BotStopped, bot: Bot) -> None:
    await state_machine.clear_state(event.user.user_id)
    async with in_transaction():
        user = await User.get_or_none(max_id=event.user.user_id)
        if user:
            await user.delete()
