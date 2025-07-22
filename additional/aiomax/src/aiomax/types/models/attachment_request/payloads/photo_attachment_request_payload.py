from ....base import MaxObject
from pydantic import Field


class PhotoAttachmentRequestPayload(MaxObject):
    url: str | None = Field(None, description="The URL of the photo attachment")
    token: str | None = Field(None, description="The token of existing attachment")
    photos: list[str] | None = Field(None, description="List of photo tokens")
