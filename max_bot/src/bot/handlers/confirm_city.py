from maxapi.types import MessageCallback
from core.logger import get_logger

from bot.instance import get_context
from bot.states import UserStates
from bot.steps import show_choose_background
from bot.handlers.wrong_step import reply_wrong_step_for_callback

logger = get_logger(__name__)


async def confirm_city(callback: MessageCallback) -> None:
    user_id = callback.callback.user.user_id
    payload = callback.callback.payload
    ctx = get_context(user_id)
    current_state = await ctx.get_state()

    if current_state != str(UserStates.confirm_city):
        await reply_wrong_step_for_callback(callback)
        return

    if payload != 'confirm_city':
        return

    await show_choose_background(user_id)
    await ctx.set_state(UserStates.choose_background)
