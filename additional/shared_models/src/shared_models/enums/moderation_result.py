from enum import StrEnum


class ModerationResult(StrEnum):
    """ModerationResult Enum

    Args:
        - REJECTED: Message is rejected.
        - APPROVED: Message is approved.
    """

    REJECTED = "auto"
    APPROVED = "manual"

    def __str__(self) -> str:
        return self.value
