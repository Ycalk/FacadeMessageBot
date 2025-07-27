from ....base import MaxObject
from pydantic import Field, field_validator


class ShareAttachmentPayload(MaxObject):
    url: str | None = Field(None, description="The URL of the shared attachment")
    token: str | None = Field(None, description="The token of the shared attachment")

    @field_validator("url")
    def validate_url(cls, value: str | None) -> str | None:
        if value is not None and len(value) < 1:
            raise ValueError("URL must be at least 1 character long")
        return value
