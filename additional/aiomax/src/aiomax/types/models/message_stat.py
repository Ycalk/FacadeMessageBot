from ..base import MaxObject
from pydantic import Field


class MessageStat(MaxObject):
    views: int = Field(
        ...,
        description="Number of views for the message",
    )
