from enum import StrEnum


class MessageLinkType(StrEnum):
    """MessageLinkType Enum

    Values:
        - FORWARD
        - REPLY
    """

    FORWARD = "forward"
    REPLY = "reply"

    def __str__(self) -> str:
        return self.value
