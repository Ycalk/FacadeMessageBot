from enum import StrEnum


class MarkupElementType(StrEnum):
    """MarkupElementType Enum

    Values:
        - STRONG
        - EMPHASIZED
        - MONOSPACED
        - LINK
        - STRIKETHROUGH
        - UNDERLINE
        - USER_MENTION
        - HEADING
        - HIGHLIGHTED
    """

    STRONG = "strong"
    EMPHASIZED = "emphasized"
    MONOSPACED = "monospaced"
    LINK = "link"
    STRIKETHROUGH = "strikethrough"
    UNDERLINE = "underline"
    USER_MENTION = "user_mention"
    HEADING = "heading"
    HIGHLIGHTED = "highlighted"

    def __str__(self) -> str:
        return self.value
