from .base import UpdateBase
from pydantic import Field
from typing import Literal
from ..chat import Chat


class MessageChatCreatedUpdate(UpdateBase):
    update_type: Literal["message_chat_created"] = "message_chat_created"
    chat: Chat = Field(..., description="Created chat object")
    message_id: str = Field(
        ..., description="ID of the message where the button was pressed"
    )
    start_payload: str | None = Field(
        None,
        description="Payload of the button that was pressed to create the chat, if available",
    )
