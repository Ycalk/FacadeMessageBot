from ..base import MaxObject
from pydantic import Field
from ..enums import ChatType


class Recipient(MaxObject):
    chat_id: int | None = Field(None, description="Unique identifier for the chat")
    chat_type: ChatType = Field(..., description="Type of the chat")
    user_id: int | None = Field(
        None, description="Unique identifier for the user, message was sent to user"
    )
