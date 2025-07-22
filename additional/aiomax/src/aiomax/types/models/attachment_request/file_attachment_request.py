from ...base import MaxObject
from typing import Literal
from .payloads import UploadedInfo


class FileAttachmentRequest(MaxObject):
    type: Literal["file"] = "file"
    payload: UploadedInfo
