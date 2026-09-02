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


def _git_text(repository: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _symlink_or_skip(link: Path, target: Path, *, directory: bool = False) -> None:
    try:
        link.symlink_to(target, target_is_directory=directory)
    except OSError as error:
        pytest.skip(f"local symlink creation is unavailable: {error}")


def _repository_with_branch_diff(
    tmp_path: Path, content: str, *, relative_path: str = "docs/public.md"
) -> Path:
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
    artifact = repository.joinpath(*relative_path.split("/"))
    artifact.parent.mkdir(parents=True)
    artifact.write_text(content, encoding="utf-8")
    _git(repository, "add", "--", relative_path)
    _git(repository, "commit", "-qm", "public artifact")
    return repository


def _repository_with_branch_blob(tmp_path: Path, content: bytes) -> Path:
    repository = _repository_with_branch_diff(tmp_path, "placeholder\n")
    (repository / "docs" / "public.md").unlink()
    (repository / "docs" / "public.bin").write_bytes(content)
    _git(repository, "add", "-A")
    _git(repository, "commit", "-qm", "binary artifact")
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


def test_release_validator_reads_committed_blob_not_dirty_masking_bytes(tmp_path: Path):
    """Catches an unsafe committed blob hidden by a sanitized working-tree replacement."""
    module = _validator_module()
    repository = _repository_with_branch_diff(tmp_path, "RAW" + "_CONTROLLED_CONTENT\n")
    (repository / "docs" / "public.md").write_text(
        "sanitized dirty replacement\n", encoding="utf-8"
    )

    findings = module.validate_release_diff(repository, base_ref="baseline")

    assert "controlled_content_marker" in {finding.kind for finding in findings}


def test_release_validator_scans_exact_alternate_head_blob(tmp_path: Path):
    """Catches scanning current HEAD bytes when a different resolved head was requested."""
    module = _validator_module()
    repository = _repository_with_branch_diff(tmp_path, "sanitized selected head\n")
    selected_head = _git_text(repository, "rev-parse", "HEAD")
    (repository / "docs" / "public.md").write_text(
        "RAW" + "_CONTROLLED_CONTENT\n", encoding="utf-8"
    )
    _git(repository, "add", "docs/public.md")
    _git(repository, "commit", "-qm", "later unsafe head")

    assert (
        module.validate_release_diff(repository, base_ref="baseline", head_ref=selected_head) == []
    )


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
        (
            "C:" + chr(92) + "private" + chr(92) + "stu" + "dent" + chr(92) + "record.json",
            "raw_subject_path",
        ),
        ("/" + "private/" + "eval_" + "output/run.json", "raw_evaluation_output_path"),
        ("model" + "/output.json", "raw_subject_path"),
        ("student" + "/output.json", "raw_subject_path"),
        ("expert" + "/output.json", "raw_subject_path"),
        ("controlled" + "/raw.json", "raw_control_path"),
        ("evaluation" + "/eval_" + "output/run.json", "raw_evaluation_output_path"),
        ("eval_" + "output/run.json", "raw_evaluation_output_path"),
        (
            "https://" + "drive.google.com/file/d/" + "1" + "AbCdEfGhIjKlMnOpQrStUvWxYz012345",
            "drive_url",
        ),
        ("1" + "AbCdEfGhIjKlMnOpQrStUvWxYz012345", "drive_id"),
        ("\\" + r"\server\share\artifact.json", "remote_or_unc_reference"),
        ('{"artifact_uri": "file' + '://host/private.bin"}', "remote_or_unc_reference"),
        ("artifact_uri: 's3" + "://private-bucket/item'", "remote_or_unc_reference"),
        ('{"artifact_uri": "gs' + '://private-bucket/item"}', "remote_or_unc_reference"),
        ('{"artifact_path": "/' + '/server/share/item.json"}', "remote_or_unc_reference"),
        ('{"artifact_path": "/' + 'mnt/secure/item.json"}', "absolute_path_reference"),
        ('{"review_host": "review.' + 'internal"}', "private_host_reference"),
        ("artifact_uri: gs" + "://private-bucket/item", "remote_or_unc_reference"),
        ("artifact_path: /" + "mnt/secure/item.json", "absolute_path_reference"),
        ("review_host: review." + "internal", "private_host_reference"),
        ('{"endpoint": "https://' + 'review.' + 'internal/api"}', "private_url"),
        ("endpoint: https://service." + "pri" + "vate/path", "private_url"),
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


def test_release_validator_rejects_reparse_point_in_repository_parent(tmp_path: Path) -> None:
    """Catches Git repository probing through a redirecting path component."""
    module = _validator_module()
    real_parent = tmp_path / "real-parent"
    real_parent.mkdir()
    repository = _repository_with_branch_diff(real_parent, "sanitized public protocol\n")
    linked_parent = tmp_path / "linked-parent"
    _symlink_or_skip(linked_parent, real_parent, directory=True)
    aliased_repository = linked_parent / repository.relative_to(real_parent)

    with pytest.raises(module.ReleaseValidationError, match="symlink|reparse"):
        module.validate_release_diff(aliased_repository, base_ref="baseline")


@pytest.mark.parametrize("content", [b"\xff\xfe\x00private", b"safe-prefix\x00binary"])
def test_release_validator_fails_closed_for_undecodable_or_binary_changed_blobs(
    tmp_path: Path, content: bytes
):
    """Catches changed blobs silently skipped when their bytes cannot be safely scanned."""
    module = _validator_module()
    repository = _repository_with_branch_blob(tmp_path, content)

    findings = module.validate_release_diff(repository, base_ref="baseline")

    assert (repository / "docs" / "public.bin", "undecodable_or_binary_blob") in {
        (finding.path, finding.kind) for finding in findings
    }


def test_release_validator_allows_only_exact_explicit_binary_path_allowlist(
    tmp_path: Path, monkeypatch
):
    """Catches a binary exception mechanism broader than one reviewed repository path."""
    module = _validator_module()
    repository = _repository_with_branch_blob(tmp_path, b"safe-prefix\x00binary")
    monkeypatch.setattr(module, "SAFE_BINARY_PATHS", frozenset({"docs/public.bin"}), raising=False)

    assert module.validate_release_diff(repository, base_ref="baseline") == []


def test_release_validator_rejects_sanitized_blob_at_prohibited_relative_path(
    tmp_path: Path,
) -> None:
    """Catches content-only scanning that permits a private-zone path with sanitized bytes."""
    module = _validator_module()
    repository = _repository_with_branch_diff(
        tmp_path,
        '{"status": "sanitized"}\n',
        relative_path="research-private/study1/sanitized.json",
    )

    findings = module.validate_release_diff(repository, base_ref="baseline")

    assert (
        repository / "research-private" / "study1" / "sanitized.json",
        "private_release_path",
    ) in {(finding.path, finding.kind) for finding in findings}


def test_release_validator_includes_type_changes_and_rejects_non_regular_head_entries(
    tmp_path: Path,
) -> None:
    """Catches type-changed symlink or gitlink entries being omitted from the resolved-head scan."""
    module = _validator_module()
    repository = _repository_with_branch_diff(tmp_path, "sanitized regular content\n")
    _git(repository, "branch", "regular-head")
    target = subprocess.run(
        ["git", "-C", str(repository), "hash-object", "-w", "--stdin"],
        input=b"synthetic-target",
        check=True,
        capture_output=True,
    ).stdout.decode("ascii").strip()
    _git(repository, "update-index", "--cacheinfo", f"120000,{target},docs/public.md")
    _git(repository, "commit", "-qm", "type change")

    scan = module.scan_release_diff(repository, base_ref="regular-head")

    assert scan.paths == (repository / "docs" / "public.md",)
    assert [(finding.path, finding.kind) for finding in scan.findings] == [
        (repository / "docs" / "public.md", "non_regular_tree_entry")
    ]


@pytest.mark.parametrize(
    "raw_path",
    [
        b".." + b"/outside.json\0",
        bytes((47,)) + b"absolute.json\0",
        b"C:" + bytes((92,)) + b"absolute.json\0",
        b"nested" + bytes((92,)) + b"escape.json\0",
    ],
)
def test_release_validator_rejects_non_repository_relative_diff_paths(
    tmp_path: Path, monkeypatch, raw_path: bytes
) -> None:
    """Catches traversal, absolute, drive, or alternate-separator paths from Git output."""
    module = _validator_module()
    repository = _repository_with_branch_diff(tmp_path, "sanitized\n")
    original = module._run_git

    def _malicious_diff(root: Path, *arguments: str) -> bytes:
        if arguments and arguments[0] == "diff":
            return raw_path
        return original(root, *arguments)

    monkeypatch.setattr(module, "_run_git", _malicious_diff)

    with pytest.raises(module.ReleaseValidationError, match="outside the repository"):
        module.validate_release_diff(repository, base_ref="baseline")
