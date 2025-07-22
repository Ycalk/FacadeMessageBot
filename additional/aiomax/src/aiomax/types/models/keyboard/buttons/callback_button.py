from .base import KeyboardButtonBase
from typing import Literal
from pydantic import Field, field_validator
from ....enums import ButtonIntent


class CallbackButton(KeyboardButtonBase):
    type: Literal["callback"] = "callback"
    payload: str = Field(..., description="Button token")
    intent: ButtonIntent = Field(ButtonIntent.DEFAULT, description="Button intent")

    @field_validator("payload")
    @classmethod
    def validate_payload(cls, value: str) -> str:
        if len(value) > 1024:
            raise ValueError("Payload must be 1024 characters or less")
        return value
