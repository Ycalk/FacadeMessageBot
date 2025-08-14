from pydantic import BaseModel, Field
from shared_models.messaging import Message
from typing import Self


class AddMessage(BaseModel):
    id: int = Field(..., description="ID сообщения")
    name: str = Field(..., description="Имя отправителя")
    city: str = Field(..., description="Город отправителя")
    text: str = Field(..., description="Текст сообщения")

    @classmethod
    def from_message(cls, message: Message) -> Self:
        return cls(
            id=message.message_id,
            name=message.name,
            city=message.city,
            text=message.text,
        )
