from ...base import MaxObject
from pydantic import Field
from ...enums import ChatType, ChatStatus
from ..image import Image
from ..user.user_with_photo import UserWithPhoto
from ..message import Message


class Chat(MaxObject):
    chat_id: int = Field(..., description="Unique identifier for the chat")
    type: ChatType = Field(..., description="Type of the chat")
    status: ChatStatus = Field(..., description="Status of the chat")
    title: str | None = Field(None, description="Title of the chat, if applicable")
    icon: Image | None = Field(None, description="Icon of the chat, if applicable")
    last_event_time: int = Field(
        ..., description="Timestamp of the last event in the chat"
    )
    participants_count: int = Field(
        ..., description="Number of participants in the chat"
    )
    owner_id: int | None = Field(
        None, description="Unique identifier for the owner of the chat, if applicable"
    )
    participants: dict | None = Field(
        None,
        description="Participants with last activity time. None if request was chat list",
    )
    is_public: bool = Field(..., description="Indicates if the chat is public")
    link: str | None = Field(None, description="Link to the chat, if applicable")
    description: str | None = Field(
        None, description="Description of the chat, if applicable"
    )
    dialog_with_user: UserWithPhoto | None = Field(
        None, description="Dialog with user, if chat type is dialog"
    )
    messages_count: int | None = Field(
        None,
        description="Number of messages in the chat, applicable only for group chats",
    )
    chat_message_id: int | None = Field(
        None,
        description="The ID of the message containing the button through which the chat was initiated",
    )
    pinned_message: Message | None = Field(
        None,
        description="The pinned message in the chat. Returned only when a specific chat is requested",
    )
