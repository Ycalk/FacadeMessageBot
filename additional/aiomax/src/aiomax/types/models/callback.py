from ..base import MaxObject, UNSET, UNSET_TYPE
from pydantic import Field
from .user import User


class Callback(MaxObject):
    timestamp: int = Field(
        ..., description="Timestamp of the callback in milliseconds since epoch"
    )
    callback_id: str = Field(..., description="Current keyboard ID")
    payload: str | UNSET_TYPE = Field(UNSET, description="Button token")
    user: User = Field(..., description="User who clicked the button")
