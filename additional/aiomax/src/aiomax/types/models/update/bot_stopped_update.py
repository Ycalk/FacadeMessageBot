from .base import UpdateBase
from pydantic import Field
from typing import Literal
from ..user import User
from ...base import UNSET, UNSET_TYPE


class BotStoppedUpdate(UpdateBase):
    update_type: Literal["bot_stopped"] = "bot_stopped"
    chat_id: int = Field(..., description="ID of the chat where the bot was stopped")
    user: User = Field(..., description="User who press start button")
    user_locale: str | UNSET_TYPE = Field(
        UNSET, description="Locale of the user who started the bot, if available"
    )
