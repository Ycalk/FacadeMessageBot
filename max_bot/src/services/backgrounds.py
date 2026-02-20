"""Сервис для работы с фонами."""

import io
import textwrap
import uuid
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from core.config import Config
from core.emoji_whitelist import EMOJI_WHITELIST
from core.logger import get_logger

logger = get_logger(__name__)

# Фиксированный список фонов
BACKGROUND_IDS = [1, 2, 3, 4]
_EMOJI_SORTED = sorted(EMOJI_WHITELIST, key=len, reverse=True)


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


def _render_preview(
    background_id: int, message: str, name: str, city: str
) -> Image.Image | None:
    """Рендерит изображение превью без сохранения на диск. Возвращает Image или None."""
    bg_path = get_background_path(background_id)
    if bg_path is None:
        return None

    img = Image.open(bg_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    W, H = img.size
    text_color = "white" if background_id == 2 else "black"

    # Рабочая область с отступами
    margin_x = int(W * 0.08)
    margin_y = int(H * 0.10)
    extra_side_inset = int(W * 0.10)  # Дополнительно ужимаем слева/справа на 10%
    margin_x += extra_side_inset
    usable_w = W - 2 * margin_x
    usable_h = H - 2 * margin_y

    # Загрузка шрифта Montserrat (с фоллбэком на DejaVu)
    font_path = get_data_dir() / "Montserrat-Medium.ttf"

    size_large = max(int(H * 0.06) - 5, 20)
    size_small = max(int(size_large * 0.70) - 2, 14)

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
        return n_lines * int(sz_l * 1.10) + int(sz_l * 1.6) + sz_s

    font_large, font_small = _load_fonts(size_large, size_small)
    wrapped_lines = textwrap.wrap(message, width=_max_chars(font_large))
    signature_parts = [part.strip() for part in (name, city) if part and part.strip()]
    signature = ", ".join(signature_parts)

    # Уменьшаем шрифт пока блок не помещается по высоте
    while _block_h(len(wrapped_lines), size_large, size_small) > usable_h and size_large > 14:
        size_large = max(size_large - 2, 14)
        size_small = max(int(size_large * 0.70) - 2, 12)
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
        d.text((x, y), text, font=font, fill=text_color, anchor="lm")

    emoji_dir = get_data_dir() / "emoji"
    emoji_cache: dict[tuple[str, int], Image.Image] = {}

    def _emoji_path(token: str) -> Path | None:
        cps = [f"{ord(ch):x}" for ch in token]
        with_vs = "-".join(cps) + ".png"
        no_vs = "-".join(cp for cp in cps if cp != "fe0f") + ".png"
        for candidate in (emoji_dir / with_vs, emoji_dir / no_vs):
            if candidate.is_file():
                return candidate
        return None

    def _emoji_image(token: str, px: int) -> Image.Image | None:
        key = (token, px)
        cached = emoji_cache.get(key)
        if cached is not None:
            return cached
        path = _emoji_path(token)
        if path is None:
            return None
        original = Image.open(path).convert("RGBA")
        resized = original.resize((px, px), Image.Resampling.LANCZOS)
        emoji_cache[key] = resized
        return resized

    def _tokenize_line(line: str) -> list[tuple[str, bool]]:
        tokens: list[tuple[str, bool]] = []
        i = 0
        while i < len(line):
            matched = False
            for emoji in _EMOJI_SORTED:
                if line.startswith(emoji, i):
                    tokens.append((emoji, True))
                    i += len(emoji)
                    matched = True
                    break
            if not matched:
                tokens.append((line[i], False))
                i += 1
        return tokens

    def _draw_line_with_emoji(
        d: ImageDraw.ImageDraw,
        cy: float,
        line: str,
        font: ImageFont.FreeTypeFont,
    ) -> None:
        tokens = _tokenize_line(line)
        emoji_px = max(int(font.size * 1.10), 12)
        widths: list[float] = []
        for token, is_emoji in tokens:
            if is_emoji:
                widths.append(float(emoji_px))
            else:
                widths.append(float(font.getlength(token)))
        x = float(margin_x)

        for (token, is_emoji), w in zip(tokens, widths):
            if is_emoji:
                emoji_img = _emoji_image(token, emoji_px)
                if emoji_img is not None:
                    y = int(cy - emoji_px / 2)
                    img.paste(emoji_img, (int(x), y), emoji_img)
                else:
                    _draw_with_shadow(d, (x, cy), token, font)
            else:
                _draw_with_shadow(d, (x, cy), token, font)
            x += w

    line_h = int(size_large * 1.10)
    sig_gap = int(size_large * 1.6)
    total_lines = len(wrapped_lines)
    block_h = _block_h(total_lines, size_large, size_small)
    y_offset = int(H * 0.08)
    start_y = H // 2 - block_h // 2 + line_h // 2 + int(H * 0.03) + y_offset
    min_start_y = int(H * 0.50)
    max_start_y = int(H - margin_y - sig_gap - (total_lines - 1) * line_h - size_small * 0.6)
    if max_start_y < min_start_y:
        max_start_y = min_start_y
    start_y = max(start_y, min_start_y)
    start_y = min(start_y, max_start_y)

    for i, line in enumerate(wrapped_lines):
        _draw_line_with_emoji(draw, start_y + i * line_h, line, font_large)

    signature_y = start_y + (total_lines - 1) * line_h + sig_gap
    _draw_line_with_emoji(draw, signature_y, signature, font_small)

    return img.convert("RGB")


def generate_text_preview_bytes(
    background_id: int, message: str, name: str, city: str
) -> bytes | None:
    """
    Рендерит превью и возвращает PNG-байты без сохранения на диск.
    Используется при показе превью пользователю (до отправки на модерацию).
    """
    img = _render_preview(background_id, message, name, city)
    if img is None:
        return None
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def generate_text_preview(
    background_id: int, message: str, name: str, city: str
) -> Path | None:
    """
    Рендерит превью и сохраняет в data/generated/. Возвращает путь к файлу.
    Используется при отправке сообщения на модерацию.
    """
    img = _render_preview(background_id, message, name, city)
    if img is None:
        return None

    generated_dir = get_data_dir() / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)

    output_path = generated_dir / f"{uuid.uuid4().hex}.png"
    img.save(output_path, "PNG")
    logger.info(f"Сгенерировано превью фона {background_id}: {output_path}")
    return output_path


def build_preview_url(filename: str) -> str:
    """Строит публичный URL к превью: {BOT_WEBHOOK_URL}/previews/{filename}."""
    base = Config.BOT_WEBHOOK_URL.rstrip("/")
    return f"{base}/previews/{filename}"
