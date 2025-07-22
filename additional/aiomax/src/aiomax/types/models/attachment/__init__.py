from .payloads import (
    ContactAttachmentPayload,
    FileAttachmentPayload,
    MediaAttachmentPayload,
    PhotoAttachmentPayload,
    ShareAttachmentPayload,
    StickerAttachmentPayload,
)
from .audio_attachment import AudioAttachment
from .contact_attachment import ContactAttachment
from .file_attachment import FileAttachment
from .image_attachment import ImageAttachment
from .inline_keyboard_attachment import InlineKeyboardAttachment
from .location_attachment import LocationAttachment
from .share_attachment import ShareAttachment
from .sticker_attachment import StickerAttachment
from .video_attachment import VideoAttachment, VideoThumbnail

from typing import Annotated, Union
from pydantic import Field

Attachment = Annotated[
    Union[
        AudioAttachment,
        ContactAttachment,
        FileAttachment,
        ImageAttachment,
        InlineKeyboardAttachment,
        LocationAttachment,
        ShareAttachment,
        StickerAttachment,
        VideoAttachment,
    ],
    Field(discriminator="type", description="Type of attachment"),
]

__all__ = [
    "ContactAttachmentPayload",
    "FileAttachmentPayload",
    "MediaAttachmentPayload",
    "PhotoAttachmentPayload",
    "ShareAttachmentPayload",
    "StickerAttachmentPayload",
    "AudioAttachment",
    "ContactAttachment",
    "FileAttachment",
    "ImageAttachment",
    "InlineKeyboardAttachment",
    "LocationAttachment",
    "ShareAttachment",
    "StickerAttachment",
    "VideoAttachment",
    "VideoThumbnail",
    "Attachment",
]
