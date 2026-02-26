"""Сервис для работы с фонами."""

import io
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
    text_color = "white"
    city_color = "#CD3782"

    # Текстовая зона привязана к блоку в макете:
    # x=42, y=433, w=636, h=240, padding=(26,39,26,39) для базового фона 720x760.
    sx = W / 720
    sy = H / 760
    block_left = int(round(42 * sx))
    block_top = int(round(433 * sy))
    block_w = int(round(636 * sx))
    block_h = int(round(240 * sy))
    pad_top = int(round(26 * sy))
    pad_right = int(round(39 * sx))
    pad_bottom = int(round(26 * sy))
    pad_left = int(round(39 * sx))

    margin_left = block_left + pad_left
    usable_w = max(block_w - pad_left - pad_right, 1)
    content_top = block_top + pad_top
    usable_h = max(block_h - pad_top - pad_bottom, 1)

    # Текстовый блок имени/города в верхней плашке:
    # top=340, left=181, right=172, gap=14 (в макете 720x760).
    header_top = int(round(340 * sy))
    header_left = int(round(181 * sx))
    header_right = int(round(172 * sx))
    header_w = max(W - header_left - header_right, 1)

    # Загрузка шрифтов.
    font_path = get_data_dir() / "Max Sans DemiBold.ttf"
    font_light_path = get_data_dir() / "Max Sans Light.ttf"

    # Визуальная компенсация: на рендере 43px выглядит немного меньше макета.
    message_font_scale = 1.08
    # Дизайн: font-size 43px, line-height 115%
    size_large = max(int(round(43 * sy * message_font_scale)), 14)
    size_small = max(int(round(30 * sy)), 12)
    line_height_mult = 1.15
    name_size = max(int(round(32 * sy)), 12)
    city_size = max(int(round(27 * sy)), 10)
    name_city_gap = int(round(14 * sy))

    def _fit_line(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> str:
        """Обрезает строку в одну линию с троеточием по ширине."""
        value = (text or "").strip()
        if not value:
            return ""
        if int(font.getlength(value)) <= max_w:
            return value
        ellipsis = "..."
        out = value
        while out and int(font.getlength(out + ellipsis)) > max_w:
            out = out[:-1]
        return (out + ellipsis) if out else ellipsis

    def _load_fonts(sz_l: int, sz_s: int) -> tuple[ImageFont.FreeTypeFont, ImageFont.FreeTypeFont]:
        base_path = font_path if font_path.is_file() else font_light_path
        return (
            ImageFont.truetype(str(base_path), sz_l),
            ImageFont.truetype(str(base_path), sz_s),
        )

    def _token_width(token: str, is_emoji: bool, font: ImageFont.FreeTypeFont) -> float:
        """Реальная ширина токена в пикселях."""
        if is_emoji:
            return float(max(int(font.size * 1.10), 12))
        return float(font.getlength(token))

    def _wrap_pixels(text: str, font: ImageFont.FreeTypeFont) -> list[str]:
        """Переносит текст по реальной пиксельной ширине с учётом emoji."""
        words = text.split(" ")
        lines: list[str] = []
        current = ""
        current_w = 0.0

        for word in words:
            tokens = _tokenize_word(word, font)
            word_w = sum(_token_width(t, ie, font) for t, ie in tokens)
            space_w = font.getlength(" ") if current else 0.0

            if current and current_w + space_w + word_w > usable_w:
                lines.append(current)
                current = word
                current_w = word_w
            else:
                current = (current + " " + word) if current else word
                current_w = current_w + space_w + word_w

        if current:
            lines.append(current)
        return lines or [""]

    def _tokenize_word(text: str, font: ImageFont.FreeTypeFont) -> list[tuple[str, bool]]:
        """Токенизирует слово на текст/emoji (аналог _tokenize_line, но без зависимости от порядка объявления)."""
        tokens: list[tuple[str, bool]] = []
        i = 0
        while i < len(text):
            matched = False
            for emoji in _EMOJI_SORTED:
                if text.startswith(emoji, i):
                    tokens.append((emoji, True))
                    i += len(emoji)
                    matched = True
                    break
            if not matched:
                tokens.append((text[i], False))
                i += 1
        return tokens

    def _line_h(sz_l: int) -> int:
        return max(int(round(sz_l * line_height_mult)), 1)

    def _sig_gap(sz_l: int) -> int:
        return max(int(round(sz_l * 0.9)), 10)

    def _block_h(n_lines: int, sz_l: int, sz_s: int, has_signature: bool) -> int:
        h = n_lines * _line_h(sz_l)
        if has_signature:
            h += _sig_gap(sz_l) + sz_s
        return h

    font_large, font_small = _load_fonts(size_large, size_small)
    wrapped_lines = _wrap_pixels(message, font_large)
    has_signature = False

    # Уменьшаем шрифт пока блок не помещается по высоте
    while _block_h(len(wrapped_lines), size_large, size_small, has_signature) > usable_h and size_large > 18:
        size_large = max(size_large - 2, 14)
        size_small = max(int(size_large * 0.70), 14)
        font_large, font_small = _load_fonts(size_large, size_small)
        wrapped_lines = _wrap_pixels(message, font_large)

    logger.info(f"Шрифт: {font_path}, size={size_large}, строк={len(wrapped_lines)}")

    # Имя/город в верхней зоне.
    name_font_path = font_path if font_path.is_file() else font_light_path
    city_font_path = font_light_path if font_light_path.is_file() else name_font_path
    name_font = ImageFont.truetype(str(name_font_path), name_size)
    city_font = ImageFont.truetype(str(city_font_path), city_size)
    safe_name = _fit_line(name, name_font, header_w)
    safe_city = _fit_line(city, city_font, header_w)
    if safe_name:
        draw.text((header_left, header_top), safe_name, font=name_font, fill=text_color, anchor="la")
    if safe_city:
        city_top = header_top + name_size + name_city_gap
        draw.text((header_left, city_top), safe_city, font=city_font, fill=city_color, anchor="la")

    def _draw_with_shadow(
        d: ImageDraw.ImageDraw,
        pos: tuple[float, float],
        text: str,
        font: ImageFont.FreeTypeFont,
    ) -> None:
        x, y = pos
        d.text((x + 1, y + 1), text, font=font, fill=(0, 0, 0, 140), anchor="lm")
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
        x = float(margin_left)

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

    line_h = _line_h(size_large)
    total_lines = len(wrapped_lines)
    text_block_h = total_lines * line_h
    top_offset = max((usable_h - text_block_h) // 2, 0)
    start_y = content_top + top_offset + line_h // 2

    for i, line in enumerate(wrapped_lines):
        _draw_line_with_emoji(draw, start_y + i * line_h, line, font_large)

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
