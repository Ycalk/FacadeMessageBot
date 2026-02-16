from fastapi import APIRouter, HTTPException
import httpx
from sqlalchemy import select

from core.logger import get_logger
from api.schemas import MessageShownRequest, MessageResponse
from api.utils import send_facade_image
from db.models import Message, MessageStatus
from db.session import async_session


logger = get_logger(__name__)

router = APIRouter(prefix="/message")


@router.post("/shown")
async def message_shown(request: MessageShownRequest):
    """
    Webhook когда сообщение показано на экране.
    frame_url - публичный URL на фото из MinIO.
    Скачивает фото и отправляет пользователю.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(request.frame_url)
            response.raise_for_status()
            image_bytes = response.content

        # Отправляем фото пользователю
        await send_facade_image(request.message_id, image_bytes)

        logger.info(f"Сообщение {request.message_id} показано и отправлено пользователю")
        return {"status": "ok"}
    except httpx.HTTPError as e:
        logger.error(f"Ошибка при скачивании фото по URL {request.frame_url}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download image: {str(e)}")
    except ValueError as e:
        logger.error(f"Сообщение {request.message_id} не найдено: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка при обработке показа сообщения {request.message_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/approved", response_model=list[MessageResponse])
async def get_approved_messages():
    """
    Возвращает все сообщения в статусах APPROVED и SHOWN_ON_FACADE.
    """
    try:
        async with async_session() as session:
            result = await session.execute(
                select(Message)
                .where(
                    Message.status.in_([
                        MessageStatus.APPROVED,
                        MessageStatus.SHOWN_ON_FACADE
                    ])
                )
                .order_by(Message.created_at.desc())
            )
            messages = result.scalars().all()

            logger.info(f"Получено {len(messages)} одобренных/показанных сообщений")
            return messages
    except Exception as e:
        logger.error(f"Ошибка при получении одобренных сообщений: {e}")
        raise HTTPException(status_code=500, detail=str(e))