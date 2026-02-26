from datetime import datetime
from enum import StrEnum

from sqlalchemy import ForeignKey, Text, func, JSON, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class MessageStatus(StrEnum):
    """Статусы обработки сообщения."""
    INTERNAL_MODERATION = "internal_moderation"    # На внутренней модерации
    VK_MODERATION = "vk_moderation"                # На VK модерации
    MAER_MODERATION = "maer_moderation"            # На модерации Maer
    APPROVED = "approved"                          # Одобрено модератором
    REJECTED = "rejected"                          # Отклонено модератором


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
    message_input_logs: Mapped[list["MessageInputLog"]] = relationship(back_populates="user")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str]
    name: Mapped[str]
    city: Mapped[str]
    frame_id: Mapped[int | None]
    status: Mapped[str] = mapped_column(default=MessageStatus.INTERNAL_MODERATION)
    shown_on_facade: Mapped[bool] = mapped_column(default=False, server_default=text("false"))  # Был показ на фасаде
    photo_sent: Mapped[bool] = mapped_column(default=False, server_default=text("false"))  # Фото отправлено пользователю
    reminder_sent: Mapped[bool] = mapped_column(default=False, server_default=text("false"))  # Напоминание о показе отправлено
    want_photo: Mapped[bool | None]               # Хочет ли получить фото фасада (None = не ответил)
    preview_url: Mapped[str | None]               # URL сгенерированного превью на фоне
    meta: Mapped[dict | None] = mapped_column(JSON, default=dict)  # Метаданные модерации
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="messages")


class MessageInputLog(Base):
    """Лог пользовательских сообщений на шаге ввода поздравления."""
    __tablename__ = "message_input_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    raw_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="message_input_logs")


class BlacklistWord(Base):
    __tablename__ = "blacklist_words"

    id: Mapped[int] = mapped_column(primary_key=True)
    word: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class AppSetting(Base):
    """Хранилище настроек приложения (ключ-значение)."""
    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(default="")
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
