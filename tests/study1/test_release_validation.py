"""Synthetic tests for the Study 1 public-release validator."""

from __future__ import annotations

import subprocess
from pathlib import Path
from urllib.parse import quote

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
    _git(repository, "config", "user.email", "study1@" + "example.test")
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


def _structured_credential_text(suffix: str) -> str:
    """Build credential-shaped text at runtime without tracking a complete sample."""
    field_name = "api_" + "key"
    field_value = "abc" + "DEF12345" + "67890"
    if suffix == ".json":
        encoded_name = field_name.replace("k", "\\u006b", 1)
        return (
            '{"'
            + encoded_name
            + '":"'
            + field_value[:8]
            + "\\n"
            + field_value[8:]
            + '"}\n'
        )
    return field_name + ": >-\n  " + field_value[:8] + "\n  " + field_value[8:] + "\n"


def _credential_fallback_text(suffix: str) -> str:
    """Build an unsafe shell fallback only at runtime so no credential sample is tracked."""
    field_name = "api_" + "key"
    fallback = (
        "${"
        + "STUDY1_TOKEN"
        + ":-"
        + "abc"
        + "DEF12345"
        + "67890"
        + "}"
    )
    if suffix == ".json":
        import json

        return json.dumps({field_name: fallback}) + "\n"
    return field_name + ": " + repr(fallback) + "\n"


def _plain_text_credential_assignment(scalar: str) -> str:
    """Build a text assignment only at runtime so tracked test code stays scanner-safe."""
    field_name = "service_" + "token"
    return field_name + "=" + scalar + "\n"


def _plain_text_credential_scalars() -> tuple[str, ...]:
    return ("x", chr(0x79D8) + chr(0x5BC6), "false")


def _bare_credential_placeholder_assignment() -> str:
    placeholder = "${" + "STUDY1_TOKEN" + "}"
    return _plain_text_credential_assignment(placeholder)


def _credential_placeholder_with_literal_assignment(prefix: str, suffix: str) -> str:
    """Build a non-standalone placeholder without tracking a credential-shaped sample."""
    placeholder = "${" + "STUDY1_TOKEN" + "}"
    return _plain_text_credential_assignment(prefix + placeholder + suffix)


def _release_locator_cases() -> tuple[tuple[str, str], ...]:
    drive_locator = (
        "https://"
        + "drive."
        + "google.com/file/d/"
        + "1"
        + "A" * 28
    )
    return (
        (quote(drive_locator, safe=""), "drive_url"),
        ("/" + "安全" + "/" + "記録", "absolute_path_reference"),
        (
            chr(92) * 2 + "伺服器" + chr(92) + "共享" + chr(92) + "記録",
            "remote_or_unc_reference",
        ),
    )


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
        ("model" + "/" + "output.json", "raw_subject_path"),
        ("student" + "/" + "output.json", "raw_subject_path"),
        ("expert" + "/" + "output.json", "raw_subject_path"),
        ("controlled" + "/" + "raw.json", "raw_control_path"),
        ("evaluation" + "/" + "eval_" + "output/run.json", "raw_evaluation_output_path"),
        ("eval_" + "output" + "/" + "run.json", "raw_evaluation_output_path"),
        (
            "https://" + "drive.google.com/file/d/" + "1" + "AbCdEfGhIjKlMnOpQrStUvWxYz012345",
            "drive_url",
        ),
        ("1" + "AbCdEfGhIjKlMnOpQrStUvWxYz012345", "drive_id"),
        ("\\" + r"\server\share\artifact.json", "remote_or_unc_reference"),
        ('{"artifact_uri": "file' + '://host/private.bin"}', "remote_or_unc_reference"),
        ("artifact_uri: 's3" + "://private-bucket/item'", "remote_or_unc_reference"),
        ('{"artifact_uri": "gs' + '://private-bucket/item"}', "remote_or_unc_reference"),
        (
            '{"artifact_path": "/' + "/" + 'server/share/item.json"}',
            "remote_or_unc_reference",
        ),
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
        ("Fetch g" + chr(115) + ":private-bucket/item", "remote_or_unc_reference"),
        (
            "Open " + chr(0xFF0F) * 2 + "server" + chr(0xFF0F) + "share/item",
            "remote_or_unc_reference",
        ),
        (
            "Download https://"
            + "drive."
            + "usercontent.google.com/download?id="
            + "0B"
            + "A" * 28,
            "drive_url",
        ),
        ("Legacy locator " + "0B" + "A" * 28, "drive_id"),
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


@pytest.mark.parametrize(
    ("content", "relative_path", "expected_kind"),
    [
        (
            '{"uri":"g\\u0073:\\/\\/private-bucket\\/committed-item"}\n',
            "docs/public.json",
            "remote_or_unc_reference",
        ),
        (
            "payload: >-\n  " + "data" + ":text/plain;base64,\n  U0VDUkVU\n",
            "docs/public.yaml",
            "remote_or_unc_reference",
        ),
    ],
)
def test_release_validator_scans_decoded_committed_structured_scalars(
    tmp_path: Path,
    content: str,
    relative_path: str,
    expected_kind: str,
) -> None:
    """Catches encoded or folded private locators inside the resolved head object."""
    module = _validator_module()
    repository = _repository_with_branch_diff(
        tmp_path,
        content,
        relative_path=relative_path,
    )

    findings = module.validate_release_diff(repository, base_ref="baseline")

    assert expected_kind in {finding.kind for finding in findings}


