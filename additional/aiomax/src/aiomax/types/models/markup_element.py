from ..base import MaxObject
from pydantic import Field
from ..enums import MarkupElementType


class MarkupElement(MaxObject):
    type: MarkupElementType = Field(
        ...,
        description="Type of the markup element",
    )
    start_index: int = Field(
        ..., description="Start index of the markup element in the text", alias="from"
    )
    length: int = Field(
        ...,
        description="Length of the markup element in the text",
    )
