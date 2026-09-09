from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema


class Study2ConfigError(ValueError):
    """Raised when a Study 2 configuration is not safe to use."""


_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schemas" / "study2-frozen-config-v1.schema.json"


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def prompt_sha256(prompt: dict[str, str]) -> str:
    """Hash a prompt without retaining its text in a receipt."""
    return canonical_sha256(prompt)


def load_config(path: Path) -> dict[str, Any]:
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Study2ConfigError(f"cannot load configuration: {path.name}") from exc
    validate_config(config)
    return config


def validate_config(config: dict[str, Any]) -> None:
    if not isinstance(config, dict):
        raise Study2ConfigError("configuration must be an object")
    try:
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.validate(config, schema)
    except (OSError, json.JSONDecodeError) as exc:
        raise Study2ConfigError("Study 2 schema is unavailable") from exc
    except jsonschema.ValidationError as exc:
        raise Study2ConfigError(exc.message) from exc

    if config["intervention"]["type"] != "SYSTEM_COMPARISON":
        raise Study2ConfigError("the intervention must be a SYSTEM_COMPARISON")
    if config["conditions"]["VEGO_AI_OFF"]["detector_v1"] != "NOT_APPLICABLE":
        raise Study2ConfigError("Detector-v1 OFF denominator must be NOT_APPLICABLE")
    if config["conditions"]["VEGO_AI_ON"]["detector_v1"] != "APPLICABLE":
        raise Study2ConfigError("Detector-v1 must be applicable only to ON")
    if config["case_ids"] != ["01", "02", "03", "04"]:
        raise Study2ConfigError("Study 2 requires the frozen four-case order")
    files = config["corpus"]["files"]
    if len({row["path"] for row in files}) != len(files):
        raise Study2ConfigError("corpus file paths must be unique")
    if sum(row["role"] == "domain_description" for row in files) != 1:
        raise Study2ConfigError("corpus requires exactly one domain description")
    if sum(row["role"] == "candidate_model" for row in files) != 4:
        raise Study2ConfigError("corpus requires exactly four candidate models")
    if "llama" in json.dumps(config, ensure_ascii=False).lower():
        raise Study2ConfigError("Llama is a separate optional protocol, not a Study 2 condition")
