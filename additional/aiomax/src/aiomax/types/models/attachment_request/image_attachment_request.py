from ...base import MaxObject
from typing import Literal
from .payloads import PhotoAttachmentRequestPayload


class ImageAttachmentRequest(MaxObject):
    type: Literal["image"] = "image"
    payload: PhotoAttachmentRequestPayload
