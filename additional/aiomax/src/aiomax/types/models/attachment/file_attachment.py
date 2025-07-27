from ...base import MaxObject
from typing import Literal
from .payloads import FileAttachmentPayload
from pydantic import Field


class FileAttachment(MaxObject):
    type: Literal["file"] = "file"
    payload: FileAttachmentPayload
    filename: str = Field(
        ...,
        description="Name of the file, including extension",
    )
    size: int = Field(
        ...,
        description="Size of the file in bytes",
    )
