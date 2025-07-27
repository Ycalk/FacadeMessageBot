from ....base import MaxObject
from pydantic import Field, field_validator
from abc import ABC


class KeyboardButtonBase(MaxObject, ABC):
    type: str
    text: str = Field(..., description="Button text")

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        if len(value) < 1 or len(value) > 128:
            raise ValueError("Text must be between 1 and 128 characters long")
        return value
