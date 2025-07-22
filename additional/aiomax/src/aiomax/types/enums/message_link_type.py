from enum import StrEnum


class MessageLinkType(StrEnum):
    """MessageLinkType Enum

    Values:
        - FORWARD
        - REPLY
    """

    FORWARD = "forward"
    REPLY = "reply"
