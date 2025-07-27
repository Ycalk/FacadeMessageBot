from ...base import MaxObject
from pydantic import Field
from .chat import Chat


class ChatList(MaxObject):
    chats: list[Chat] = Field(
        ...,
        description="List of chats",
    )
    marker: int | None = Field(
        None,
        description="Marker for pagination, used to fetch the next set of chats",
    )
