from ...base import MaxObject
from typing import Literal
from .payloads import PhotoAttachmentPayload


class ImageAttachment(MaxObject):
    type: Literal["image"] = "image"
    payload: PhotoAttachmentPayload
