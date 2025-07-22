from ...base import MaxObject
from typing import Literal
from .payloads import ContactAttachmentPayload


class ContactAttachment(MaxObject):
    type: Literal["contact"] = "contact"
    payload: ContactAttachmentPayload
