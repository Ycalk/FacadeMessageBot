from ...base import MaxObject
from typing import Literal
from .payloads import UploadedInfo


class VideoAttachmentRequest(MaxObject):
    type: Literal["video"] = "video"
    payload: UploadedInfo
