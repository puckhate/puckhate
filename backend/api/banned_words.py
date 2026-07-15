import json
import logging
import re
import unicodedata
from pathlib import Path

logger = logging.getLogger(__name__)

_BANNED_WORDS_FILE = Path(__file__).resolve().parent / "banned_words.json"
_TOKEN_SPLIT_RE = re.compile(r"[\W_]+", re.UNICODE)


def _normalize(text: str) -> str:
    """Fold look-alike forms and drop invisible characters before matching."""
    normalized = unicodedata.normalize("NFKC", text)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Cf")


def _load_banned_words() -> frozenset[str]:
    # The list is git-secret encrypted, so the plaintext file is absent until the
    # deploy runs `git secret reveal`. Warn the user if the file is missing.
    try:
        with _BANNED_WORDS_FILE.open(encoding="utf-8") as fh:
            words = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning(
            "Banned-word list unavailable (%s); screening is disabled. Create backend/api/banned_words.json to enable.",
            exc,
        )
        return frozenset()
    if not isinstance(words, list):
        logger.warning(
            "Banned-word list must be a JSON array, got %s; screening is disabled.",
            type(words).__name__,
        )
        return frozenset()
    # Normalize entries the same way incoming text is normalized
    normalized = (
        _normalize(word).strip().lower() for word in words if isinstance(word, str)
    )
    # Skip non-string / blank entries rather than crashing at import
    return frozenset(word for word in normalized if word)


# Loaded once at import, requires a server restart to load a new list
BANNED_WORDS = _load_banned_words()


def contains_banned_word(text: str) -> str | None:
    """Return the first banned word found in `text`, or None if clean.

    Matching is case-insensitive and whole-word
    """
    if not text or not BANNED_WORDS:
        return None
    for token in _TOKEN_SPLIT_RE.split(_normalize(text).lower()):
        if token in BANNED_WORDS:
            return token
    return None
