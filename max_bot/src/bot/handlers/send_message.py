from core.logger import get_logger

from maxapi.types import MessageCallback

from bot.instance import get_context
from bot.steps import show_moderation_warning

logger = get_logger(__name__)


async def send_message_handler(callback: MessageCallback) -> None:
    """Показывает экран предупреждения о модерации перед вводом поздравления."""
    user_id = callback.callback.user.user_id
    ctx = get_context(user_id)

    # Очищаем предыдущее состояние если пользователь хочет начать заново
    current_state = await ctx.get_state()
    if current_state:
        await ctx.clear()

    await show_moderation_warning(user_id)
