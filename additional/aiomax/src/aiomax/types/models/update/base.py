from ...base import MaxObject
from pydantic import Field
from abc import ABC


class UpdateBase(MaxObject, ABC):
    update_type: str
    timestamp: int = Field(
        ...,
        description="The time when the update was created, in milliseconds since the epoch",
    )
