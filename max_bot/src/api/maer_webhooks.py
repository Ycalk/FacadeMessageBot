"""Webhooks для интеграции с Maer API."""

from datetime import datetime
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from core.logger import get_logger
from api.schemas import MessageModeratedRequest, MessageShownOnFacadeRequest
from api.auth import verify_api_token
from api.utils import notify_user_moderation_result
from db.models import Message, MessageStatus
from db.session import async_session


logger = get_logger(__name__)

router = APIRouter(prefix="/maer", dependencies=[verify_api_token])


@router.post("/moderated")
async def message_moderated(request: MessageModeratedRequest):
    """
    Webhook от Maer API с результатом модерации.

    Вызывается Maer после завершения модерации.

    status: 0 - на модерации, 1 - успешно, 2 - отклонён
    """
    try:
        async with async_session() as session:
            result = await session.execute(
                select(Message).where(Message.id == request.id)
            )
            message = result.scalar_one_or_none()

            if not message:
                logger.error(f"Сообщение {request.id} не найдено для обработки webhook")
                raise HTTPException(status_code=404, detail="Сообщение не найдено")

            # Обработка статуса от Maer
            if request.status == 0:
                # На модерации - не обновляем статус
                logger.info(f"Сообщение {request.id} на модерации в Maer")
                return {"status": "ok"}

            elif request.status == 1:
                # Одобрено
                message.status = MessageStatus.APPROVED
                logger.info(f"Сообщение {request.id} одобрено Maer → APPROVED")

                # Уведомляем пользователя об одобрении
                await notify_user_moderation_result(request.id, approved=True)

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

                # Уведомляем пользователя об отклонении
                await notify_user_moderation_result(request.id, approved=False)

            else:
                logger.error(f"Неизвестный статус {request.status} от Maer для сообщения {request.id}")
                raise HTTPException(status_code=422, detail=f"Неизвестный статус: {request.status}")

            await session.commit()

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

            # Обновляем статус только если ещё не отправлено фото
            if message.status != MessageStatus.PHOTO_SENT:
                old_status = message.status
                message.status = MessageStatus.SHOWN_ON_FACADE

                # Сохраняем время показа в мета
                if not message.meta:
                    message.meta = {}
                message.meta["shown_at"] = datetime.now().isoformat()

                await session.commit()

                logger.info(
                    f"Сообщение {request.id} показано на фасаде: "
                    f"{old_status} → SHOWN_ON_FACADE"
                )
            else:
                logger.info(
                    f"Сообщение {request.id} уже в статусе PHOTO_SENT, "
                    f"не меняем на SHOWN_ON_FACADE"
                )

        return {"status": "ok"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обработке webhook показа от Maer для сообщения {request.id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
