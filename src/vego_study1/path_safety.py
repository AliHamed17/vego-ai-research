"""Shared fail-closed local path and private-write safeguards for Study 1."""

from __future__ import annotations

import os
import re
import secrets
import stat
import subprocess
from pathlib import Path

_URI_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:[\\/]")
_REPARSE_ATTRIBUTE = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


def is_remote_value(value: str | Path) -> bool:
    """Return whether a lexical path value names a URI or UNC/network path."""
    raw_value = str(value)
    return raw_value.startswith((r"\\", "//")) or (
        bool(_URI_SCHEME.match(raw_value)) and not bool(_WINDOWS_DRIVE.match(raw_value))
    )


def local_path(value: str | Path, field_name: str, error_type: type[Exception]) -> Path:
    """Reject remote syntax before any filesystem operation and return a lexical path."""
    if is_remote_value(value):
        raise error_type(f"{field_name} must not be a remote URL, URI, or UNC path")
    return Path(value)


def _absolute_lexical(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def _is_within(candidate: Path, parent: Path) -> bool:
    try:
        candidate.relative_to(parent)
    except ValueError:
        return False
    return True


def is_reparse_point(path: Path) -> bool:
    """Detect a symlink or Windows reparse point without following the entry."""
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return False
    return path.is_symlink() or bool(
        getattr(metadata, "st_file_attributes", 0) & _REPARSE_ATTRIBUTE
    )


def reject_reparse_entry(path: Path, field_name: str, error_type: type[Exception]) -> None:
    """Reject one existing source or destination entry that redirects elsewhere."""
    try:
        redirected = is_reparse_point(path)
    except OSError as error:
        raise error_type(f"{field_name} reparse-point check failed") from error
    if redirected:
        raise error_type(f"{field_name} must not be a symlink or reparse point")


def _reject_reparse_components(
    candidate: Path,
    anchor: Path,
    field_name: str,
    error_type: type[Exception],
) -> None:
    try:
        relative = candidate.relative_to(anchor)
    except ValueError as error:
        raise error_type(f"{field_name} escapes its approved root") from error
    current = anchor
    for part in relative.parts:
        current /= part
        reject_reparse_entry(current, field_name, error_type)


def validate_private_output_root(
    value: str | Path,
    repository_root: str | Path,
    error_type: type[Exception],
) -> Path:
    """Authorize exactly one ignored, repository-owned Study 1 private destination."""
    candidate = _absolute_lexical(local_path(value, "private_output_root", error_type))
    repository = Path(repository_root).resolve()
    private_base = repository / "research-private" / "study1"
    if not _is_within(candidate, private_base):
        raise error_type(
            "private_output_root must be beneath this repository's research-private/study1"
        )
    _reject_reparse_components(candidate, repository, "private_output_root", error_type)
    resolved_candidate = candidate.resolve(strict=False)
    resolved_base = private_base.resolve(strict=False)
    if not _is_within(resolved_candidate, resolved_base):
        raise error_type(
            "private_output_root must resolve beneath this repository's research-private/study1"
        )
    try:
        relative = candidate.relative_to(repository)
        ignored = (
            subprocess.run(
                ["git", "-C", str(repository), "check-ignore", "-q", "--", str(relative)],
                capture_output=True,
                check=False,
            ).returncode
            == 0
        )
    except OSError as error:
        raise error_type("private_output_root Git-ignore check failed") from error
    if not ignored:
        raise error_type("private_output_root must pass the repository Git-ignore check")
    return candidate


def _mkdir_without_reparse(
    directory: Path,
    repository_root: Path,
    field_name: str,
    error_type: type[Exception],
) -> None:
    relative = directory.relative_to(repository_root)
    current = repository_root
    for part in relative.parts:
        current /= part
        reject_reparse_entry(current, field_name, error_type)
        try:
            current.mkdir()
        except FileExistsError:
            pass
        except OSError as error:
            raise error_type(f"{field_name} directory creation failed") from error
        reject_reparse_entry(current, field_name, error_type)
        if not current.is_dir():
            raise error_type(f"{field_name} must contain only local directories")


def ensure_private_directory(
    directory: str | Path,
    private_output_root: str | Path,
    repository_root: str | Path,
    error_type: type[Exception],
) -> Path:
    """Create a directory below an authorized root one non-reparse component at a time."""
    root = validate_private_output_root(private_output_root, repository_root, error_type)
    candidate = _absolute_lexical(local_path(directory, "private directory", error_type))
    if not _is_within(candidate, root):
        raise error_type("private directory escapes private_output_root")
    repository = Path(repository_root).resolve()
    _reject_reparse_components(candidate, repository, "private directory", error_type)
    _mkdir_without_reparse(candidate, repository, "private directory", error_type)
    validate_private_output_root(root, repository, error_type)
    _reject_reparse_components(candidate, repository, "private directory", error_type)
    if not _is_within(candidate.resolve(strict=True), root.resolve(strict=True)):
        raise error_type("private directory resolved outside private_output_root")
    return candidate


def read_local_bytes(
    path: Path,
    field_name: str,
    error_type: type[Exception],
    *,
    containment_root: Path | None = None,
) -> bytes:
    """Read a regular local file after immediate no-redirect and containment checks."""
    candidate = _absolute_lexical(path)
    reject_reparse_entry(candidate, field_name, error_type)
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as error:
        raise error_type(f"{field_name} must be a readable local file") from error
    if containment_root is not None and not _is_within(
        resolved, containment_root.resolve(strict=True)
    ):
        raise error_type(f"{field_name} resolved outside its selected source root")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(candidate, flags)
        with os.fdopen(descriptor, "rb") as stream:
            return stream.read()
    except OSError as error:
        raise error_type(f"{field_name} must be a readable local file") from error


def assert_local_file_unchanged(
    path: Path,
    expected: bytes,
    field_name: str,
    error_type: type[Exception],
) -> None:
    """Fail closed when a local input no longer matches its immutable snapshot."""
    if read_local_bytes(path, field_name, error_type) != expected:
        raise error_type(f"{field_name} changed after its immutable snapshot was read")


def atomic_write_private_text(
    destination: str | Path,
    content: str,
    private_output_root: str | Path,
    repository_root: str | Path,
    error_type: type[Exception],
) -> None:
    """Atomically replace one regular private file without following a destination leaf."""
    root = validate_private_output_root(private_output_root, repository_root, error_type)
    target = _absolute_lexical(local_path(destination, "private destination", error_type))
    if not _is_within(target, root):
        raise error_type("private destination escapes private_output_root")
    parent = ensure_private_directory(target.parent, root, repository_root, error_type)
    reject_reparse_entry(target, "private destination", error_type)
    temporary = parent / f".{target.name}.{secrets.token_hex(8)}.tmp"
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_BINARY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        descriptor = os.open(temporary, flags, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content.encode("utf-8"))
            stream.flush()
            os.fsync(stream.fileno())
        validate_private_output_root(root, repository_root, error_type)
        _reject_reparse_components(
            parent, Path(repository_root).resolve(), "private destination", error_type
        )
        reject_reparse_entry(target, "private destination", error_type)
        os.replace(temporary, target)
    except OSError as error:
        raise error_type("private destination atomic write failed") from error
    finally:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
