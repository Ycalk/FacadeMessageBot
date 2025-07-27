from ...base import MaxObject
from typing import Literal
from .payloads import ShareAttachmentRequestPayload


class ShareAttachmentRequest(MaxObject):
    type: Literal["share"] = "share"
    payload: ShareAttachmentRequestPayload
