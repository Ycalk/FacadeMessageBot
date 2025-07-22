from ..base import MaxObject
from pydantic import Field
from .attachment import Attachment
from .markup_element import MarkupElement


class MessageBody(MaxObject):
    mid: str = Field(..., description="Unique identifier for the message")
    seq: int = Field(..., description="Message sequence ID")
    text: str | None = Field(..., description="Text of the message")
    attachments: list[Attachment] | None = Field(
        ..., description="List of attachments in the message"
    )
    markup: list[MarkupElement] | None = Field(
        ..., description="List of markup elements in the message"
    )
