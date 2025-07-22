from .base import KeyboardButtonBase
from typing import Literal
from pydantic import Field, field_validator


class LinkButton(KeyboardButtonBase):
    type: Literal["link"] = "link"
    url: str = Field(..., description="URL to open when the button is clicked")

    @field_validator("url")
    def validate_url(cls, value: str) -> str:
        if len(value) > 2048:
            raise ValueError("URL length must not exceed 2048 characters")
        return value
