"""Валидация текста по whitelist символов и эмодзи."""

from core.config import Config
from core.emoji_whitelist import EMOJI_WHITELIST

_EMOJI_BY_FIRST_CHAR: dict[str, list[str]] = {}
for emoji in sorted(EMOJI_WHITELIST, key=len, reverse=True):
    first = emoji[0]
    _EMOJI_BY_FIRST_CHAR.setdefault(first, []).append(emoji)


def is_text_allowed(text: str) -> bool:
    """Проверяет, что текст состоит из ALLOWED_CHARACTERS и разрешённых emoji."""
    i = 0
    while i < len(text):
        char = text[i]
        if char in Config.ALLOWED_CHARACTERS:
            i += 1
            continue

        matched = False
        for emoji in _EMOJI_BY_FIRST_CHAR.get(char, []):
            if text.startswith(emoji, i):
                i += len(emoji)
                matched = True
                break

        if not matched:
            return False

    return True
