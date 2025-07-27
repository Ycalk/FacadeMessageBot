from ...base import MaxObject
from typing import Literal
from .payloads import MediaAttachmentPayload
from pydantic import Field


class VideoThumbnail(MaxObject):
    url: str = Field(..., description="URL to access the video thumbnail")


class VideoAttachment(MaxObject):
    type: Literal["video"] = "video"
    payload: MediaAttachmentPayload
    thumbnail: VideoThumbnail | None = Field(
        None,
        description="Thumbnail of the video attachment, if available. Contains URL to access the thumbnail.",
    )
    width: int | None = Field(
        None, description="Width of the video in pixels, if available."
    )
    height: int | None = Field(
        None, description="Height of the video in pixels, if available."
    )
    duration: int | None = Field(
        None, description="Duration of the video in seconds, if available."
    )
