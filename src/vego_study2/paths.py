from __future__ import annotations

import os
from pathlib import Path


class UnsafeOutputPathError(ValueError):
    """Raised when an output path escapes the approved private root."""


def _has_reparse_point(path: Path) -> bool:
    try:
        return bool(path.lstat().st_file_attributes & getattr(os, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))
    except (AttributeError, FileNotFoundError, OSError):
        return False


def ensure_safe_output_root(output_root: Path, allowed_root: Path) -> Path:
    """Return a resolved output path only when it is a non-symlink child root.

    The check is intentionally independent of the runner so callers can test
    path policy before creating any output.  Missing final components are
    allowed; every existing ancestor must be a normal directory.
    """
    candidate = Path(output_root)
    root = Path(allowed_root)
    if not candidate.is_absolute() or not root.is_absolute():
        raise UnsafeOutputPathError("output and allowed roots must be absolute")
    if any(part in {"", "."} for part in candidate.parts):
        raise UnsafeOutputPathError("invalid output path component")

    root_absolute = root.absolute()
    candidate_absolute = candidate.absolute()
    try:
        lexical_parts = candidate_absolute.relative_to(root_absolute).parts
    except ValueError as exc:
        raise UnsafeOutputPathError("output path escapes approved root") from exc

    # Inspect the lexical path before resolving it.  This catches a symlink
    # which happens to point back inside the approved root.
    current_lexical = root_absolute
    if _has_reparse_point(current_lexical):
        raise UnsafeOutputPathError("approved root is a reparse point")
    for part in lexical_parts:
        current_lexical = current_lexical / part
        if current_lexical.exists() and _has_reparse_point(current_lexical):
            raise UnsafeOutputPathError("output path contains a symlink or reparse point")

    root_resolved = root_absolute.resolve(strict=False)
    candidate_resolved = candidate_absolute.resolve(strict=False)
    try:
        candidate_resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise UnsafeOutputPathError("output path escapes approved root") from exc

    current = root_resolved
    for part in candidate_resolved.relative_to(root_resolved).parts:
        current = current / part
        if current.exists() and not current.is_dir():
            raise UnsafeOutputPathError("output path component is not a directory")
    return candidate_resolved
