"""Сервис внутренней модерации с множественными модераторами."""

from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified

from core.config import Config
from core.logger import get_logger
from db.models import Message, MessageStatus
from db.session import async_session

logger = get_logger(__name__)


async def moderate_by_moderator(message_id: int, moderator_id: str, approve: bool) -> dict:
    """
    Модерация сообщения конкретным модератором.

    Args:
        message_id: ID сообщения
        moderator_id: ID модератора
        approve: True для одобрения, False для отклонения

    Returns:
        dict с результатом модерации
    """
    async with async_session() as session:
        result = await session.execute(
            select(Message).where(Message.id == message_id)
        )
        message = result.scalar_one_or_none()

        if not message:
            logger.error(f"Сообщение {message_id} не найдено")
            return {"success": False, "error": "Message not found"}

        if message.status != MessageStatus.INTERNAL_MODERATION:
            logger.warning(
                f"Сообщение {message_id} не в статусе внутренней модерации (текущий: {message.status})"
            )
            return {"success": False, "error": "Invalid status"}

        # Инициализируем meta если его нет
        if not message.meta:
            message.meta = {"approvals": [], "rejections": []}

        # Если отклонение - сразу переводим в rejected
        if not approve:
            if moderator_id not in message.meta.get("rejections", []):
                message.meta.setdefault("rejections", []).append(moderator_id)
                flag_modified(message, "meta")
            message.status = MessageStatus.REJECTED
            await session.commit()
            logger.info(f"Сообщение {message_id} отклонено модератором {moderator_id}")

            from api.utils import send_rejection_notification
            await send_rejection_notification(message_id)

            return {
                "success": True,
                "status": "rejected",
                "moderator": moderator_id
            }

        # Если одобрение - добавляем в список одобривших
        if moderator_id not in message.meta.get("approvals", []):
            message.meta.setdefault("approvals", []).append(moderator_id)
            flag_modified(message, "meta")

        # Проверяем, все ли модераторы одобрили
        required_moderators = set(Config.moderators_list)
        approved_moderators = set(message.meta.get("approvals", []))

        if required_moderators.issubset(approved_moderators):
            # Все одобрили — переходим к VK модерации
            message.meta["vk_entered"] = True
            flag_modified(message, "meta")
            message.status = MessageStatus.VK_MODERATION
            await session.commit()
            logger.info(
                f"Сообщение {message_id} одобрено всеми модераторами → VK модерация"
            )

            return {
                "success": True,
                "status": "vk_moderation",
                "moderator": moderator_id,
                "all_approved": True
            }
        else:
            # Ещё не все одобрили
            await session.commit()
            logger.info(
                f"Сообщение {message_id} одобрено модератором {moderator_id} "
                f"({len(approved_moderators)}/{len(required_moderators)})"
            )
            return {
                "success": True,
                "status": "internal_moderation",
                "moderator": moderator_id,
                "approved_count": len(approved_moderators),
                "required_count": len(required_moderators),
                "all_approved": False
            }
