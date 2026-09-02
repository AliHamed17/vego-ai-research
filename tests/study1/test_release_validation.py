"""Synthetic tests for the Study 1 public-release validator."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


def _validator_module():
    from vego_study1 import release_validation

    return release_validation


def _git(repository: Path, *arguments: str) -> None:
    subprocess.run(["git", "-C", str(repository), *arguments], check=True, capture_output=True)


def _repository_with_branch_diff(tmp_path: Path, content: str) -> Path:
    """Build a small committed branch diff containing one public artifact."""
    repository = tmp_path / "synthetic-release-repository"
    repository.mkdir()
    _git(repository, "init", "-q")
    _git(repository, "config", "user.email", "study1@example.test")
    _git(repository, "config", "user.name", "Study 1 Test")
    (repository / "README.md").write_text("base\n", encoding="utf-8")
    _git(repository, "add", "README.md")
    _git(repository, "commit", "-qm", "base")
    _git(repository, "branch", "baseline")
    (repository / "docs").mkdir()
    (repository / "docs" / "public.md").write_text(content, encoding="utf-8")
    _git(repository, "add", "docs/public.md")
    _git(repository, "commit", "-qm", "public artifact")
    return repository


def test_release_validator_scans_only_committed_branch_diff(tmp_path: Path):
    """Catches a validator that scans unrelated working-tree files instead of the selected diff."""
    module = _validator_module()
    repository = _repository_with_branch_diff(tmp_path, "sanitized public protocol\n")
    (repository / "ignored-danger.md").write_text("RAW" + "_CONTROLLED_CONTENT\n", encoding="utf-8")

    assert module.validate_release_diff(repository, base_ref="baseline") == []
    assert module.proposed_tracked_paths(repository, base_ref="baseline") == [
        repository / "docs" / "public.md"
    ]


def test_release_validator_allows_public_research_context_links(tmp_path: Path):
    """Catches a path matcher that misclassifies an https research citation as a local Windows path."""
    module = _validator_module()
    repository = _repository_with_branch_diff(
        tmp_path, "https://proceedings.example.test/paper/reference.html\n"
    )

    assert module.validate_release_diff(repository, base_ref="baseline") == []


@pytest.mark.parametrize(
    ("unsafe_content", "expected_kind"),
    [
        ("C:" + r"\\private\\stu" + "dent\\record.json", "raw_subject_path"),
        ("/pri" + "vate/" + "eval_" + "output/run.json", "raw_evaluation_output_path"),
        ("model" + "/output.json", "raw_subject_path"),
        ("student" + "/output.json", "raw_subject_path"),
        ("expert" + "/output.json", "raw_subject_path"),
        ("controlled" + "/raw.json", "raw_control_path"),
        ("evaluation" + "/eval_" + "output/run.json", "raw_evaluation_output_path"),
        ("eval_" + "output/run.json", "raw_evaluation_output_path"),
        ("https://" + "drive.google.com/file/d/" + "1" + "AbCdEfGhIjKlMnOpQrStUvWxYz012345", "drive_url"),
        ("1" + "AbCdEfGhIjKlMnOpQrStUvWxYz012345", "drive_id"),
        (r"\\server\\share\\artifact.json", "remote_or_unc_reference"),
        ("api_" + "key=" + "abcDEF1234567890", "credential_like"),
        ('"api_' + 'key": "' + "abcDEF1234567890" + '"', "credential_like"),
        ("OPENAI_" + "API_" + "KEY=" + "abcDEF1234567890", "credential_like"),
        ("RAW" + "_CONTROLLED_CONTENT", "controlled_content_marker"),
    ],
)
def test_release_validator_rejects_prohibited_public_artifacts(
    tmp_path: Path, unsafe_content: str, expected_kind: str
):
    """Catches a release gate that permits a prohibited reference in a proposed tracked artifact."""
    module = _validator_module()
    repository = _repository_with_branch_diff(tmp_path, unsafe_content + "\n")

    findings = module.validate_release_diff(repository, base_ref="baseline")

    relative_findings = [
        (finding.path.as_posix().removeprefix(repository.as_posix() + "/"), finding.kind)
        for finding in findings
    ]
    assert ("docs/public.md", expected_kind) in relative_findings
    assert {path for path, _kind in relative_findings} == {"docs/public.md"}


def test_release_validator_rejects_an_unknown_diff_base(tmp_path: Path):
    """Catches a validator that silently scans an unspecified or incorrect Git comparison range."""
    module = _validator_module()
    repository = _repository_with_branch_diff(tmp_path, "sanitized public protocol\n")

    with pytest.raises(module.ReleaseValidationError, match="Git diff"):
        module.validate_release_diff(repository, base_ref="missing-base")
