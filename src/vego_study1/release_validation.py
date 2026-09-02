"""Validate Git object bytes from one resolved Study 1 branch comparison."""

from __future__ import annotations

import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .path_safety import local_path, read_local_bytes, resolve_local_directory
from .privacy import public_artifact_byte_findings, public_path_finding_kinds


class ReleaseValidationError(ValueError):
    """Raised when the selected Git diff cannot be safely validated."""


@dataclass(frozen=True)
class ReleaseFinding:
    """A prohibited public reference found in a proposed tracked artifact."""

    path: Path
    line: int
    kind: str


@dataclass(frozen=True)
class ReleaseScan:
    """One immutable scan result bound to resolved base and head commits."""

    base_commit: str
    head_commit: str
    paths: tuple[Path, ...]
    findings: tuple[ReleaseFinding, ...]


@dataclass(frozen=True)
class TreeEntry:
    """One exact non-tree entry from a resolved Git commit tree."""

    path: PurePosixPath
    mode: str
    object_type: str
    object_id: str


# Binary exceptions are exact repository-relative paths reviewed as intrinsically public-safe.
# Study 1 currently has no such exception; extensions and directories are intentionally insufficient.
SAFE_BINARY_PATHS: frozenset[str] = frozenset()
# Non-regular exceptions require an exact path, mode, and object type review.
SAFE_NON_REGULAR_ENTRIES: frozenset[tuple[str, str, str]] = frozenset()


def _run_git(repository_root: Path, *arguments: str) -> bytes:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repository_root), *arguments],
            check=False,
            capture_output=True,
        )
    except OSError as error:
        raise ReleaseValidationError("Git diff could not be executed") from error
    if completed.returncode != 0:
        raise ReleaseValidationError("Git diff could not resolve the selected branch comparison")
    return completed.stdout


def _resolve_commit(repository_root: Path, reference: str) -> str:
    output = _run_git(repository_root, "rev-parse", "--verify", f"{reference}^{{commit}}")
    try:
        commit = output.decode("ascii").strip()
    except UnicodeDecodeError as error:
        raise ReleaseValidationError("Git diff returned an invalid commit identifier") from error
    if not commit or any(character not in "0123456789abcdefABCDEF" for character in commit):
        raise ReleaseValidationError("Git diff returned an invalid commit identifier")
    return commit.lower()


def _relative_tracked_paths(
    repository_root: Path, base_commit: str, head_commit: str
) -> list[PurePosixPath]:
    output = _run_git(
        repository_root,
        "diff",
        "--name-only",
        "-z",
        "--no-renames",
        "--diff-filter=ACMRT",
        f"{base_commit}...{head_commit}",
    )
    if output and not output.endswith(b"\0"):
        raise ReleaseValidationError("Git diff returned an invalid path stream")
    paths: list[PurePosixPath] = []
    raw_values = output[:-1].split(b"\0") if output else []
    if any(not raw_value for raw_value in raw_values):
        raise ReleaseValidationError("Git diff returned an invalid path stream")
    for raw_value in raw_values:
        try:
            value = raw_value.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ReleaseValidationError("Git diff returned an undecodable path") from error
        candidate = PurePosixPath(value)
        if (
            candidate.is_absolute()
            or ".." in candidate.parts
            or not candidate.parts
            or "\\" in value
            or (len(value) >= 2 and value[0].isalpha() and value[1] == ":")
        ):
            raise ReleaseValidationError("Git diff returned a path outside the repository")
        paths.append(candidate)
    return paths


def _head_tree_entries(repository_root: Path, head_commit: str) -> dict[PurePosixPath, TreeEntry]:
    output = _run_git(repository_root, "ls-tree", "-r", "-z", "--full-tree", head_commit)
    if output and not output.endswith(b"\0"):
        raise ReleaseValidationError("Git tree returned an invalid entry stream")
    entries: dict[PurePosixPath, TreeEntry] = {}
    for record in output[:-1].split(b"\0") if output else []:
        if b"\t" not in record:
            raise ReleaseValidationError("Git tree returned an invalid entry")
        metadata, raw_path = record.split(b"\t", 1)
        try:
            mode, object_type, object_id = metadata.decode("ascii").split()
            value = raw_path.decode("utf-8")
        except (UnicodeDecodeError, ValueError) as error:
            raise ReleaseValidationError("Git tree returned an undecodable entry") from error
        path = PurePosixPath(value)
        if (
            path.is_absolute()
            or ".." in path.parts
            or not path.parts
            or "\\" in value
            or (len(value) >= 2 and value[0].isalpha() and value[1] == ":")
        ):
            raise ReleaseValidationError("Git tree returned a path outside the repository")
        if path in entries:
            raise ReleaseValidationError("Git tree returned a duplicate entry")
        if not object_id or any(character not in "0123456789abcdefABCDEF" for character in object_id):
            raise ReleaseValidationError("Git tree returned an invalid object identifier")
        entries[path] = TreeEntry(path, mode, object_type, object_id.lower())
    return entries


