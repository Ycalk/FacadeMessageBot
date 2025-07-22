from ....base import MaxObject
from pydantic import Field


class StickerAttachmentPayload(MaxObject):
    url: str = Field(..., description="URL to access the photo attachment")
    code: str = Field(..., description="Sticker ID")
