from .payloads import (
    ContactAttachmentRequestPayload,
    PhotoAttachmentRequestPayload,
    ShareAttachmentRequestPayload,
    StickerAttachmentRequestPayload,
    UploadedInfo,
)
from .audio_attachment_request import AudioAttachmentRequest
from .contact_attachment_request import ContactAttachmentRequest
from .file_attachment_request import FileAttachmentRequest
from .image_attachment_request import ImageAttachmentRequest
from .inline_keyboard_attachment_request import InlineKeyboardAttachmentRequest
from .location_attachment_request import LocationAttachmentRequest
from .share_attachment_request import ShareAttachmentRequest
from .sticker_attachment_request import StickerAttachmentRequest
from .video_attachment_request import VideoAttachmentRequest

from typing import Annotated, Union
from pydantic import Field

AttachmentRequest = Annotated[
    Union[
        AudioAttachmentRequest,
        ContactAttachmentRequest,
        FileAttachmentRequest,
        ImageAttachmentRequest,
        InlineKeyboardAttachmentRequest,
        LocationAttachmentRequest,
        ShareAttachmentRequest,
        StickerAttachmentRequest,
        VideoAttachmentRequest,
    ],
    Field(discriminator="type", description="Type of attachment request"),
]

__all__ = [
    "AttachmentRequest",
    "AudioAttachmentRequest",
    "ContactAttachmentRequest",
    "FileAttachmentRequest",
    "ImageAttachmentRequest",
    "InlineKeyboardAttachmentRequest",
    "LocationAttachmentRequest",
    "ShareAttachmentRequest",
    "StickerAttachmentRequest",
    "VideoAttachmentRequest",
    "ContactAttachmentRequestPayload",
    "PhotoAttachmentRequestPayload",
    "ShareAttachmentRequestPayload",
    "StickerAttachmentRequestPayload",
    "UploadedInfo",
]
