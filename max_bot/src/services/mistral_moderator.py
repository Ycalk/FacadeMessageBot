"""Модерация сообщений через Mistral AI."""

from openai import AsyncOpenAI
from core.config import Config
from core.logger import get_logger
from services.app_settings import DEFAULT_MISTRAL_PROMPT, MISTRAL_PROMPT_KEY, get_setting

logger = get_logger(__name__)

# Инициализируем клиент Mistral (использует OpenAI-совместимый API)
client = AsyncOpenAI(
    api_key=Config.MISTRAL_API_KEY,
    base_url="https://api.mistral.ai/v1"
) if Config.MISTRAL_API_KEY else None


async def moderate_with_mistral(text: str, name: str, city: str) -> dict:
    """
    Модерация сообщения через Mistral AI.

    Args:
        text: Текст сообщения
        name: Имя отправителя
        city: Город отправителя

    Returns:
        dict с ключами:
        - approved: bool - одобрено ли сообщение
        - reason: str - причина решения (если отклонено)
        - confidence: float - уверенность модели (0-1)
    """
    if not client:
        logger.warning("Mistral API ключ не настроен, пропускаем AI модерацию")
        return {"approved": True, "reason": "Mistral не настроен", "confidence": 0.0}

    try:
        rules = await get_setting(MISTRAL_PROMPT_KEY, DEFAULT_MISTRAL_PROMPT)
        prompt = (
            f"{rules}\n\n"
            f"СООБЩЕНИЕ ДЛЯ ПРОВЕРКИ:\n"
            f'Текст: {text}\n'
            f"Имя: {name}\n"
            f"Город: {city}"
        )

        response = await client.chat.completions.create(
            model=Config.MISTRAL_MODEL,
            messages=[
                {"role": "system", "content": (
                    "Ты модератор публичных сообщений. "
                    "Всегда отвечай строго в формате JSON:\n"
                    '{"approved": true/false, '
                    '"reason": "причина отклонения или пустая строка", '
                    '"confidence": 0.95}'
                )},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200,
            response_format={"type": "json_object"}
        )

        result_text = response.choices[0].message.content

        # Парсим JSON ответ
        import json
        result = json.loads(result_text)

        logger.info(
            f"Mistral модерация: approved={result.get('approved')}, "
            f"confidence={result.get('confidence')}, reason={result.get('reason', '')}"
        )

        return {
            "approved": result.get("approved", False),
            "reason": result.get("reason", ""),
            "confidence": result.get("confidence", 0.0)
        }

    except Exception as e:
        logger.error(f"Ошибка при Mistral модерации: {e}")
        # При ошибке пропускаем (одобряем)
        return {"approved": True, "reason": f"Ошибка Mistral: {e}", "confidence": 0.0}
