from .message_notification import MessageNotification
from typing import Annotated, Literal
from pydantic import Field


class NoAvailableTime(MessageNotification):
    exception: Annotated[
        Literal["no_available_time"],
        Field(
            description="Exception type indicating no available time for the message."
        ),
    ] = "no_available_time"
