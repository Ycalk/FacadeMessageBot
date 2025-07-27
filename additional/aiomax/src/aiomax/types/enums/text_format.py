from enum import StrEnum


class TextFormat(StrEnum):
    """TextFormat Enum

    Values:
        - MARKDOWN
        - HTML
    """

    MARKDOWN = "markdown"
    HTML = "html"

    def __str__(self) -> str:
        return self.value
