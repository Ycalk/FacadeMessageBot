from ...base import MaxObject
from typing import Literal
from .payloads import StickerAttachmentRequestPayload


class StickerAttachmentRequest(MaxObject):
    type: Literal["sticker"] = "sticker"
    payload: StickerAttachmentRequestPayload
