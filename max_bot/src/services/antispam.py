"""Антиспам-система на базе Redis (скользящее окно)."""

import time

from redis.asyncio import Redis

from core.config import Config
from core.logger import get_logger

logger = get_logger(__name__)


class AntiSpam:
    """Ограничение частоты действий пользователя через Redis sorted set."""

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    def _action_key(self, user_id: int) -> str:
        return f"antispam:{user_id}"

    def _block_key(self, user_id: int) -> str:
        return f"antispam:block:{user_id}"

    async def is_blocked(self, user_id: int) -> bool:
        """Проверяет, заблокирован ли пользователь за спам."""
        if user_id in Config.unlimited_users_list:
            return False
        return await self._redis.exists(self._block_key(user_id)) > 0

    async def record_action(self, user_id: int) -> bool:
        """Записывает действие пользователя.

        Возвращает True если действие разрешено, False если пользователь заспамил.
        """
        if user_id in Config.unlimited_users_list:
            return True

        # Проверяем блокировку
        if await self._redis.exists(self._block_key(user_id)):
            return False

        now = time.time()
        key = self._action_key(user_id)
        window_start = now - Config.ANTISPAM_WINDOW_SECONDS

        pipe = self._redis.pipeline()
        # Удаляем старые записи за пределами окна
        pipe.zremrangebyscore(key, 0, window_start)
        # Добавляем текущее действие
        pipe.zadd(key, {str(now): now})
        # Считаем действия в окне
        pipe.zcard(key)
        # TTL чтобы ключ не висел вечно
        pipe.expire(key, Config.ANTISPAM_WINDOW_SECONDS * 2)
        results = await pipe.execute()

        action_count = results[2]

        if action_count > Config.ANTISPAM_MAX_ACTIONS:
            # Блокируем пользователя
            await self._redis.setex(
                self._block_key(user_id),
                Config.ANTISPAM_BLOCK_SECONDS,
                "1",
            )
            logger.warning(
                f"Пользователь {user_id} заблокирован за спам "
                f"({action_count} действий за {Config.ANTISPAM_WINDOW_SECONDS} сек)"
            )
            return False

        return True
