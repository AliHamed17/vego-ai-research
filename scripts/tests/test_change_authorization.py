from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_hlayer_change_authorization.py"
WORKFLOW = ROOT / ".github" / "workflows" / "supervisor-package.yml"
VERIFY_SOURCE = ROOT / "scripts" / "verify-source.ps1"


def load_module():
    spec = importlib.util.spec_from_file_location("change_authorization", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_authorized_protected_content_is_hash_bound(
    tmp_path: Path,
    monkeypatch,
) -> None:
    module = load_module()
    monkeypatch.delenv(module.TRUSTED_HASH_ENV, raising=False)
    protected = tmp_path / "VEGO-AI" / "framework" / "llm_client.py"
    protected.parent.mkdir(parents=True)
    seed = tmp_path / "seed.txt"
    seed.write_text("seed\n", encoding="utf-8")
    run_git(tmp_path, "init")
    run_git(tmp_path, "config", "user.email", "fixture@example.invalid")
    run_git(tmp_path, "config", "user.name", "Fixture")
    run_git(tmp_path, "add", "seed.txt")
    run_git(tmp_path, "commit", "-m", "seed")
    protected.write_text("baseline\n", encoding="utf-8")
    run_git(tmp_path, "add", "VEGO-AI/framework/llm_client.py")
    run_git(tmp_path, "commit", "-m", "baseline")

    protected.write_text("authorized hardening\n", encoding="utf-8")
    authorization = tmp_path / "authorization.json"
    config = {
        "allowed_paths": ["VEGO-AI/framework/llm_client.py"],
        "authorized_content_sha256": {
            "VEGO-AI/framework/llm_client.py": module._portable_sha256(protected)
        },
        "forbidden_paths": [],
        "merge_requires_independent_approval": True,
        "authorization_expires_on": "2099-12-31",
    }
    authorization.write_text(json.dumps(config), encoding="utf-8")
    trusted_hash = module._portable_sha256(authorization)
    untrusted_result = module.inspect(tmp_path, authorization, "HEAD^")
    assert untrusted_result["status"] == "FAIL"
    assert untrusted_result["authorization_trusted"] is False
    assert any(
        "not configured outside the candidate tree" in item
        for item in untrusted_result["failures"]
    )
    assert (
        module.inspect(
            tmp_path,
            authorization,
            "HEAD^",
            trusted_authorization_sha256=trusted_hash,
        )["status"]
        == "PASS"
    )

    protected.write_text("later unreviewed change\n", encoding="utf-8")
    result = module.inspect(
        tmp_path,
        authorization,
        "HEAD^",
        trusted_authorization_sha256=trusted_hash,
    )
    assert result["status"] == "FAIL"
    assert any("content differs" in item for item in result["failures"])

    config["authorized_content_sha256"][
        "VEGO-AI/framework/llm_client.py"
    ] = module._portable_sha256(protected)
    authorization.write_text(json.dumps(config), encoding="utf-8")
    result = module.inspect(
        tmp_path,
        authorization,
        "HEAD^",
        trusted_authorization_sha256=trusted_hash,
    )
    assert result["status"] == "FAIL"
    assert result["authorization_trusted"] is False
    assert any(
        "differs from the trusted authorization" in item
        for item in result["failures"]
    )


def test_protected_rename_reports_the_source_path(tmp_path: Path) -> None:
    module = load_module()
    protected = tmp_path / "VEGO-AI" / "framework" / "agent4_variability_explorer.py"
    protected.parent.mkdir(parents=True)
    protected.write_text("protected baseline\n", encoding="utf-8")
    run_git(tmp_path, "init")
    run_git(tmp_path, "config", "user.email", "fixture@example.invalid")
    run_git(tmp_path, "config", "user.name", "Fixture")
    run_git(tmp_path, "add", "VEGO-AI/framework/agent4_variability_explorer.py")
    run_git(tmp_path, "commit", "-m", "baseline")

    destination = tmp_path / "relocated_agent4.py"
    run_git(
        tmp_path,
        "mv",
        "VEGO-AI/framework/agent4_variability_explorer.py",
        destination.name,
    )
    run_git(tmp_path, "commit", "-m", "attempt protected relocation")
    authorization = tmp_path / "authorization.json"
    authorization.write_text(
        json.dumps(
            {
                "allowed_paths": [],
                "authorized_content_sha256": {},
                "forbidden_paths": [
                    "VEGO-AI/framework/agent4_variability_explorer.py"
                ],
                "merge_requires_independent_approval": True,
                "authorization_expires_on": "2099-12-31",
            }
        ),
        encoding="utf-8",
    )

    result = module.inspect(
        tmp_path,
        authorization,
        "HEAD^",
        trusted_authorization_sha256=module._portable_sha256(authorization),
    )
    assert result["status"] == "FAIL"
    assert "VEGO-AI/framework/agent4_variability_explorer.py" in result[
        "forbidden_changes"
    ]


def test_canonical_runtime_paths_are_protected(tmp_path: Path) -> None:
    module = load_module()
    runtime = tmp_path / "src" / "vego_hlayer" / "runtime.py"
    runtime.parent.mkdir(parents=True)
    seed = tmp_path / "seed.txt"
    seed.write_text("seed\n", encoding="utf-8")
    run_git(tmp_path, "init", "-b", "main")
    run_git(tmp_path, "config", "user.email", "fixture@example.invalid")
    run_git(tmp_path, "config", "user.name", "Fixture")
    run_git(tmp_path, "add", "seed.txt")
    run_git(tmp_path, "commit", "-m", "seed")
    runtime.write_text("baseline\n", encoding="utf-8")
    run_git(tmp_path, "add", "src/vego_hlayer/runtime.py")
    run_git(tmp_path, "commit", "-m", "baseline")
    runtime.write_text("unreviewed\n", encoding="utf-8")
    authorization = tmp_path / "authorization.json"
    authorization.write_text(
        json.dumps(
            {
                "allowed_paths": [],
                "authorized_content_sha256": {},
                "forbidden_paths": [],
                "merge_requires_independent_approval": True,
                "authorization_expires_on": "2099-12-31",
            }
        ),
        encoding="utf-8",
    )
    result = module.inspect(
        tmp_path,
        authorization,
        "HEAD^",
        trusted_authorization_sha256=module._portable_sha256(authorization),
    )
    assert result["status"] == "FAIL"
    assert result["unauthorized_changes"] == ["src/vego_hlayer/runtime.py"]


def test_git_symlink_mode_cannot_reuse_an_authorized_hash(tmp_path: Path) -> None:
    module = load_module()
    protected = tmp_path / "src" / "vego_hlayer" / "runtime.py"
    protected.parent.mkdir(parents=True)
    seed = tmp_path / "seed.txt"
    seed.write_text("seed\n", encoding="utf-8")
    run_git(tmp_path, "init", "-b", "main")
    run_git(tmp_path, "config", "user.email", "fixture@example.invalid")
    run_git(tmp_path, "config", "user.name", "Fixture")
    run_git(tmp_path, "add", "seed.txt")
    run_git(tmp_path, "commit", "-m", "seed")
    protected.write_text("baseline\n", encoding="utf-8")
    run_git(tmp_path, "add", "src/vego_hlayer/runtime.py")
    run_git(tmp_path, "commit", "-m", "baseline")

    protected.write_text("authorized\n", encoding="utf-8")
    blob = subprocess.run(
        ["git", "hash-object", "-w", "--stdin"],
        cwd=tmp_path,
        input="authorized\n",
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip()
    run_git(
        tmp_path,
        "update-index",
        "--add",
        "--cacheinfo",
        f"120000,{blob},src/vego_hlayer/runtime.py",
    )
    authorization = tmp_path / "authorization.json"
    authorization.write_text(
        json.dumps(
            {
                "allowed_paths": ["src/vego_hlayer/runtime.py"],
                "authorized_content_sha256": {
                    "src/vego_hlayer/runtime.py": module._portable_sha256(protected)
                },
                "forbidden_paths": [],
                "merge_requires_independent_approval": True,
                "authorization_expires_on": "2099-12-31",
            }
        ),
        encoding="utf-8",
    )
    result = module.inspect(
        tmp_path,
        authorization,
        "HEAD^",
        trusted_authorization_sha256=module._portable_sha256(authorization),
    )
    assert result["status"] == "FAIL"
    assert any(
        "cannot be a symbolic link or reparse point" in item
        for item in result["failures"]
    )


def test_default_base_falls_back_to_local_main_without_remote(
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = load_module()
    monkeypatch.delenv("PR_BASE_SHA", raising=False)
    monkeypatch.delenv("H_LAYER_CHANGE_BASE", raising=False)
    monkeypatch.delenv("GITHUB_BASE_REF", raising=False)
    run_git(tmp_path, "init", "-b", "main")
    run_git(tmp_path, "config", "user.email", "fixture@example.invalid")
    run_git(tmp_path, "config", "user.name", "Fixture")
    marker = tmp_path / "marker.txt"
    marker.write_text("baseline\n", encoding="utf-8")
    run_git(tmp_path, "add", "marker.txt")
    run_git(tmp_path, "commit", "-m", "baseline")
    run_git(tmp_path, "checkout", "-b", "feature")
    marker.write_text("feature\n", encoding="utf-8")
    run_git(tmp_path, "commit", "-am", "feature")

    assert module.resolve_comparison_base(tmp_path) == "main"
    assert module.resolve_comparison_base(tmp_path, "origin/main") == "main"
    run_git(tmp_path, "checkout", "main")
    try:
        module.resolve_comparison_base(tmp_path)
    except ValueError as exc:
        assert "no trusted ancestor" in str(exc)
    else:
        raise AssertionError("a single-commit checkout must fail closed")
    try:
        module.resolve_comparison_base(tmp_path, "main")
    except ValueError as exc:
        assert "distinct from HEAD" in str(exc)
    else:
        raise AssertionError("a comparison base resolving to HEAD must fail closed")


def test_git_path_reader_preserves_newlines(monkeypatch, tmp_path: Path) -> None:
    module = load_module()
    raw_path = b"VEGO-AI/framework/review\nhook.py\0"

    def fake_run(*_args, **_kwargs):
        return SimpleNamespace(stdout=raw_path)

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    assert module._git_paths(tmp_path, "diff", "--name-only", "-z") == {
        "VEGO-AI/framework/review\nhook.py"
    }


def test_push_workflow_uses_the_pre_push_revision() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert (
        "H_LAYER_AUTHORIZATION_SHA256: "
        "${{ vars.H_LAYER_AUTHORIZATION_SHA256 }}" in workflow
    )
    assert "PUSH_BEFORE_SHA: ${{ github.event.before }}" in workflow
    assert 'BASE="${PR_BASE_SHA:-${PUSH_BEFORE_SHA:-origin/main}}"' in workflow
    assert 'BASE="${PR_BASE_SHA:-${PUSH_BEFORE_SHA:-HEAD^}}"' in workflow


def test_python_matrix_runs_proposal_visual_tests() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert (
        "uv run python -m pytest tests/proposal_visuals -q -p no:cacheprovider"
        in workflow
    )


def test_verify_source_bootstraps_authorization_from_external_trust() -> None:
    script = VERIFY_SOURCE.read_text(encoding="utf-8")
    assert "[string]$TrustedAuthorizationSha256" in script
    assert "gh variable get H_LAYER_AUTHORIZATION_SHA256 --repo $repository" in script
    assert "$env:H_LAYER_AUTHORIZATION_SHA256 = $trusted.ToLowerInvariant()" in script


def test_verify_source_bootstraps_locked_dependencies_before_doctor() -> None:
    script = VERIFY_SOURCE.read_text(encoding="utf-8")
    doctor = script.index("uv run python scripts/vego_doctor.py")
    assert script.index("uv sync --frozen --all-groups") < doctor
    assert script.index("npm ci --ignore-scripts --no-audit") < doctor
    assert "npx --no-install playwright install chromium" in script
    assert "refs/tags/${tag}:refs/tags/${tag}" in script
    assert "2eeccb1cbb2d01faa3e8ceb43466a52e0fee23cf" in script
