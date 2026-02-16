from datetime import datetime
from enum import StrEnum

from sqlalchemy import ForeignKey, func, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class MessageStatus(StrEnum):
    """Статусы обработки сообщения."""
    CREATED = "created"                            # Создано
    AUTO_MODERATION = "auto_moderation"            # Автоматическая модерация
    INTERNAL_MODERATION = "internal_moderation"    # На внутренней модерации
    EXTERNAL_MODERATION = "external_moderation"    # На внешней модерации
    APPROVED = "approved"                          # Одобрено модератором
    REJECTED = "rejected"                          # Отклонено модератором
    SHOWN_ON_FACADE = "shown_on_facade"            # Показано на фасаде
    PHOTO_SENT = "photo_sent"                      # Фото фасада отправлено пользователю


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    max_id: Mapped[int] = mapped_column(unique=True)
    first_name: Mapped[str | None]
    username: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    messages: Mapped[list["Message"]] = relationship(back_populates="user")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str]
    name: Mapped[str]
    city: Mapped[str]
    frame_id: Mapped[int | None]
    image_url: Mapped[str | None]  # Presigned URL фото от пользователя в MinIO
    status: Mapped[str] = mapped_column(default=MessageStatus.CREATED)
    meta: Mapped[dict | None] = mapped_column(JSON, default=dict)  # Метаданные модерации
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="messages")
