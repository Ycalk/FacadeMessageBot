from .message_input import MessageInput
from typing import Annotated, Literal
from pydantic import Field


class NoAvailableTime(MessageInput):
    exception: Annotated[
        Literal["no_available_time"],
        Field(
            description="Exception type indicating no available time for the message."
        ),
    ] = "no_available_time"
