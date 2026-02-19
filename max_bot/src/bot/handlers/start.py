from typing import Union
from core.logger import get_logger

from maxapi.types import BotStarted, MessageCreated

from bot.steps import show_start

logger = get_logger(__name__)


async def start_handler(event: Union[BotStarted, MessageCreated]) -> None:
    user_id = (
        event.user.user_id
        if hasattr(event, "user")
        else event.message.sender.user_id
    )
    await show_start(user_id)
