from fastapi import APIRouter, HTTPException
import httpx
from sqlalchemy import select, or_
from urllib.parse import urlparse

from core.logger import get_logger
from api.schemas import MessageShownRequest, MessageResponse
from api.auth import verify_api_token
from api.utils import send_facade_image
from db.models import Message, MessageStatus
from db.session import async_session


logger = get_logger(__name__)

router = APIRouter(prefix="/message", dependencies=[verify_api_token])

_ALLOWED_FRAME_HOST = "s3.facader.ycalk.tech"


def _validate_frame_url(frame_url: str) -> str:
    """Проверяет, что фото можно скачивать только из доверенного S3."""
    parsed = urlparse(frame_url)
    if parsed.scheme != "https":
        raise HTTPException(status_code=400, detail="frame_url должен использовать https")
    if parsed.hostname != _ALLOWED_FRAME_HOST:
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимый домен frame_url: разрешен только {_ALLOWED_FRAME_HOST}",
        )
    if parsed.username or parsed.password:
        raise HTTPException(status_code=400, detail="frame_url с userinfo не поддерживается")
    return frame_url


@router.post("/shown")
async def message_shown(request: MessageShownRequest):
    """
    Webhook когда сообщение показано на экране.
    frame_url - публичный URL на фото фасада.
    Скачивает фото и отправляет пользователю.
    """
    try:
        frame_url = _validate_frame_url(request.frame_url)
        async with httpx.AsyncClient() as client:
            response = await client.get(frame_url, follow_redirects=False, timeout=10.0)
            if 300 <= response.status_code < 400:
                raise HTTPException(status_code=400, detail="Редиректы для frame_url запрещены")
            response.raise_for_status()
            image_bytes = response.content

        # Отправляем фото пользователю
        await send_facade_image(request.message_id, image_bytes)

        logger.info(f"Сообщение {request.message_id} показано и отправлено пользователю")
        return {"status": "ok"}
    except HTTPException:
        raise
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
    Возвращает одобренные сообщения, исключая тех, кто отказался от фото (want_photo=False).
    """
    try:
        async with async_session() as session:
            result = await session.execute(
                select(Message)
                .where(
                    Message.status == MessageStatus.APPROVED,
                    or_(Message.want_photo.is_(None), Message.want_photo == True),
                )
                .order_by(Message.created_at.desc())
            )
            messages = result.scalars().all()

            logger.info(f"Получено {len(messages)} одобренных сообщений")
            return messages
    except Exception as e:
        logger.error(f"Ошибка при получении одобренных сообщений: {e}")
        raise HTTPException(status_code=500, detail=str(e))
