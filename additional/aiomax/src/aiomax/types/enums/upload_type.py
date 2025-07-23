from enum import StrEnum


class UploadType(StrEnum):
    """UploadType Enum

    Values:
        - IMAGE
        - VIDEO
        - AUDIO
        - FILE
    """

    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"

    def __str__(self) -> str:
        return self.value
