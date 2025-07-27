from enum import StrEnum


class ChatType(StrEnum):
    """ChatType Enum

    Values:
        - CHAT: Group chat.
    """

    CHAT = "chat"
    DIALOG = "dialog"

    def __str__(self) -> str:
        return self.value
