from .base import UpdateBase
from pydantic import Field
from typing import Literal
from ..user import User


class BotAddedUpdate(UpdateBase):
    update_type: Literal["bot_added"] = "bot_added"
    chat_id: int = Field(..., description="ID of the chat where the bot was added")
    user: User = Field(..., description="User who added the bot")
    is_channel: bool = Field(
        ..., description="True if the bot was added to a channel, False if to a group"
    )
