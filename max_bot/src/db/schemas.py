from datetime import datetime

from pydantic import BaseModel


class UserRead(BaseModel):
    id: int
    max_id: int
    first_name: str | None
    username: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageRead(BaseModel):
    id: int
    text: str
    name: str
    city: str
    preview_url: str | None
    shown_on_facade: bool
    photo_sent: bool
    created_at: datetime

    model_config = {"from_attributes": True}
