from ....base import MaxObject
from pydantic import Field


class StickerAttachmentRequestPayload(MaxObject):
    code: str = Field(..., description="Sticker code")
