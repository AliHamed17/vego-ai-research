"""Validate Git object bytes from one resolved Study 1 branch comparison."""

from __future__ import annotations

import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .privacy import PUBLIC_ARTIFACT_PATTERNS


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


# Binary exceptions are exact repository-relative paths reviewed as intrinsically public-safe.
# Study 1 currently has no such exception; extensions and directories are intentionally insufficient.
SAFE_BINARY_PATHS: frozenset[str] = frozenset()


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
        "--diff-filter=ACMR",
        f"{base_commit}...{head_commit}",
    )
    paths: list[PurePosixPath] = []
    for raw_value in (value for value in output.split(b"\0") if value):
        try:
            value = raw_value.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ReleaseValidationError("Git diff returned an undecodable path") from error
        candidate = PurePosixPath(value)
        if candidate.is_absolute() or ".." in candidate.parts or not candidate.parts:
            raise ReleaseValidationError("Git diff returned a path outside the repository")
        paths.append(candidate)
    return paths


def _blob_bytes(repository_root: Path, head_commit: str, path: PurePosixPath) -> bytes:
    return _run_git(repository_root, "cat-file", "blob", f"{head_commit}:{path.as_posix()}")


def _findings_for_bytes(path: Path, content: bytes, relative_path: str) -> list[ReleaseFinding]:
    if b"\0" in content:
        if relative_path in SAFE_BINARY_PATHS:
            return []
        return [ReleaseFinding(path=path, line=1, kind="undecodable_or_binary_blob")]
    try:
        lines = content.decode("utf-8").splitlines()
    except UnicodeDecodeError:
        if relative_path in SAFE_BINARY_PATHS:
            return []
        return [ReleaseFinding(path=path, line=1, kind="undecodable_or_binary_blob")]
    findings: list[ReleaseFinding] = []
    for line_number, line in enumerate(lines, start=1):
        for kind, pattern in PUBLIC_ARTIFACT_PATTERNS:
            if pattern.search(line):
                findings.append(ReleaseFinding(path=path, line=line_number, kind=kind))
    return findings


def scan_release_diff(
    repository_root: str | Path, *, base_ref: str, head_ref: str = "HEAD"
) -> ReleaseScan:
    """Resolve both refs once, then scan changed blobs from the resolved head object."""
    root = Path(repository_root).resolve()
    base_commit = _resolve_commit(root, base_ref)
    head_commit = _resolve_commit(root, head_ref)
    relative_paths = _relative_tracked_paths(root, base_commit, head_commit)
    findings: list[ReleaseFinding] = []
    public_paths: list[Path] = []
    for relative_path in relative_paths:
        public_path = root.joinpath(*relative_path.parts)
        public_paths.append(public_path)
        content = _blob_bytes(root, head_commit, relative_path)
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
        try:
            content = candidate.read_bytes()
        except OSError as error:
            raise ReleaseValidationError("selected release artifact could not be read") from error
        findings.extend(_findings_for_bytes(candidate, content, candidate.as_posix()))
    return findings


def validate_release_diff(
    repository_root: str | Path, *, base_ref: str, head_ref: str = "HEAD"
) -> list[ReleaseFinding]:
    """Scan only resolved proposed Git blobs; never read changed worktree bytes."""
    return list(scan_release_diff(repository_root, base_ref=base_ref, head_ref=head_ref).findings)
