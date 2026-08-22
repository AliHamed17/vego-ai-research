from __future__ import annotations

import os
from pathlib import Path

_DENIED_SUFFIXES = {".env", ".exe", ".msi", ".bat", ".cmd", ".ps1", ".dll", ".key", ".pem", ".pfx"}
_ALLOWED_SUFFIXES = {
    ".csv",
    ".docx",
    ".eml",
    ".m4a",
    ".md",
    ".mp3",
    ".mp4",
    ".pdf",
    ".pptx",
    ".rtf",
    ".srt",
    ".txt",
    ".vtt",
    ".wav",
    ".xlsx",
}
_DENIED_NAMES = {
    "id_rsa",
    "id_ed25519",
    "credentials",
    "credentials.json",
    "cookies",
    "history",
    "login data",
    "tokens.json",
    "web data",
}
_DENIED_PATH_PARTS = {"appdata", "program files", "program files (x86)", "windows"}


def _is_reparse_point(path: Path) -> bool:
    try:
        attributes = os.lstat(path).st_file_attributes
    except OSError:
        return True
    except AttributeError:
        attributes = 0
    return path.is_symlink() or bool(attributes & 0x400)


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=True).relative_to(root.resolve(strict=True))
    except (FileNotFoundError, ValueError):
        return False
    return True


def is_allowed_file(path: Path, *, approved_roots: tuple[Path, ...]) -> bool:
    """Fail closed for executable, credential, and browser-profile files."""

    if not path.is_file() or not approved_roots:
        return False
    name = path.name.casefold()
    suffix = path.suffix.casefold()
    if suffix not in _ALLOWED_SUFFIXES or suffix in _DENIED_SUFFIXES or name in _DENIED_NAMES:
        return False
    if _DENIED_PATH_PARTS.intersection(part.casefold() for part in path.parts):
        return False
    for parent in (path, *path.parents):
        if _is_reparse_point(parent):
            return False
    return any(_is_within(path, root) for root in approved_roots)
