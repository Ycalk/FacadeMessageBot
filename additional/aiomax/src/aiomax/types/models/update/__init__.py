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
    ],
    Field(discriminator="type", description="Type of attachment"),
]

__all__ = [
    "Update",
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
]
