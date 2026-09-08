"""Local schema validation for safe multi-dataset machine records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema


class SchemaError(ValueError):
    """Raised when a generated multi-dataset record violates its schema."""


_SCHEMA_ROOT = Path(__file__).resolve().parents[2] / "schemas"


def validate_named(payload: Any, schema_name: str) -> None:
    """Validate a local payload against one repository-managed JSON schema."""

    try:
        schema = json.loads((_SCHEMA_ROOT / schema_name).read_text(encoding="utf-8"))
        jsonschema.validate(payload, schema)
    except (OSError, json.JSONDecodeError) as exc:
        raise SchemaError(f"schema unavailable: {schema_name}") from exc
    except jsonschema.ValidationError as exc:
        raise SchemaError(f"schema validation failed: {schema_name}: {exc.message}") from exc
