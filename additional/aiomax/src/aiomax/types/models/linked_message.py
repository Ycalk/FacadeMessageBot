from ..base import MaxObject
from pydantic import Field
from ..enums import MessageLinkType
from .user import User
from .message_body import MessageBody


class LinkedMessage(MaxObject):
    type: MessageLinkType = Field(
        ...,
        description="Type of the linked message",
    )
    sender: User | None = Field(
        None,
        description="User who sent the linked message",
    )
    chat_id: int | None = Field(
        None,
        description="ID of the chat where the linked message was sent",
    )
    message: MessageBody
