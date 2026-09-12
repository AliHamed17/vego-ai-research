from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from vego_study2.config import load_config

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "docs/research/phd-proposal/study2-frozen-config.json"


def test_frozen_config_validates_against_its_schema() -> None:
    config = load_config(CONFIG)
    schema = json.loads((ROOT / "schemas/study2-frozen-config-v1.schema.json").read_text())
    jsonschema.validate(config, schema)


def test_result_and_receipt_schemas_are_valid_json_documents() -> None:
    for name in ("study2-result-v1.schema.json", "study2-run-receipt-v1.schema.json"):
        schema = json.loads((ROOT / "schemas" / name).read_text())
        jsonschema.Draft202012Validator.check_schema(schema)


def test_documents_keep_not_executed_and_claim_boundaries() -> None:
    docs = [
        ROOT / "docs/research/phd-proposal/2026-09-06-study2-preregistration-draft.md",
        ROOT / "docs/research/phd-proposal/2026-09-06-study2-methodology-he.md",
        ROOT / "docs/research/phd-proposal/2026-09-06-study2-supervisor-onepage-he.md",
        ROOT / "docs/research/phd-proposal/2026-09-06-study2-not-executed-dashboard.md",
        ROOT / "docs/research/phd-proposal/study2-quality-evaluation-template.md",
        ROOT / "docs/research/phd-proposal/study2b-model-portability-protocol.md",
        ROOT / "docs/research/phd-proposal/study2-result-matrix.json",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "NOT_EXECUTED" in text or "NOT_EXECUTED" in text.replace("־", "")
        assert "accuracy" in text.lower() or "דיוק" in text
    assert "Llama" not in CONFIG.read_text(encoding="utf-8")
