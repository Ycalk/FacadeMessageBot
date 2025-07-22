from ...base import MaxObject
from typing import Literal
from .payloads import ShareAttachmentPayload
from pydantic import Field


class ShareAttachment(MaxObject):
    type: Literal["share"] = "share"
    payload: ShareAttachmentPayload
    title: str | None = Field(
        None,
        description="Title of the shared content, if available",
    )
    description: str | None = Field(
        None,
        description="Description of the shared content, if available",
    )
    image_url: str | None = Field(
        None,
        description="URL of an image representing the shared content, if available",
    )
