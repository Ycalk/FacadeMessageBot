"""Сервис для работы с фонами."""

import textwrap
import uuid
from pathlib import Path

from core.config import Config
from core.logger import get_logger

logger = get_logger(__name__)

# Фиксированный список фонов
BACKGROUND_IDS = [1, 2, 3]


def get_data_dir() -> Path:
    """Возвращает путь к директории data из конфига."""
    return Path(Config.DATA_DIR)


def get_backgrounds_preview_path() -> Path | None:
    """Возвращает путь к backgrounds.png — превью всех трёх фонов."""
    path = get_data_dir() / "backgrounds.png"
    if not path.is_file():
        logger.warning(f"Файл backgrounds.png не найден: {path}")
        return None
    return path


def get_background_path(background_id: int) -> Path | None:
    """Возвращает путь к отдельному файлу фона data/{id}.png."""
    path = get_data_dir() / f"{background_id}.png"
    if not path.is_file():
        logger.warning(f"Фон не найден: {path}")
        return None
    return path


def generate_text_preview(
    background_id: int, message: str, name: str, city: str
) -> Path | None:
    """
    Накладывает текст поздравления на выбранный фон и сохраняет результат
    в data/generated/. Возвращает путь к сгенерированному файлу или None при ошибке.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        logger.error("Библиотека Pillow не установлена — превью недоступно")
        return None

    bg_path = get_background_path(background_id)
    if bg_path is None:
        return None

    generated_dir = get_data_dir() / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)

    img = Image.open(bg_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    W, H = img.size

    # Загрузка шрифта Montserrat (с фоллбэком на DejaVu)
    font_path = get_data_dir() / "Montserrat-Bold.ttf"
    font_large: ImageFont.ImageFont | ImageFont.FreeTypeFont = ImageFont.load_default()
    font_small: ImageFont.ImageFont | ImageFont.FreeTypeFont = ImageFont.load_default()
  
    size_large = max(int(H * 0.06), 24)
    size_small = max(int(H * 0.04), 18)
    font_large = ImageFont.truetype(str(font_path), size_large)
    font_small = ImageFont.truetype(str(font_path), size_small)
    logger.info(f"Шрифт загружен: {font_path}")

    # Перенос длинного текста поздравления
    max_chars = max(int(W / (H * 0.035)), 20)
    wrapped_lines = textwrap.wrap(f"«{message}»", width=max_chars)
    signature = f"{name}, {city}"

    def _draw_with_shadow(
        d: ImageDraw.ImageDraw,
        pos: tuple[float, float],
        text: str,
        font: ImageFont.ImageFont | ImageFont.FreeTypeFont,
    ) -> None:
        x, y = pos
        for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
            d.text((x + dx, y + dy), text, font=font, fill="black", anchor="mm")
        d.text((x, y), text, font=font, fill="white", anchor="mm")

    line_height = int(H * 0.08)
    total_lines = len(wrapped_lines)
    start_y = H // 2 - (total_lines * line_height) // 2

    for i, line in enumerate(wrapped_lines):
        _draw_with_shadow(draw, (W // 2, start_y + i * line_height), line, font_large)

    signature_y = start_y + total_lines * line_height + int(H * 0.05)
    _draw_with_shadow(draw, (W // 2, signature_y), signature, font_small)

    output_path = generated_dir / f"{uuid.uuid4().hex}.png"
    img.convert("RGB").save(output_path, "PNG")
    logger.info(f"Сгенерировано превью фона {background_id}: {output_path}")
    return output_path


def build_preview_url(filename: str) -> str:
    """Строит публичный URL к превью: {BOT_WEBHOOK_URL}/previews/{filename}."""
    base = Config.BOT_WEBHOOK_URL.rstrip("/")
    return f"{base}/previews/{filename}"
