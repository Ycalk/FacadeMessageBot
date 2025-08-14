from aiomax.types.updates import BotStoppedUpdate
from aiomax import Bot
from shared_models.database import User
from tortoise.transactions import in_transaction
from bot.bot import state_machine


async def stop_handler(update: BotStoppedUpdate, bot: Bot) -> None:
    state_machine.clear_state(update.user.user_id)
    async with in_transaction():
        user = await User.get_or_none(max_id=update.user.user_id)
        if user:
            await user.delete()
