from .message_notification import MessageNotification
from typing import Annotated
from pydantic import Field


class NoAvailableTime(MessageNotification):
    stop_message_collecting: Annotated[
        bool,
        Field(description="Indicates whether message collecting should be stopped."),
    ]
