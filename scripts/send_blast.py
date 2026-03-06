"""
Рассылка сообщений пользователям из output1.csv по их max_id.
Запуск: python send_blast.py
"""

import asyncio
import csv
import pathlib

from maxapi import Bot
from maxapi.enums.parse_mode import ParseMode
from maxapi.enums.upload_type import UploadType
from maxapi.types.attachments.upload import AttachmentPayload, AttachmentUpload
from maxapi.types.input_media import InputMediaBuffer
from maxapi.utils.message import process_input_media

# ─── Настройки ───────────────────────────────────────────────────────────────

BOT_TOKEN = ""

CSV_FILE = pathlib.Path(__file__).parent / "output1.csv"

# PNG-изображение для вложения (лежит рядом со скриптом)
IMAGE_FILE = pathlib.Path(__file__).parent / "IMG_20260306_171117.png"

# Текст сообщения, которое будет отправлено каждому пользователю
MESSAGE_TEXT = """7 и 8 марта ваши поздравления могут засиять в центре Москвы! ✨

Напишите тёплые слова в чат‑боте — и они появятся на медиафасаде по адресу: Москва, ул. Большая Тульская, 2.
Это оригинальный способ сказать «я тебя люблю», «спасибо» или просто поднять настроение дорогому человеку ❤️
Пропустили трансляцию? Мы отправим фото вашего поздравления в чат — сохраняйте на память! 📸

Давайте сделаем этот праздник ярче вместе: [https://max.ru/max_8marta_bot](https://max.ru/max_8marta_bot)\
"""

# Пауза между отправками (секунд), чтобы не словить 429
DELAY_BETWEEN_MESSAGES = 0.1

# Пауза при 429 (умножается на номер попытки)
RATE_LIMIT_BASE_PAUSE = 2.0

MAX_RETRIES = 3

# ─── Логика ──────────────────────────────────────────────────────────────────


def load_max_ids(csv_path: pathlib.Path) -> list[tuple[int, str]]:
    """Возвращает список (max_id, имя) из CSV."""
    users = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            max_id = int(row["max_id"])
            first_name = row.get("first_name", "").strip()
            users.append((max_id, first_name))
    return users


async def upload_image(bot: Bot, image_path: pathlib.Path) -> str | None:
    """Загружает изображение в MAX один раз и возвращает токен для переиспользования."""
    if not image_path.exists():
        print(f"[предупреждение] Файл изображения не найден: {image_path}")
        return None
    try:
        image_bytes = image_path.read_bytes()
        att = InputMediaBuffer(buffer=image_bytes, filename=image_path.name)
        upload = await process_input_media(base_connection=bot, bot=bot, att=att)
        token = upload.payload.token
        print(f"Изображение загружено в MAX, токен: {token[:20]}...")
        return token
    except Exception as e:
        print(f"[ошибка] Не удалось загрузить изображение: {e}")
        return None


async def send_with_retry(bot: Bot, max_id: int, text: str, image_token: str | None) -> str:
    """
    Отправляет сообщение с повтором при 429.

    Возвращает:
        'sent'    — успешно
        'skipped' — чат не найден (пользователь заблокировал / не запускал бота)
        'error'   — другая ошибка, все попытки исчерпаны
    """
    attachments = []
    if image_token:
        attachments.append(
            AttachmentUpload(type=UploadType.IMAGE, payload=AttachmentPayload(token=image_token))
        )

    for attempt in range(MAX_RETRIES):
        try:
            await bot.send_message(user_id=max_id, text=text, attachments=attachments or None, parse_mode=ParseMode.MARKDOWN)
            return "sent"
        except Exception as e:
            err = str(e).lower()
            if "404" in err or "chat.not.found" in err or "not.found" in err:
                print(f"  [пропуск] {max_id} — чат не найден")
                return "skipped"
            if "403" in err or "chat.denied" in err or "dialog.suspended" in err:
                print(f"  [пропуск] {max_id} — диалог заблокирован")
                return "skipped"
            if "429" in err or "too.many.requests" in err or "too_many" in err:
                wait = RATE_LIMIT_BASE_PAUSE * (attempt + 1)
                print(f"  [429] {max_id} — rate limit, ждём {wait:.0f}с (попытка {attempt + 1}/{MAX_RETRIES})")
                await asyncio.sleep(wait)
                continue
            print(f"  [ошибка] {max_id}: {e}")
            return "error"

    print(f"  [ошибка] {max_id} — все попытки исчерпаны")
    return "error"


async def main() -> None:
    users = load_max_ids(CSV_FILE)
    total = len(users)
    print(f"Загружено пользователей: {total}")
    print(f"Текст сообщения:\n---\n{MESSAGE_TEXT.strip()}\n---\n")

    bot = Bot(BOT_TOKEN)

    # Загружаем изображение один раз
    image_token = await upload_image(bot, IMAGE_FILE)

    sent = skipped = errors = 0

    for i, (max_id, name) in enumerate(users, start=1):
        label = f"{name} ({max_id})" if name else str(max_id)
        print(f"[{i}/{total}] Отправка → {label} ...", end=" ", flush=True)

        outcome = await send_with_retry(bot, max_id, MESSAGE_TEXT, image_token)

        if outcome == "sent":
            sent += 1
            print("OK")
        elif outcome == "skipped":
            skipped += 1
        else:
            errors += 1

        await asyncio.sleep(DELAY_BETWEEN_MESSAGES)

    print(f"\nГотово: {sent} отправлено, {skipped} недоступно, {errors} ошибок")


if __name__ == "__main__":
    asyncio.run(main())
