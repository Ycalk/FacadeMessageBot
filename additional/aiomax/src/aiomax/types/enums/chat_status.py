from enum import StrEnum


class ChatStatus(StrEnum):
    """ChatStatus Enum

    Values:
        - ACTIVE: Bot is chat participant
        - REMOVED: Bot is removed from chat
        - LEFT: Bot has left the chat
        - CLOSED: Chat is closed
    """

    ACTIVE = "active"  # Bot is chat participant
    REMOVED = "removed"  # Bot is removed from chat
    LEFT = "left"  # Bot has left the chat
    CLOSED = "closed"  # Chat is closed

    def __str__(self) -> str:
        return self.value
