from __future__ import annotations

from dataclasses import dataclass

VALID_CLASSIFICATIONS = {"public", "internal", "restricted", "secret"}
VALID_TARGETS = {"local", "github", "codecium"}


@dataclass(frozen=True)
class KnowledgeRecord:
    record_id: str
    project: str
    classification: str
    source_kind: str
    source_ref: str
    sha256: str
    summary: str
    review_state: str
    publish_target: str = "local"


def validate_record(record: KnowledgeRecord) -> list[str]:
    errors: list[str] = []
    if record.classification not in VALID_CLASSIFICATIONS:
        errors.append("invalid classification")
    if record.publish_target not in VALID_TARGETS:
        errors.append("invalid publish target")
    if len(record.sha256) != 64 or any(char not in "0123456789abcdef" for char in record.sha256.lower()):
        errors.append("sha256 must be 64 hexadecimal characters")
    if record.classification in {"restricted", "secret"} and record.publish_target != "local":
        errors.append(f"{record.classification} records cannot publish to {record.publish_target}")
    return errors
