"""Pydantic схемы для API endpoints."""

from datetime import datetime
from pydantic import BaseModel


class ModerateRequest(BaseModel):
    """Запрос на модерацию от конкретного модератора."""
    message_id: int
    moderator_id: str
    approve: bool


class MessageShownRequest(BaseModel):
    """Webhook когда сообщение показано на экране."""
    message_id: int
    frame_url: str  # URL на фото фасада


class MessageModeratedRequest(BaseModel):
    """
    Webhook от Maer API с результатом модерации.

    status:
        0 - на модерации
        1 - модерация завершена успешно
        2 - отклонён (причина в поле reason)
    """
    id: int  # ID сообщения
    status: int  # 0, 1, 2
    reason: str | None = None  # Причина отклонения (опционально)


class MessageShownOnFacadeRequest(BaseModel):
    """
    Webhook от Maer API о показе сообщения на фасаде.

    type:
        1 - shown (показано на фасаде)
    """
    id: int  # ID сообщения
    type: int  # 1 = shown


class MessageResponse(BaseModel):
    """Ответ со списком сообщений."""
    id: int
    user_id: int
    text: str
    name: str
    city: str
    frame_id: int | None
    status: str
    want_photo: bool | None
    preview_url: str | None
    created_at: datetime

    class Config:
        from_attributes = True
