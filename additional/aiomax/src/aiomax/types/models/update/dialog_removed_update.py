from .base import UpdateBase
from pydantic import Field
from typing import Literal
from ..user import User


class DialogRemovedUpdate(UpdateBase):
    update_type: Literal["dialog_removed"] = "dialog_removed"
    chat_id: int = Field(..., description="ID of the chat where the dialog was removed")
    user: User = Field(..., description="User who removed the dialog")