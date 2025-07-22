from ....base import MaxObject
from pydantic import Field


class FileAttachmentPayload(MaxObject):
    url: str = Field(..., description="URL to access the photo attachment")
    token: str = Field(
        ...,
        description="Use token if you are trying to reuse the same attachment in another message",
    )
