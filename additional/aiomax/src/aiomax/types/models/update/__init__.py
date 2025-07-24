from .bot_added_update import BotAddedUpdate
from .bot_removed_update import BotRemovedUpdate
from .bot_started_update import BotStartedUpdate
from .chat_title_changed_update import ChatTitleChangedUpdate
from .message_callback_update import MessageCallbackUpdate
from .message_chat_created_update import MessageChatCreatedUpdate
from .message_created_update import MessageCreatedUpdate
from .message_edited_update import MessageEditedUpdate
from .message_removed_update import MessageRemovedUpdate
from .user_added_update import UserAddedUpdate
from .user_removed_update import UserRemovedUpdate
from .bot_stopped_update import BotStoppedUpdate

from ...base import MaxObject
from typing import Annotated, Union
from pydantic import Field

Update = Annotated[
    Union[
        BotAddedUpdate,
        BotRemovedUpdate,
        BotStartedUpdate,
        ChatTitleChangedUpdate,
        MessageCallbackUpdate,
        MessageChatCreatedUpdate,
        MessageCreatedUpdate,
        MessageEditedUpdate,
        MessageRemovedUpdate,
        UserAddedUpdate,
        UserRemovedUpdate,
        BotStoppedUpdate,
    ],
    Field(discriminator="update_type", description="Type of attachment"),
]


class UpdateList(MaxObject):
    updates: list[Update] = Field(
        ...,
        description="List of updates",
    )
    marker: int | None = Field(
        None,
        description="Marker for the next batch of updates. If not provided, it means there are no more updates.",
    )


__all__ = [
    "Update",
    "UpdateList",
    "BotAddedUpdate",
    "BotRemovedUpdate",
    "BotStartedUpdate",
    "ChatTitleChangedUpdate",
    "MessageCallbackUpdate",
    "MessageChatCreatedUpdate",
    "MessageCreatedUpdate",
    "MessageEditedUpdate",
    "MessageRemovedUpdate",
    "UserAddedUpdate",
    "UserRemovedUpdate",
    "BotStoppedUpdate",
]
