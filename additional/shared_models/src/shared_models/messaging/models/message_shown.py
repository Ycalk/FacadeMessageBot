from .message_notification import MessageNotification
from typing import Annotated, Optional
from pydantic import Field


class MessageShown(MessageNotification):
    photo_url: Annotated[
        Optional[str],
        Field(None, description="URL of the photo associated with the message shown."),
    ] = None
