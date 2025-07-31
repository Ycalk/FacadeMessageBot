import importlib

try:
    importlib.import_module("tortoise")
    importlib.import_module("aerich")
except ImportError:
    raise RuntimeError(
        "To use database, install package with [database] or [full] extra."
    )


from .models import Media, Message, ModerationLog, User
from .config import get_tortoise_orm_config, TORTOISE_ORM_FROM_ENV


__all__ = [
    "Media",
    "Message",
    "ModerationLog",
    "User",
    "get_tortoise_orm_config",
    "TORTOISE_ORM_FROM_ENV",
]
