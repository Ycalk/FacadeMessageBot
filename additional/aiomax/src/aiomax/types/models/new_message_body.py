from ..base import MaxObject
from pydantic import Field
from .attachment_request import AttachmentRequest
from ..enums import TextFormat


class NewMessageBody(MaxObject):
    text: str | None = Field(None, description="The text of the message")
    attachments: list[AttachmentRequest] | None = Field(
        None, description="List of attachments in the message"
    )
    notify: bool = Field(
        True, description="Whether to notify the user about the message"
    )
    format: TextFormat | None = Field(
        None, description="Format of the text in the message"
    )
