from .base import UpdateBase
from pydantic import Field
from typing import Literal
from ..user import User


class BotRemovedUpdate(UpdateBase):
    update_type: Literal["bot_removed"] = "bot_removed"
    chat_id: int = Field(..., description="ID of the chat where the bot was removed")
    user: User = Field(..., description="User who removed the bot")
    is_channel: bool = Field(
        ...,
        description="True if the bot was removed from a channel, False if from a group",
    )
