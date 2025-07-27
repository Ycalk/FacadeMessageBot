from .base import UpdateBase
from pydantic import Field
from ..message import Message
from typing import Literal


class MessageCreatedUpdate(UpdateBase):
    update_type: Literal["message_created"] = "message_created"
    message: Message = Field(
        ...,
        description="Message that was created",
    )
    user_locale: str | None = Field(
        None,
        description="Locale of the user who created the message",
    )
