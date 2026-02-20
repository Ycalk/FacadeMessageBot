"""Сервис настроек приложения — key/value хранилище поверх PostgreSQL с in-memory кэшем."""

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from core.logger import get_logger
from db.models import AppSetting
from db.session import async_session

logger = get_logger(__name__)

# Ключи настроек
MISTRAL_PROMPT_KEY = "mistral_custom_prompt"
DEFAULT_MISTRAL_PROMPT = """\
Ты модератор поздравлений для медиафасада здания.
Твоя задача - проверить сообщение на соответствие правилам:

ПРАВИЛА:
1. Запрещены: мат, оскорбления, политика, реклама, спам
2. Запрещены: призывы к насилию, экстремизм, дискриминация
3. Запрещены: контакты (телефоны, email, ссылки)
4. Разрешены: добрые поздравления, пожелания, признания в любви
5. Сообщение должно быть на русском языке

Будь строгим, но справедливым. Если есть сомнения - лучше отклони.\
"""

# In-memory кэш: инвалидируется при записи
_cache: dict[str, str] = {}


async def get_setting(key: str, default: str = "") -> str:
    """Возвращает значение настройки из кэша или БД."""
    if key in _cache:
        return _cache[key]

    async with async_session() as session:
        result = await session.execute(
            select(AppSetting).where(AppSetting.key == key)
        )
        row = result.scalar_one_or_none()
        value = row.value if row else default

    _cache[key] = value
    return value


async def set_setting(key: str, value: str) -> None:
    """Сохраняет значение настройки в БД и обновляет кэш."""
    async with async_session() as session:
        stmt = insert(AppSetting).values(key=key, value=value)
        stmt = stmt.on_conflict_do_update(
            index_elements=["key"],
            set_={"value": value, "updated_at": func.now()},
        )
        await session.execute(stmt)
        await session.commit()

    _cache[key] = value
    logger.info(f"Настройка сохранена: {key!r} = {value[:80]!r}{'...' if len(value) > 80 else ''}")


async def init_default_settings() -> None:
    """Записывает дефолтные настройки в БД при первом запуске (не перезаписывает существующие)."""
    defaults = {
        MISTRAL_PROMPT_KEY: DEFAULT_MISTRAL_PROMPT,
    }
    async with async_session() as session:
        for key, value in defaults.items():
            stmt = insert(AppSetting).values(key=key, value=value)
            stmt = stmt.on_conflict_do_nothing(index_elements=["key"])
            await session.execute(stmt)
        await session.commit()
    logger.info("Настройки по умолчанию инициализированы")
