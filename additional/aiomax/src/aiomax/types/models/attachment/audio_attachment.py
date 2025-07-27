from ...base import MaxObject
from typing import Literal
from .payloads import MediaAttachmentPayload
from pydantic import Field


class AudioAttachment(MaxObject):
    type: Literal["audio"] = "audio"
    payload: MediaAttachmentPayload
    transcription: str | None = Field(
        None, description="Transcription of the audio content"
    )
