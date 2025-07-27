from .base import UpdateBase
from pydantic import Field
from typing import Literal
from ..user import User
from ...base import UNSET, UNSET_TYPE


class BotStartedUpdate(UpdateBase):
    update_type: Literal["bot_started"] = "bot_started"
    chat_id: int = Field(..., description="ID of the chat where the bot was started")
    user: User = Field(..., description="User who press start button")
    payload: str | None = Field(None, description="Additional data from link, if any")
    user_locale: str | UNSET_TYPE = Field(
        UNSET, description="Locale of the user who started the bot, if available"
    )
