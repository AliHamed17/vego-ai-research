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


def reject_reparse_components(
    candidate: Path,
    field_name: str,
    error_type: type[Exception],
    *,
    containment_anchor: Path | None = None,
) -> None:
    """Reject redirects in every existing component before resolving or probing a leaf."""
    absolute_candidate = _absolute_lexical(candidate)
    if containment_anchor is not None:
        absolute_anchor = _absolute_lexical(containment_anchor)
        try:
            absolute_candidate.relative_to(absolute_anchor)
        except ValueError as error:
            raise error_type(f"{field_name} escapes its approved root") from error
    current = Path(absolute_candidate.anchor)
    reject_reparse_entry(current, field_name, error_type)
    for part in absolute_candidate.parts[1:]:
        current /= part
        reject_reparse_entry(current, field_name, error_type)


def resolve_local_directory(
    path: Path,
    field_name: str,
    error_type: type[Exception],
    *,
    containment_root: Path | None = None,
) -> Path:
    """Resolve one existing local directory only after all components are non-redirecting."""
    candidate = _absolute_lexical(path)
    reject_reparse_components(candidate, field_name, error_type)
    try:
        metadata = candidate.lstat()
    except OSError as error:
        raise error_type(f"{field_name} must be an existing local directory") from error
    if not stat.S_ISDIR(metadata.st_mode):
        raise error_type(f"{field_name} must be an existing local directory")
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as error:
        raise error_type(f"{field_name} must be an existing local directory") from error
    reject_reparse_components(candidate, field_name, error_type)
    if containment_root is not None:
        root_candidate = _absolute_lexical(containment_root)
        reject_reparse_components(root_candidate, field_name, error_type)
        try:
            root = root_candidate.resolve(strict=True)
        except OSError as error:
            raise error_type(f"{field_name} selected source root is unavailable") from error
        if not _is_within(resolved, root):
            raise error_type(f"{field_name} resolved outside its selected source root")
    return resolved


