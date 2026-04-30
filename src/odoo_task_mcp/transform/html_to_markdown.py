from __future__ import annotations

import bleach
from markdownify import markdownify as md


def html_to_markdown(html: str | None) -> str:
    if not html:
        return ""
    allowed_tags = bleach.sanitizer.ALLOWED_TAGS | {"p", "br", "ul", "ol", "li"}
    cleaned = bleach.clean(html, tags=allowed_tags, strip=True)
    return md(cleaned).strip()
