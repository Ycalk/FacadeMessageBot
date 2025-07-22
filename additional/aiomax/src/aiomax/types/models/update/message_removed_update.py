from .base import UpdateBase
from pydantic import Field
from typing import Literal


class MessageRemovedUpdate(UpdateBase):
    update_type: Literal["message_removed"] = "message_removed"
    message_id: str = Field(..., description="ID of the message that was removed")
    chat_id: int = Field(
        ..., description="ID of the chat where the message was removed"
    )
    user_id: int = Field(..., description="ID of the user who removed the message")
