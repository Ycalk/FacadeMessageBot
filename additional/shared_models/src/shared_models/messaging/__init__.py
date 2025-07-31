import importlib

try:
    importlib.import_module("faststream")
except ImportError:
    raise RuntimeError(
        "To use messaging, install package with [messaging] or [full] extra."
    )

from .models import (
    Message,
    MessageNotification,
    MessageShown,
    ModerationResult,
    NoAvailableTime,
)
from .queues import (
    auto_moderator_queue,
    auto_moderator_dlx_queue,
    facade_message_moderator_queue,
    facade_message_moderator_dlx_queue,
    manual_moderator_queue,
    manual_moderator_dlx_queue,
    vision_notification_queue,
    vision_notification_dlx_queue,
)
from .exchanges import moderator_exchange, dlx_exchange, vision_exchange


__all__ = [
    "Message",
    "MessageNotification",
    "MessageShown",
    "ModerationResult",
    "NoAvailableTime",
    "auto_moderator_queue",
    "auto_moderator_dlx_queue",
    "facade_message_moderator_queue",
    "facade_message_moderator_dlx_queue",
    "manual_moderator_queue",
    "manual_moderator_dlx_queue",
    "vision_notification_queue",
    "vision_notification_dlx_queue",
    "moderator_exchange",
    "dlx_exchange",
    "vision_exchange",
]
