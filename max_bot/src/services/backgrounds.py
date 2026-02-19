"""Сервис для работы с фонами."""

import textwrap
import uuid
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

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
    bg_path = get_background_path(background_id)
    if bg_path is None:
        return None

    generated_dir = get_data_dir() / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)

    img = Image.open(bg_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    W, H = img.size

    # Рабочая область с отступами
    margin_x = int(W * 0.08)
    margin_y = int(H * 0.10)
    usable_w = W - 2 * margin_x
    usable_h = H - 2 * margin_y

    # Загрузка шрифта Montserrat (с фоллбэком на DejaVu)
    font_path = get_data_dir() / "Montserrat-Bold.ttf"
    if not font_path.is_file():
        for fallback in [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/local/share/fonts/Montserrat-Bold.ttf",
        ]:
            if Path(fallback).is_file():
                font_path = Path(fallback)
                break

    size_large = max(int(H * 0.06), 24)
    size_small = max(int(size_large * 0.70), 16)

    def _load_fonts(sz_l: int, sz_s: int) -> tuple[ImageFont.FreeTypeFont, ImageFont.FreeTypeFont]:
        return (
            ImageFont.truetype(str(font_path), sz_l),
            ImageFont.truetype(str(font_path), sz_s),
        )

    def _max_chars(font: ImageFont.FreeTypeFont) -> int:
        """Количество символов, помещающихся в usable_w, по реальной ширине глифов."""
        sample = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя "
        avg_w = font.getlength(sample) / len(sample)
        return max(int(usable_w / avg_w), 10)

    def _block_h(n_lines: int, sz_l: int, sz_s: int) -> int:
        return n_lines * int(sz_l * 1.35) + int(sz_l * 1.6) + sz_s

    font_large, font_small = _load_fonts(size_large, size_small)
    wrapped_lines = textwrap.wrap(message, width=_max_chars(font_large))
    signature = f"{name}, {city}"

    # Уменьшаем шрифт пока блок не помещается по высоте
    while _block_h(len(wrapped_lines), size_large, size_small) > usable_h and size_large > 14:
        size_large = max(size_large - 2, 14)
        size_small = max(int(size_large * 0.70), 12)
        font_large, font_small = _load_fonts(size_large, size_small)
        wrapped_lines = textwrap.wrap(message, width=_max_chars(font_large))

    logger.info(f"Шрифт: {font_path}, size={size_large}, строк={len(wrapped_lines)}")

    def _draw_with_shadow(
        d: ImageDraw.ImageDraw,
        pos: tuple[float, float],
        text: str,
        font: ImageFont.FreeTypeFont,
    ) -> None:
        x, y = pos
        for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
            d.text((x + dx, y + dy), text, font=font, fill="black", anchor="mm")
        d.text((x, y), text, font=font, fill="white", anchor="mm")

    line_h = int(size_large * 1.35)
    sig_gap = int(size_large * 0.8)
    total_lines = len(wrapped_lines)
    block_h = _block_h(total_lines, size_large, size_small)
    start_y = H // 2 - block_h // 2 + line_h // 2

    for i, line in enumerate(wrapped_lines):
        _draw_with_shadow(draw, (W // 2, start_y + i * line_h), line, font_large)

    signature_y = start_y + (total_lines - 1) * line_h + sig_gap
    _draw_with_shadow(draw, (W // 2, signature_y), signature, font_small)

    output_path = generated_dir / f"{uuid.uuid4().hex}.png"
    img.convert("RGB").save(output_path, "PNG")
    logger.info(f"Сгенерировано превью фона {background_id}: {output_path}")
    return output_path


def build_preview_url(filename: str) -> str:
    """Строит публичный URL к превью: {BOT_WEBHOOK_URL}/previews/{filename}."""
    base = Config.BOT_WEBHOOK_URL.rstrip("/")
    return f"{base}/previews/{filename}"
