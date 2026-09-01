"""Loading and typed access for GovernedJudgmentRecord-v1 instances.

Validates records against ``schemas/governed-judgment-record-v1.schema.json``
using the same Draft 2020-12 registry/format conventions as
``scripts/validate_research_records.py``. Deterministic and offline: no LLM or
API calls, no network. Design artifact only: nothing here asserts an empirical
outcome (EXP-005 0/24).
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import jsonschema
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas" / "governed-judgment-record-v1.schema.json"
SCHEMA_VERSION = "GovernedJudgmentRecord-v1"


class ValidationError(ValueError):
    """A record failed to parse or violated the schema; carries every message."""

    def __init__(self, messages: Sequence[str]) -> None:
        self.messages: list[str] = list(messages)
        super().__init__("; ".join(self.messages) or "invalid record")


@lru_cache(maxsize=1)
def _validator() -> jsonschema.Draft202012Validator:
    registry = Registry().with_resources(
        [
            (schema["$id"], Resource.from_contents(schema))
            for schema in (
                json.loads(path.read_text(encoding="utf-8"))
                for path in sorted((ROOT / "schemas").glob("*.schema.json"))
            )
            if "$id" in schema
        ]
    )
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return jsonschema.Draft202012Validator(
        schema,
        registry=registry,
        format_checker=jsonschema.FormatChecker(),
    )


def schema_errors(record: Mapping[str, Any]) -> list[str]:
    """Return every schema violation as ``<json.path>: <message>``, sorted by path."""

    return [
        (".".join(str(part) for part in issue.absolute_path) or "<root>")
        + f": {issue.message}"
        for issue in sorted(
            _validator().iter_errors(record), key=lambda item: list(item.path)
        )
    ]


@dataclass(frozen=True)
class DissentEntry:
    """One retained dissent entry; append-only per the schema, never averaged."""

    dissent_id: str
    dissenting_record_id: str
    qualified: bool
    conflict_on: str
    blocks_reuse: bool
    adjudication_status: str
    adjudication_outcome: str | None
    raw: Mapping[str, Any]

    @classmethod
    def from_raw(cls, raw: Mapping[str, Any]) -> DissentEntry:
        adjudication = raw.get("adjudication") or {}
        return cls(
            dissent_id=raw["dissentId"],
            dissenting_record_id=raw["dissentingRecordId"],
            qualified=bool(raw["qualified"]),
            conflict_on=raw["conflictOn"],
            blocks_reuse=bool(raw["blocksReuse"]),
            adjudication_status=adjudication.get("status", "not_started"),
            adjudication_outcome=adjudication.get("outcome"),
            raw=raw,
        )


@dataclass(frozen=True)
class Scope:
    """Scope as a decidable conjunction plus its exclusions (the negative half)."""

    ladder_level: str
    decidable: bool
    stated_narrowly: str
    exclusions: tuple[Mapping[str, Any], ...]
    raw: Mapping[str, Any]


@dataclass(frozen=True)
class Competence:
    """Claim-specific assessed competence, recorded separately from authority."""

    assessment_id: str
    assessed_for_claim_id: str
    claim_specific: bool
    assessment_method: str
    level: str
    distinct_from_authority: bool
    raw: Mapping[str, Any]


@dataclass(frozen=True)
class Authority:
    """Claim-scoped mandate to settle the contested fragment; not competence."""

    authority_id: str
    holder_ref: str
    role_ref: str
    claim_scoped: bool
    authority_basis: str
    binding_power: str
    distinct_from_competence: bool
    raw: Mapping[str, Any]


@dataclass(frozen=True)
class Receipts:
    """Retrieval/use/outcome receipts: instrumentation data, never claims."""

    append_only: bool
    retrieval: tuple[Mapping[str, Any], ...]
    use: tuple[Mapping[str, Any], ...]
    outcome: tuple[Mapping[str, Any], ...]
    raw: Mapping[str, Any]


class GovernedJudgmentRecord:
    """Validated read-only view over one GovernedJudgmentRecord-v1 instance.

    Construction validates the payload in full and raises ``ValidationError``
    with the complete message list otherwise. Optional content groups (absent
    under ablation or a degraded conformance profile) surface as ``None`` or an
    empty tuple rather than raising.
    """

    def __init__(self, record: Mapping[str, Any]) -> None:
        if not isinstance(record, Mapping):
            raise ValidationError(
                [f"<root>: record must be a JSON object, got {type(record).__name__}"]
            )
        payload = dict(record)
        errors = schema_errors(payload)
        if errors:
            raise ValidationError(errors)
        self._record: dict[str, Any] = payload

    @classmethod
    def load(cls, source: str | Path | Mapping[str, Any]) -> GovernedJudgmentRecord:
        """Load from a mapping or a JSON file path; parse failures also raise
        ``ValidationError``."""

        if isinstance(source, Mapping):
            return cls(source)
        path = Path(source)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValidationError([f"{path}: {exc}"]) from exc
        if not isinstance(payload, Mapping):
            raise ValidationError(
                [f"{path}: top-level JSON value must be an object"]
            )
        return cls(payload)

    def to_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(self._record))

    @property
    def record_id(self) -> str:
        return self._record["recordId"]

    @property
    def contract_status(self) -> str:
        return self._record["contractStatus"]

    @property
    def conformance_profile(self) -> str:
        return self._record["conformanceProfile"]

    @property
    def claim_boundary(self) -> str:
        return self._record["claimBoundary"]

    @property
    def lifecycle(self) -> Mapping[str, Any] | None:
        return self._record.get("lifecycle")

    @property
    def lifecycle_state(self) -> str | None:
        lifecycle = self._record.get("lifecycle")
        return None if lifecycle is None else lifecycle["state"]

    @property
    def recorded_reuse_gate(self) -> Mapping[str, Any] | None:
        lifecycle = self._record.get("lifecycle")
        return None if lifecycle is None else lifecycle["reuseGate"]

    @property
    def recorded_transitions(self) -> tuple[Mapping[str, Any], ...]:
        lifecycle = self._record.get("lifecycle")
        return () if lifecycle is None else tuple(lifecycle["transitions"])

    @property
    def retained_dissent(self) -> tuple[DissentEntry, ...]:
        return tuple(
            DissentEntry.from_raw(entry)
            for entry in self._record.get("retainedDissent", ())
        )

    @property
    def scope(self) -> Scope | None:
        raw = self._record.get("scope")
        if raw is None:
            return None
        return Scope(
            ladder_level=raw["ladderLevel"],
            decidable=bool(raw["decidable"]),
            stated_narrowly=raw["statedNarrowly"],
            exclusions=tuple(raw["exclusions"]),
            raw=raw,
        )

    @property
    def competence(self) -> Competence | None:
        raw = self._record.get("competence")
        if raw is None:
            return None
        return Competence(
            assessment_id=raw["assessmentId"],
            assessed_for_claim_id=raw["assessedForClaimId"],
            claim_specific=bool(raw["claimSpecific"]),
            assessment_method=raw["assessmentMethod"],
            level=raw["level"],
            distinct_from_authority=bool(raw["distinctFromAuthority"]),
            raw=raw,
        )

    @property
    def authority(self) -> Authority | None:
        raw = self._record.get("authority")
        if raw is None:
            return None
        return Authority(
            authority_id=raw["authorityId"],
            holder_ref=raw["holderRef"],
            role_ref=raw["roleRef"],
            claim_scoped=bool(raw["claimScoped"]),
            authority_basis=raw["authorityBasis"],
            binding_power=raw["bindingPower"],
            distinct_from_competence=bool(raw["distinctFromCompetence"]),
            raw=raw,
        )

    @property
    def receipts(self) -> Receipts | None:
        raw = self._record.get("receipts")
        if raw is None:
            return None
        return Receipts(
            append_only=bool(raw["appendOnly"]),
            retrieval=tuple(raw["retrieval"]),
            use=tuple(raw["use"]),
            outcome=tuple(raw["outcome"]),
            raw=raw,
        )


def load_record(source: str | Path | Mapping[str, Any]) -> GovernedJudgmentRecord:
    """Module-level alias for ``GovernedJudgmentRecord.load``."""

    return GovernedJudgmentRecord.load(source)
