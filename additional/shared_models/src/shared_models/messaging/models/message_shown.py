from .message_input import MessageInput
from typing import Annotated, Optional
from pydantic import Field


class MessageShown(MessageInput):
    photo_url: Annotated[
        Optional[str],
        Field(None, description="URL of the photo associated with the message shown."),
    ] = None
