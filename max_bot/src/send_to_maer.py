"""
Скрипт для ручной отправки сообщения в Maer и перевода статуса в maer_moderation.

Использование (внутри контейнера):
    python send_to_maer.py <message_id>

Пример:
    python send_to_maer.py 42
"""

import asyncio
import sys

from sqlalchemy import select

from db.models import Message, MessageStatus
from db.session import async_session
from services.maer_client import MaerAPIError, send_to_maer_moderation


async def main(message_id: int) -> None:
    async with async_session() as session:
        result = await session.execute(
            select(Message).where(Message.id == message_id)
        )
        message = result.scalar_one_or_none()

        if not message:
            print(f"Сообщение {message_id} не найдено")
            sys.exit(1)

        print(f"Сообщение {message_id}: статус={message.status}, имя={message.name}, город={message.city}")
        print(f"Текст: {message.text}")

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
            print(f"Сообщение {message_id} успешно отправлено в Maer → статус MAER_MODERATION")
        except MaerAPIError as e:
            print(f"Ошибка Maer API: {e}")
            sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python send_to_maer.py <message_id>")
        sys.exit(1)

    try:
        msg_id = int(sys.argv[1])
    except ValueError:
        print(f"Неверный ID: {sys.argv[1]}")
        sys.exit(1)

    asyncio.run(main(msg_id))
