from .base import UpdateBase
from pydantic import Field
from typing import Literal
from ..user import User


class DialogClearedUpdate(UpdateBase):
    update_type: Literal["dialog_cleared"] = "dialog_cleared"
    chat_id: int = Field(..., description="ID of the chat where the dialog was cleared")
    user: User = Field(..., description="User who cleared the dialog")