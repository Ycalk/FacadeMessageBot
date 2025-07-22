from .base import UpdateBase
from ...base import UNSET, UNSET_TYPE
from pydantic import Field
from typing import Literal
from ..user import User


class UserRemovedUpdate(UpdateBase):
    update_type: Literal["user_removed"] = "user_removed"
    chat_id: int = Field(..., description="ID of the chat where the user was removed")
    user: User = Field(..., description="User who was removed")
    admin_id: int | UNSET_TYPE = Field(
        UNSET, description="ID of the admin who removed the new user, if available"
    )
    is_channel: bool = Field(
        ..., description="True if the user was added to a channel, False if to a group"
    )
