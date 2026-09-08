from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_multidataset_admission.py"
PREREGISTRATION = ROOT / "docs/research/phd-proposal/multidataset/multidataset-preregistration-template-v1.json"


def _load_builder():
    spec = importlib.util.spec_from_file_location("build_multidataset_admission", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_admission_builder_generates_safe_consistent_blocked_artifacts(tmp_path: Path) -> None:
    builder = _load_builder()
    result = builder.build(builder.DEFAULT_INPUT, tmp_path)

    assert result["study_status"] == "NO_GO_FOR_PROVIDER_EXECUTION"
    assert result["provider_calls"] == 0
    qure = json.loads((tmp_path / "qure-data-card-v1.json").read_text(encoding="utf-8"))
    archive = json.loads((tmp_path / "vego-se-archive-data-card-v1.json").read_text(encoding="utf-8"))
    assert qure["decision"] == "NOT_ADMITTED"
    assert archive["decision"] == "NOT_ADMITTED"
    qure_card = (tmp_path / "qure-data-card-v1.md").read_text(encoding="utf-8")
    archive_card = (tmp_path / "vego-se-archive-data-card-v1.md").read_text(encoding="utf-8")
    decision_table = (tmp_path / "2026-09-08-multidataset-decision-table.md").read_text(encoding="utf-8")
    assert "LICENCE_UNVERIFIED" in qure_card
    assert "TASK_FIT_UNVERIFIED" in archive_card
    assert "No multi-dataset baseline or ON/OFF result" in decision_table
    tracked_text = "\n".join(path.read_text(encoding="utf-8") for path in tmp_path.iterdir())
    assert "external_data/" not in tracked_text
    assert "C:\\Users" not in tracked_text
    assert "ENGINEERING_FIXTURE_NOT_SCIENTIFIC" not in tracked_text


def test_preregistration_requires_explicit_user_model_freeze_binding() -> None:
    template = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    policy = template["provider_policy"]

    assert policy["model_freeze_status"] == "USER_NOT_FROZEN"
    assert policy["model_approval_sha256"] is None
    assert policy["provider_calls_permitted"] is False
