from ...base import MaxObject
from typing import Literal
from .payloads import UploadedInfo


class AudioAttachmentRequest(MaxObject):
    type: Literal["audio"] = "audio"
    payload: UploadedInfo
