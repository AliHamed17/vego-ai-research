"""Validate only the proposed tracked Git diff for Study 1 public-release safety."""

from __future__ import annotations

import re
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path


class ReleaseValidationError(ValueError):
    """Raised when the selected Git diff cannot be safely validated."""


@dataclass(frozen=True)
class ReleaseFinding:
    """A prohibited public reference found in a proposed tracked artifact."""

    path: Path
    line: int
    kind: str


_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "raw_subject_path",
        re.compile(r"(?i)(?:[a-z]:[\\/]|/)(?:[^\s\"']*[\\/])?(?:student|expert|model)[\\/][^\s\"']+"),
    ),
    (
        "raw_evaluation_output_path",
        re.compile(
            r"(?i)(?<![a-z0-9_-])(?:[a-z]:[\\/]|/)[^\s\"']*"
            r"[\\/]eval_output(?:[\\/][^\s\"']*)?"
        ),
    ),
    (
        "private_absolute_path",
        re.compile(r"(?i)(?:(?<![a-z0-9])[a-z]:[\\/]|/(?:home|users|private)/)"),
    ),
    ("drive_url", re.compile(r"(?i)https?://(?:drive|docs)\.google\.com/")),
    ("drive_id", re.compile(r"\b1[A-Za-z0-9_-]{24,}\b")),
    (
        "remote_or_unc_reference",
        re.compile(r"(?i)(?:^|\s)(?:\\\\|(?:file|s3|ssh|ftp|git):)"),
    ),
    (
        "credential_like",
        re.compile(
            r"(?i)\b(?:api[_-]?key|token|secret|password|credential)\b\s*[:=]\s*"
            r"(?!\$\{|\{\{)[A-Za-z0-9_./+=-]{8,}"
        ),
    ),
    (
        "controlled_content_marker",
        re.compile(r"(?i)RAW[_]CONTROLLED[_]CONTENT|CONTROLLED[_](?:STUDENT|EXPERT)|(?:STUDENT|EXPERT)[_]RAW[_]"),
    ),
)


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


def _relative_tracked_paths(repository_root: Path, base_ref: str, head_ref: str) -> list[Path]:
    output = _run_git(
        repository_root,
        "diff",
        "--name-only",
        "-z",
        "--diff-filter=ACMR",
        f"{base_ref}...{head_ref}",
    )
    return [Path(value.decode("utf-8")) for value in output.split(b"\0") if value]


def proposed_tracked_paths(
    repository_root: str | Path, *, base_ref: str, head_ref: str = "HEAD"
) -> list[Path]:
    """Return existing tracked files changed in exactly the selected branch comparison."""
    root = Path(repository_root).resolve()
    paths: list[Path] = []
    for relative_path in _relative_tracked_paths(root, base_ref, head_ref):
        candidate = (root / relative_path).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as error:
            raise ReleaseValidationError("Git diff returned a path outside the repository") from error
        if candidate.is_file():
            paths.append(candidate)
    return paths


def validate_release_paths(paths: Iterable[Path]) -> list[ReleaseFinding]:
    """Find prohibited references in proposed public text/code artifacts."""
    findings: list[ReleaseFinding] = []
    for path in paths:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(lines, start=1):
            for kind, pattern in _PATTERNS:
                if pattern.search(line):
                    findings.append(ReleaseFinding(path=path, line=line_number, kind=kind))
    return findings


def validate_release_diff(
    repository_root: str | Path, *, base_ref: str, head_ref: str = "HEAD"
) -> list[ReleaseFinding]:
    """Scan only proposed tracked branch-diff artifacts; never traverse ignored private data."""
    return validate_release_paths(
        proposed_tracked_paths(repository_root, base_ref=base_ref, head_ref=head_ref)
    )