def _blob_bytes(repository_root: Path, object_id: str) -> bytes:
    return _run_git(repository_root, "cat-file", "blob", object_id)


def _findings_for_bytes(path: Path, content: bytes, relative_path: str) -> list[ReleaseFinding]:
    if b"\0" in content:
        if relative_path in SAFE_BINARY_PATHS:
            return []
        return [ReleaseFinding(path=path, line=1, kind="undecodable_or_binary_blob")]
    try:
        content.decode("utf-8")
    except UnicodeDecodeError:
        if relative_path in SAFE_BINARY_PATHS:
            return []
        return [ReleaseFinding(path=path, line=1, kind="undecodable_or_binary_blob")]
    return [
        ReleaseFinding(
            path=path,
            line=line_number,
            kind=(
                "undecodable_or_binary_blob"
                if kind == "undecodable_or_binary_artifact"
                else kind
            ),
        )
        for line_number, kind in public_artifact_byte_findings(
            content, relative_path=relative_path
        )
    ]


def scan_release_diff(
    repository_root: str | Path, *, base_ref: str, head_ref: str = "HEAD"
) -> ReleaseScan:
    """Resolve both refs once, then scan changed blobs from the resolved head object."""
    root = resolve_local_directory(
        local_path(repository_root, "repository_root", ReleaseValidationError),
        "repository_root",
        ReleaseValidationError,
    )
    base_commit = _resolve_commit(root, base_ref)
    head_commit = _resolve_commit(root, head_ref)
    relative_paths = _relative_tracked_paths(root, base_commit, head_commit)
    tree_entries = _head_tree_entries(root, head_commit)
    findings: list[ReleaseFinding] = []
    public_paths: list[Path] = []
    for relative_path in relative_paths:
        public_path = root.joinpath(*relative_path.parts)
        public_paths.append(public_path)
        findings.extend(
            ReleaseFinding(path=public_path, line=1, kind=kind)
            for kind in public_path_finding_kinds(relative_path.as_posix())
        )
        entry = tree_entries.get(relative_path)
        if entry is None:
            raise ReleaseValidationError("Git diff entry is missing from the resolved head tree")
        entry_identity = (
            relative_path.as_posix(),
            entry.mode,
            entry.object_type,
        )
        non_regular = entry.mode not in {"100644", "100755"} or entry.object_type != "blob"
        if non_regular:
            if entry_identity not in SAFE_NON_REGULAR_ENTRIES:
                findings.append(
                    ReleaseFinding(path=public_path, line=1, kind="non_regular_tree_entry")
                )
                continue
            if entry.object_type != "blob":
                continue
        content = _blob_bytes(root, entry.object_id)
        findings.extend(_findings_for_bytes(public_path, content, relative_path.as_posix()))
    return ReleaseScan(
        base_commit=base_commit,
        head_commit=head_commit,
        paths=tuple(public_paths),
        findings=tuple(findings),
    )


def proposed_tracked_paths(
    repository_root: str | Path, *, base_ref: str, head_ref: str = "HEAD"
) -> list[Path]:
    """Return changed paths from the resolved Git comparison, independent of worktree state."""
    return list(scan_release_diff(repository_root, base_ref=base_ref, head_ref=head_ref).paths)


def validate_release_paths(paths: Iterable[Path]) -> list[ReleaseFinding]:
    """Find prohibited references in explicitly selected local artifacts."""
    findings: list[ReleaseFinding] = []
    for path in paths:
        candidate = Path(path)
        content = read_local_bytes(
            candidate,
            "selected release artifact",
            ReleaseValidationError,
        )
        findings.extend(_findings_for_bytes(candidate, content, candidate.as_posix()))
    return findings


def validate_release_diff(
    repository_root: str | Path, *, base_ref: str, head_ref: str = "HEAD"
) -> list[ReleaseFinding]:
    """Scan only resolved proposed Git blobs; never read changed worktree bytes."""
    return list(scan_release_diff(repository_root, base_ref=base_ref, head_ref=head_ref).findings)
