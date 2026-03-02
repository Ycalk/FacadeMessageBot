"""Webhooks для интеграции с Maer API."""

from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from core.logger import get_logger
from api.schemas import AcceptingMessagesRequest, MessageModeratedRequest, MessageShownOnFacadeRequest
from api.auth import verify_api_token
from api.utils import notify_user_moderation_result
from db.models import Message, MessageStatus
from db.session import async_session
from services.app_settings import set_accepting_messages


logger = get_logger(__name__)

router = APIRouter(prefix="/maer", dependencies=[verify_api_token])


@router.put("/accepting")
async def set_accepting(request: AcceptingMessagesRequest):
    """Включает или отключает приём сообщений от пользователей."""
    await set_accepting_messages(request.accepting)
    state = "включён" if request.accepting else "отключён"
    logger.info(f"Приём сообщений {state}")
    return {"status": "ok", "accepting": request.accepting}


@router.post("/moderated")
async def message_moderated(request: MessageModeratedRequest):
    """
    Webhook от Maer API с результатом модерации.

    Вызывается Maer после завершения модерации.

    status: 0 - на модерации, 1 - успешно, 2 - отклонён
    """
    try:
        should_notify_approved = False
        should_notify_rejected = False

        async with async_session() as session:
            result = await session.execute(
                select(Message).where(Message.id == request.id)
            )
            message = result.scalar_one_or_none()

            if not message:
                logger.error(f"Сообщение {request.id} не найдено для обработки webhook")
                raise HTTPException(status_code=404, detail="Сообщение не найдено")

            if request.planned_show_at is not None:
                message.planned_show_at = request.planned_show_at

            if request.status in {1, 2} and message.status != MessageStatus.MAER_MODERATION:
                logger.warning(
                    f"Игнорируем /maer/moderated для сообщения {request.id}: "
                    f"ожидали статус {MessageStatus.MAER_MODERATION}, текущий {message.status}"
                )
                return {"status": "ignored", "reason": "message_not_in_maer_moderation"}

            # Обработка статуса от Maer
            if request.status == 0:
                # На модерации - не обновляем статус
                await session.commit()
                logger.info(f"Сообщение {request.id} на модерации в Maer")
                return {"status": "ok"}

            elif request.status == 1:
                # Одобрено
                message.status = MessageStatus.APPROVED
                logger.info(f"Сообщение {request.id} одобрено Maer → APPROVED")
                should_notify_approved = True

            elif request.status == 2:
                # Отклонено
                message.status = MessageStatus.REJECTED
                reason = request.reason or "Не указана"
                logger.info(
                    f"Сообщение {request.id} отклонено Maer → REJECTED. Причина: {reason}"
                )

                # Сохраняем причину отклонения в мета
                if not message.meta:
                    message.meta = {}
                message.meta["maer_rejection_reason"] = reason
                should_notify_rejected = True

            else:
                logger.error(f"Неизвестный статус {request.status} от Maer для сообщения {request.id}")
                raise HTTPException(status_code=422, detail=f"Неизвестный статус: {request.status}")

            await session.commit()

        if should_notify_approved:
            await notify_user_moderation_result(request.id, approved=True)
        elif should_notify_rejected:
            await notify_user_moderation_result(request.id, approved=False)

        return {"status": "ok"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обработке webhook от Maer для сообщения {request.id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/shown")
async def message_shown(request: MessageShownOnFacadeRequest):
    """
    Webhook от Maer API о показе сообщения на фасаде.

    Вызывается когда сообщение показано на креативе.

    type: 1 - shown (показано)
    """
    # Проверяем тип события
    if request.type != 1:
        logger.error(f"Неизвестный тип события {request.type} от Maer для сообщения {request.id}")
        raise HTTPException(status_code=422, detail=f"Неизвестный тип события: {request.type}")

    try:
        async with async_session() as session:
            result = await session.execute(
                select(Message).where(Message.id == request.id)
            )
            message = result.scalar_one_or_none()

            if not message:
                logger.error(f"Сообщение {request.id} не найдено для обработки webhook показа")
                raise HTTPException(status_code=404, detail="Сообщение не найдено")

            # Обрабатываем событие показа только для сообщений,
            # которые уже прошли модерацию.
            if message.status != MessageStatus.APPROVED:
                logger.warning(
                    f"Игнорируем /maer/shown для сообщения {request.id}: "
                    f"статус {message.status} не прошёл модерацию"
                )
                return {"status": "ignored", "reason": "message_not_moderated"}

            shown_at_utc = datetime.now(timezone.utc)
            message.shown_on_facade = True
            if message.shown_time is None:
                message.shown_time = shown_at_utc

            # Сохраняем время показа в мета
            if not message.meta:
                message.meta = {}
            message.meta["shown_at"] = message.shown_time.isoformat()

            await session.commit()

            logger.info(
                f"Сообщение {request.id} показано на фасаде: "
                f"shown_on_facade=True, shown_time={message.shown_time.isoformat()}"
            )

        return {"status": "ok"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обработке webhook показа от Maer для сообщения {request.id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
