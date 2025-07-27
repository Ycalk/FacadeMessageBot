from ..base import MaxObject
from pydantic import Field, field_validator


class BotCommand(MaxObject):
    name: str = Field(
        ...,
        description="The name of the command, 1-32 characters. Can contain only lowercase letters, digits and underscores.",
    )
    description: str | None = Field(
        None,
        description="Description of the command, 1-128 characters. Can contain any characters.",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value.islower():
            raise ValueError("Command name must be lowercase.")
        if len(value) < 1 or len(value) > 32:
            raise ValueError("Command name must be between 1 and 32 characters long.")
        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if value is not None and (len(value) < 1 or len(value) > 128):
            raise ValueError("Description must be between 1 and 128 characters long.")
        return value
