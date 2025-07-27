from ....base import MaxObject
from pydantic import Field


class ShareAttachmentRequestPayload(MaxObject):
    url: str | None = Field(None, description="The URL of the share attachment")
    token: str | None = Field(None, description="The token of the existing attachment")
