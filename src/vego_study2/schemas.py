from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema


class SchemaValidationError(ValueError):
    """Raised when a persisted Study 2 object violates its contract."""


_SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schemas"


def validate_named(payload: dict[str, Any], schema_name: str) -> None:
    try:
        schema = json.loads((_SCHEMA_DIR / schema_name).read_text(encoding="utf-8"))
        jsonschema.validate(payload, schema)
    except (OSError, json.JSONDecodeError) as exc:
        raise SchemaValidationError(f"schema unavailable: {schema_name}") from exc
    except jsonschema.ValidationError as exc:
        raise SchemaValidationError(exc.message) from exc


def validate_result(payload: dict[str, Any]) -> None:
    validate_named(payload, "study2-result-v1.schema.json")


def validate_receipt(payload: dict[str, Any]) -> None:
    validate_named(payload, "study2-run-receipt-v1.schema.json")
