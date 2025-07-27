from .base import UpdateBase
from pydantic import Field
from ..message import Message
from ..callback import Callback
from typing import Literal


class MessageCallbackUpdate(UpdateBase):
    update_type: Literal["message_callback"] = "message_callback"
    callback: Callback = Field(..., description="Callback data from the message")
    message: Message | None = Field(
        None,
        description="Message that triggered the callback",
    )
    user_locale: str | None = Field(
        None, description="Locale of the user who triggered the callback"
    )
