from ...base import MaxObject
from typing import Literal
from .payloads import StickerAttachmentPayload
from pydantic import Field


class StickerAttachment(MaxObject):
    type: Literal["sticker"] = "sticker"
    payload: StickerAttachmentPayload
    width: int = Field(
        ...,
        description="Width of the sticker in pixels",
    )
    height: int = Field(
        ...,
        description="Height of the sticker in pixels",
    )
