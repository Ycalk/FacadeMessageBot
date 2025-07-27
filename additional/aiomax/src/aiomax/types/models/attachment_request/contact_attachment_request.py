from ...base import MaxObject
from typing import Literal
from .payloads import ContactAttachmentRequestPayload


class ContactAttachmentRequest(MaxObject):
    type: Literal["contact"] = "contact"
    payload: ContactAttachmentRequestPayload
