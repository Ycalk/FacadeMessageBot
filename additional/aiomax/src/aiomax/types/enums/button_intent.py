from enum import StrEnum


class ButtonIntent(StrEnum):
    """ButtonIntent Enum

    Values:
        - DEFAULT: Default button intent
        - POSITIVE: Positive button intent
        - NEGATIVE: Negative button intent
    """

    DEFAULT = "default"
    POSITIVE = "positive"
    NEGATIVE = "negative"

    def __str__(self) -> str:
        return self.value
