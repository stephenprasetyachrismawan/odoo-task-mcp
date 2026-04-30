from __future__ import annotations

import re

SECRET_PATTERNS = [
    re.compile(r"\b[A-Za-z0-9_\-]{24,}\b"),
]


def redact_text(text: str) -> str:
    redacted = text
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted
