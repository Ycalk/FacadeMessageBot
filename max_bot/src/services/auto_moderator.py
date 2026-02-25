"""Вспомогательные функции автоодобрения модераторами."""

from core.config import Config
from core.logger import get_logger

logger = get_logger(__name__)


async def apply_auto_approvals(message_id: int) -> None:
    """Применяет автоодобрения от модераторов с включённым автоапрувом."""
    from services.app_settings import get_auto_approve_moderators
    from services.internal_moderator import moderate_by_moderator

    auto_mods = await get_auto_approve_moderators()
    if not auto_mods:
        return

    for mod_id in auto_mods:
        if mod_id in Config.moderators_list:
            result = await moderate_by_moderator(message_id, mod_id, True)
            if result.get("success"):
                logger.info(f"Автоодобрение сообщения {message_id} модератором {mod_id!r}")
