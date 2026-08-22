from __future__ import annotations

import re
from pathlib import Path

PRIVATE_PATTERN = re.compile(r"(?:drive\.google\.com|docs\.google\.com|file:///|C:\\Users\\)", re.IGNORECASE)


def validate_records(records_root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted(records_root.rglob("*.json")):
        if PRIVATE_PATTERN.search(path.read_text(encoding="utf-8", errors="replace")):
            errors.append(f"private identifier found: {path.name}")
    return errors
