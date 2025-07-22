from .base import UpdateBase
from pydantic import Field
from typing import Literal
from ..user import User


class ChatTitleChangedUpdate(UpdateBase):
    update_type: Literal["chat_title_changed"] = "chat_title_changed"
    chat_id: int = Field(..., description="ID of the chat where the title was changed")
    user: User = Field(..., description="User who changed the chat title")
    title: str = Field(..., description="New title of the chat")
