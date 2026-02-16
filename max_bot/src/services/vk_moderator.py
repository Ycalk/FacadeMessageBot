"""Сервис VK модерации с множественными модераторами."""

from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified

from core.config import Config
from core.logger import get_logger
from db.models import Message, MessageStatus
from db.session import async_session
from services.maer_client import send_to_maer_moderation, MaerAPIError

logger = get_logger(__name__)


async def moderate_by_vk_moderator(message_id: int, moderator_id: str, approve: bool) -> dict:
    """
    Модерация сообщения VK модератором.

    Args:
        message_id: ID сообщения
        moderator_id: ID VK модератора
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
            return {"success": False, "error": "Сообщение не найдено"}

        if message.status != MessageStatus.VK_MODERATION:
            logger.warning(
                f"Сообщение {message_id} не в статусе VK модерации (текущий: {message.status})"
            )
            return {"success": False, "error": "Неверный статус"}

        # Инициализируем meta если его нет
        if not message.meta:
            message.meta = {"vk_approvals": [], "vk_rejections": []}

        # Если отклонение — сразу переводим в rejected
        if not approve:
            if moderator_id not in message.meta.get("vk_rejections", []):
                message.meta.setdefault("vk_rejections", []).append(moderator_id)
                flag_modified(message, "meta")
            message.status = MessageStatus.REJECTED
            await session.commit()
            logger.info(f"Сообщение {message_id} отклонено VK модератором {moderator_id}")

            from api.utils import send_rejection_notification
            await send_rejection_notification(message_id)

            return {
                "success": True,
                "status": "rejected",
                "moderator": moderator_id
            }

        # Если одобрение — добавляем в список одобривших
        if moderator_id not in message.meta.get("vk_approvals", []):
            message.meta.setdefault("vk_approvals", []).append(moderator_id)
            flag_modified(message, "meta")

        # Проверяем, все ли VK модераторы одобрили
        required_moderators = set(Config.vk_moderators_list)
        approved_moderators = set(message.meta.get("vk_approvals", []))

        if required_moderators.issubset(approved_moderators):
            # Все VK модераторы одобрили
            if Config.DEVELOP:
                # В режиме разработки просто переводим в статус maer_moderation
                message.status = MessageStatus.MAER_MODERATION
                await session.commit()
                logger.info(
                    f"Сообщение {message_id} одобрено всеми VK модераторами → "
                    f"MAER_MODERATION (режим разработки, запрос в Maer пропущен)"
                )
            else:
                try:
                    await send_to_maer_moderation(
                        message_id=message.id,
                        name=message.name,
                        city=message.city,
                        text=message.text,
                        layout=message.frame_id or 1,
                    )
                    message.status = MessageStatus.MAER_MODERATION
                    await session.commit()
                    logger.info(
                        f"Сообщение {message_id} одобрено всеми VK модераторами → отправлено в Maer"
                    )
                except MaerAPIError as e:
                    logger.error(
                        f"Ошибка Maer API для сообщения {message_id}: {e}"
                    )
                    await session.commit()
                    return {
                        "success": False,
                        "error": f"Ошибка Maer API: {e}",
                        "moderator": moderator_id,
                        "all_approved": True
                    }

            return {
                "success": True,
                "status": "maer_moderation",
                "moderator": moderator_id,
                "all_approved": True
            }
        else:
            # Ещё не все VK модераторы одобрили
            await session.commit()
            logger.info(
                f"Сообщение {message_id} одобрено VK модератором {moderator_id} "
                f"({len(approved_moderators)}/{len(required_moderators)})"
            )
            return {
                "success": True,
                "status": "vk_moderation",
                "moderator": moderator_id,
                "approved_count": len(approved_moderators),
                "required_count": len(required_moderators),
                "all_approved": False
            }