def validate_private_output_root(
    value: str | Path,
    repository_root: str | Path,
    error_type: type[Exception],
) -> Path:
    """Authorize exactly one ignored, repository-owned Study 1 private destination."""
    candidate = _absolute_lexical(local_path(value, "private_output_root", error_type))
    repository_candidate = _absolute_lexical(
        local_path(repository_root, "repository_root", error_type)
    )
    repository = resolve_local_directory(
        repository_candidate, "repository_root", error_type
    )
    private_base = repository / "research-private" / "study1"
    if not _is_within(candidate, private_base):
        raise error_type(
            "private_output_root must be beneath this repository's research-private/study1"
        )
    reject_reparse_components(
        candidate,
        "private_output_root",
        error_type,
        containment_anchor=repository,
    )
    resolved_candidate = candidate.resolve(strict=False)
    resolved_base = private_base.resolve(strict=False)
    if not _is_within(resolved_candidate, resolved_base):
        raise error_type(
            "private_output_root must resolve beneath this repository's research-private/study1"
        )
    reject_reparse_components(
        candidate,
        "private_output_root",
        error_type,
        containment_anchor=repository,
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
        reject_reparse_components(
            current,
            field_name,
            error_type,
            containment_anchor=repository_root,
        )
        try:
            current.mkdir()
        except FileExistsError:
            pass
        except OSError as error:
            raise error_type(f"{field_name} directory creation failed") from error
        reject_reparse_components(
            current,
            field_name,
            error_type,
            containment_anchor=repository_root,
        )
        try:
            metadata = current.lstat()
        except OSError as error:
            raise error_type(f"{field_name} directory verification failed") from error
        if not stat.S_ISDIR(metadata.st_mode):
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
    repository = resolve_local_directory(
        local_path(repository_root, "repository_root", error_type),
        "repository_root",
        error_type,
    )
    reject_reparse_components(
        candidate,
        "private directory",
        error_type,
        containment_anchor=repository,
    )
    _mkdir_without_reparse(candidate, repository, "private directory", error_type)
    validate_private_output_root(root, repository, error_type)
    reject_reparse_components(
        candidate,
        "private directory",
        error_type,
        containment_anchor=repository,
    )
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
    reject_reparse_components(candidate, field_name, error_type)
    try:
        metadata = candidate.lstat()
        if not stat.S_ISREG(metadata.st_mode):
            raise OSError("not a regular file")
        resolved = candidate.resolve(strict=True)
    except OSError as error:
        raise error_type(f"{field_name} must be a readable local file") from error
    resolved_root: Path | None = None
    if containment_root is not None:
        root_candidate = _absolute_lexical(containment_root)
        reject_reparse_components(root_candidate, field_name, error_type)
        try:
            resolved_root = root_candidate.resolve(strict=True)
        except OSError as error:
            raise error_type(f"{field_name} selected source root is unavailable") from error
        if not _is_within(resolved, resolved_root):
            raise error_type(f"{field_name} resolved outside its selected source root")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(candidate, flags)
        with os.fdopen(descriptor, "rb") as stream:
            opened_metadata = os.fstat(stream.fileno())
            if not stat.S_ISREG(opened_metadata.st_mode):
                raise error_type(f"{field_name} must be a readable regular local file")
            reject_reparse_components(candidate, field_name, error_type)
            resolved_after_open = candidate.resolve(strict=True)
            if resolved_after_open != resolved:
                raise error_type(f"{field_name} changed while it was opened")
            if resolved_root is not None and not _is_within(resolved_after_open, resolved_root):
                raise error_type(f"{field_name} resolved outside its selected source root")
            current_metadata = candidate.lstat()
            if (
                getattr(current_metadata, "st_dev", None),
                getattr(current_metadata, "st_ino", None),
            ) != (
                getattr(opened_metadata, "st_dev", None),
                getattr(opened_metadata, "st_ino", None),
            ):
                raise error_type(f"{field_name} changed while it was opened")
            return stream.read()
    except OSError as error:
        raise error_type(f"{field_name} must be a readable local file") from error


def reject_path_alias(
    source: Path,
    destination: Path,
    field_name: str,
    error_type: type[Exception],
) -> None:
    """Reject lexical, resolved, or same-file aliases without following unsafe components."""
    source_candidate = _absolute_lexical(source)
    destination_candidate = _absolute_lexical(destination)
    if source_candidate == destination_candidate:
        raise error_type(f"{field_name} must not be a receipt destination alias")
    reject_reparse_components(source_candidate, field_name, error_type)
    reject_reparse_components(destination_candidate, "receipt destination", error_type)
    if source_candidate.resolve(strict=False) == destination_candidate.resolve(strict=False):
        raise error_type(f"{field_name} must not be a receipt destination alias")
    try:
        source_candidate.lstat()
        destination_candidate.lstat()
    except FileNotFoundError:
        return
    except OSError as error:
        raise error_type(f"{field_name} alias check failed") from error
    try:
        aliases = os.path.samefile(source_candidate, destination_candidate)
    except OSError as error:
        raise error_type(f"{field_name} alias check failed") from error
    reject_reparse_components(source_candidate, field_name, error_type)
    reject_reparse_components(destination_candidate, "receipt destination", error_type)
    if aliases:
        raise error_type(f"{field_name} must not be a receipt destination alias")


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
    reject_reparse_components(
        target,
        "private destination",
        error_type,
        containment_anchor=root,
    )
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
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise error_type("private destination temporary file is not regular")
            stream.write(content.encode("utf-8"))
            stream.flush()
            os.fsync(stream.fileno())
        validate_private_output_root(root, repository_root, error_type)
        reject_reparse_components(
            parent,
            "private destination",
            error_type,
            containment_anchor=resolve_local_directory(
                local_path(repository_root, "repository_root", error_type),
                "repository_root",
                error_type,
            ),
        )
        reject_reparse_components(
            target,
            "private destination",
            error_type,
            containment_anchor=root,
        )
        os.replace(temporary, target)
    except OSError as error:
        raise error_type("private destination atomic write failed") from error
    finally:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