@pytest.mark.parametrize("suffix", [".json", ".yaml"])
def test_release_validator_detects_structured_credential_association(
    tmp_path: Path, suffix: str
) -> None:
    """Catches the committed-tree scan losing decoded credential key/value association."""
    module = _validator_module()
    repository = _repository_with_branch_diff(
        tmp_path,
        _structured_credential_text(suffix),
        relative_path="docs/public" + suffix,
    )

    findings = module.validate_release_diff(repository, base_ref="baseline")

    assert "credential_like" in {finding.kind for finding in findings}


def test_release_validator_preserves_reused_yaml_alias_credential_context(
    tmp_path: Path,
) -> None:
    """Catches committed-tree scanning that loses the second context of a YAML alias."""
    content = (
        'public_label: &shared "synthetic unicode 私密"\n'
        + ("service-" + "token-copy")
        + ": *shared\n"
    )
    repository = _repository_with_branch_diff(
        tmp_path,
        content,
        relative_path="docs/public.yaml",
    )

    findings = _validator_module().validate_release_diff(repository, base_ref="baseline")

    assert "credential_like" in {finding.kind for finding in findings}


@pytest.mark.parametrize("suffix", [".json", ".yaml"])
def test_release_validator_rejects_credential_shell_fallbacks_from_committed_trees(
    tmp_path: Path, suffix: str
) -> None:
    """Catches a committed JSON or YAML literal fallback allowlisted as a bare placeholder."""
    repository = _repository_with_branch_diff(
        tmp_path,
        _credential_fallback_text(suffix),
        relative_path="docs/public" + suffix,
    )

    findings = _validator_module().validate_release_diff(repository, base_ref="baseline")

    assert "credential_like" in {finding.kind for finding in findings}


@pytest.mark.parametrize("scalar", _plain_text_credential_scalars())
def test_release_validator_rejects_any_non_placeholder_plain_text_credential_scalar(
    tmp_path: Path, scalar: str
) -> None:
    """Catches committed-tree scanning that permits short, Unicode, or boolean-like values."""
    repository = _repository_with_branch_diff(
        tmp_path,
        _plain_text_credential_assignment(scalar),
        relative_path="docs/public.env",
    )

    findings = _validator_module().validate_release_diff(repository, base_ref="baseline")

    assert "credential_like" in {finding.kind for finding in findings}


def test_release_validator_keeps_a_bare_plain_text_credential_placeholder_public_safe(
    tmp_path: Path,
) -> None:
    """Catches committed-tree assignment hardening that rejects a bare placeholder."""
    repository = _repository_with_branch_diff(
        tmp_path,
        _bare_credential_placeholder_assignment(),
        relative_path="docs/public.env",
    )

    findings = _validator_module().validate_release_diff(repository, base_ref="baseline")

    assert "credential_like" not in {finding.kind for finding in findings}


@pytest.mark.parametrize(
    ("prefix", "suffix"),
    [
        ("literal-", ""),
        ("", "-literal"),
        ("literal-", "-literal"),
        ("literal ", ""),
        ("", " literal"),
        ("", "${OTHER}"),
        ("(", ")"),
        ("", ",literal"),
        ("", "#literal"),
        ('"', '"literal'),
    ],
)
def test_release_validator_rejects_credential_placeholders_with_literal_neighbors(
    tmp_path: Path, prefix: str, suffix: str
) -> None:
    """Catches committed-tree scans that allowlist only a placeholder substring."""
    repository = _repository_with_branch_diff(
        tmp_path,
        _credential_placeholder_with_literal_assignment(prefix, suffix),
        relative_path="docs/public.env",
    )

    findings = _validator_module().validate_release_diff(repository, base_ref="baseline")

    assert "credential_like" in {finding.kind for finding in findings}


@pytest.mark.parametrize(("locator", "expected_kind"), _release_locator_cases())
def test_release_validator_decodes_and_classifies_encoded_or_unicode_tree_locators(
    tmp_path: Path, locator: str, expected_kind: str
) -> None:
    """Catches committed-tree scans that miss encoded Drive and Unicode path or UNC tokens."""
    repository = _repository_with_branch_diff(
        tmp_path,
        "Locator " + locator + "\n",
    )

    findings = _validator_module().validate_release_diff(repository, base_ref="baseline")

    assert expected_kind in {finding.kind for finding in findings}


@pytest.mark.parametrize(
    ("relative_path", "expected_kind"),
    [
        ("docs/archive/review." + "internal/public.md", "private_host_reference"),
        ("docs/archive/ali" + "ce@" + "example.test/public.md", "email_identifier"),
        (
            "docs/archive/api_" + "key=abc" + "DEF1234567890/public.md",
            "credential_like",
        ),
    ],
)
def test_release_validator_applies_privacy_rules_to_the_whole_tree_pathname(
    tmp_path: Path, relative_path: str, expected_kind: str
) -> None:
    """Catches sanitized committed blobs whose Git path alone carries private metadata."""
    module = _validator_module()
    repository = _repository_with_branch_diff(
        tmp_path,
        "sanitized public content\n",
        relative_path=relative_path,
    )

    findings = module.validate_release_diff(repository, base_ref="baseline")

    assert expected_kind in {finding.kind for finding in findings}


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
        b".." + bytes((47,)) + b"outside.json\0",
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
