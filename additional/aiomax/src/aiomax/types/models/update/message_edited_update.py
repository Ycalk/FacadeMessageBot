from .base import UpdateBase
from pydantic import Field
from ..message import Message
from typing import Literal


class MessageEditedUpdate(UpdateBase):
    update_type: Literal["message_edited"] = "message_edited"
    message: Message = Field(..., description="Message that was edited")
