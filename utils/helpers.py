import re
from pathlib import Path

# Matches all known Pinterest URL variants
_PINTEREST_RE = re.compile(
    r"https?://(www\.)?(pin\.it|pinterest\.[a-z.]+)/",
    re.IGNORECASE,
)

# Telegram Bot API upload limit
MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB


def is_pinterest_url(text: str) -> bool:
    """Return True if text contains a Pinterest link."""
    return bool(_PINTEREST_RE.search(text.strip()))


def extract_pinterest_url(text: str) -> str | None:
    """Extract the first Pinterest URL found in text, or None."""
    match = _PINTEREST_RE.search(text.strip())
    if not match:
        return None
    # Return from the start of the match to the end of the word
    start = match.start()
    # Grab until whitespace
    end = len(text)
    for i in range(start, len(text)):
        if text[i] in (" ", "\n", "\t"):
            end = i
            break
    return text[start:end]


def file_size(path: str) -> int:
    """Return file size in bytes."""
    return Path(path).stat().st_size


def is_within_telegram_limit(path: str) -> bool:
    return file_size(path) <= MAX_UPLOAD_BYTES
