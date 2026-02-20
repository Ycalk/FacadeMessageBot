"""Сервис чёрного списка слов — in-memory regex кэш поверх PostgreSQL."""

import re
from sqlalchemy import select, delete

from core.logger import get_logger
from db.models import BlacklistWord
from db.session import async_session

logger = get_logger(__name__)

# Скомпилированный паттерн — пересобирается при изменении списка
_pattern: re.Pattern | None = None


def _rebuild_pattern(words: list[str]) -> None:
    """Пересобирает compiled regex из текущего списка слов."""
    global _pattern
    if not words:
        _pattern = None
        logger.info("Чёрный список пуст, паттерн сброшен")
        return
    escaped = [re.escape(w) for w in words]
    _pattern = re.compile("|".join(escaped), re.IGNORECASE)
    logger.info(f"Чёрный список загружен: {len(words)} слов/фраз")


def is_blacklisted(text: str) -> bool:
    """Проверяет, содержит ли текст слова из чёрного списка. O(n) по длине текста."""
    return bool(_pattern and _pattern.search(text))


async def load_blacklist() -> None:
    """Загружает чёрный список из БД и пересобирает паттерн. Вызывать при старте."""
    async with async_session() as session:
        result = await session.execute(select(BlacklistWord.word))
        words = list(result.scalars().all())
    _rebuild_pattern(words)


async def get_all_words() -> list[BlacklistWord]:
    """Возвращает все записи чёрного списка из БД."""
    async with async_session() as session:
        result = await session.execute(
            select(BlacklistWord).order_by(BlacklistWord.created_at.desc())
        )
        return list(result.scalars().all())


async def add_word(word: str) -> BlacklistWord | None:
    """
    Добавляет слово в чёрный список и обновляет паттерн.
    Возвращает None если слово уже существует.
    """
    word = word.strip().lower()
    if not word:
        return None
    async with async_session() as session:
        # Проверяем дубликат
        existing = await session.execute(
            select(BlacklistWord).where(BlacklistWord.word == word)
        )
        if existing.scalar_one_or_none():
            logger.info(f"Слово уже в чёрном списке: {word!r}")
            return None
        entry = BlacklistWord(word=word)
        session.add(entry)
        await session.commit()
        await session.refresh(entry)
        logger.info(f"Добавлено в чёрный список: {word!r}")

    await load_blacklist()
    return entry


async def add_words_bulk(words: list[str]) -> int:
    """
    Массовое добавление слов (например, из .txt файла).
    Пропускает дубликаты. Возвращает количество реально добавленных.
    """
    normalized = list({w.strip().lower() for w in words if w.strip()})
    if not normalized:
        return 0

    async with async_session() as session:
        # Получаем уже существующие
        existing_result = await session.execute(select(BlacklistWord.word))
        existing = set(existing_result.scalars().all())

        new_words = [w for w in normalized if w not in existing]
        if not new_words:
            return 0

        session.add_all([BlacklistWord(word=w) for w in new_words])
        await session.commit()
        logger.info(f"Массово добавлено в чёрный список: {len(new_words)} слов")

    await load_blacklist()
    return len(new_words)


async def delete_word(word_id: int) -> bool:
    """Удаляет слово по ID. Возвращает True если удалено."""
    async with async_session() as session:
        result = await session.execute(
            delete(BlacklistWord).where(BlacklistWord.id == word_id)
        )
        await session.commit()
        deleted = result.rowcount > 0
        if deleted:
            logger.info(f"Удалено из чёрного списка: id={word_id}")

    if deleted:
        await load_blacklist()
    return deleted
