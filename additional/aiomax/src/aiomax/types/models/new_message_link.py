from ..base import MaxObject
from pydantic import Field
from ..enums import MessageLinkType


class NewMessageLink(MaxObject):
    type: MessageLinkType = Field(..., description="Type of the link")
    mid: str = Field(..., description="Message ID")
