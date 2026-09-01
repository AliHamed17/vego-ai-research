"""GJR-LIFECYCLE 1.0.0: the GovernedJudgmentRecord-v1 lifecycle, executable.

Implements exactly what ``schemas/governed-judgment-record-v1.schema.json``
declares: the seven-state enum, the T01-T20 legal transition table (the
schema's ``transitionRecord`` oneOf, held verbatim in ``TRANSITION_TABLE``
with ``TXX`` reserved for rejected attempts at pairs outside it), the
CHK-12/13/14 record-side reuse gate, and the CHK-15/16/17 guard requirements
on revocation, supersession, and expiry. Both accepted transitions and
rejected attempts are recorded in the schema's ``transitionRecord`` shape, so
predictable rejection is inspectable.

Rejection codes: the schema constrains codes to ``^GJR-E-[0-9]{3}$`` and the
worked example (``schemas/examples/governed-judgment-record.valid.json``,
attempts TR-0003/TR-0004) fixes two of them: GJR-E-002 for a from/to pair that
is not in the transition table, and GJR-E-014 for a return to active while a
qualified dissent awaits adjudication (guard G-ADJ-AUTHORITY). The remaining
codes used here are assigned in ``REJECTION_CODES`` within the same pattern.

Reuse gate: CHK-12 closes the record-side gate for every non-active state via
``BLOCKING_REASON_BY_STATE`` (the schema's blockingReasons enum members);
CHK-13 leaves it open only for active, with read-side gates owned by SQ3;
CHK-14 defines the unadjudicated statuses in ``UNADJUDICATED_STATUSES`` and
the worked example records ``retained_dissent_pending_adjudication`` as the
dissent-closed reason.

Deterministic and offline; timestamps are caller-supplied, never generated.
Design artifact only: no empirical outcome is asserted (EXP-005 0/24).
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from types import MappingProxyType
from typing import Any

STATE_MACHINE_ID = "GJR-LIFECYCLE"
STATE_MACHINE_VERSION = "1.0.0"

STATES: tuple[str, ...] = (
    "draft",
    "active",
    "contested",
    "retained_dissent",
    "superseded",
    "expired",
    "revoked",
)

TRANSITION_TABLE: Mapping[str, tuple[str, str]] = MappingProxyType(
    {
        "T01": ("draft", "active"),
        "T02": ("draft", "revoked"),
        "T03": ("active", "contested"),
        "T04": ("active", "retained_dissent"),
        "T05": ("active", "superseded"),
        "T06": ("active", "expired"),
        "T07": ("active", "revoked"),
        "T08": ("contested", "active"),
        "T09": ("contested", "retained_dissent"),
        "T10": ("contested", "superseded"),
        "T11": ("contested", "expired"),
        "T12": ("contested", "revoked"),
        "T13": ("retained_dissent", "active"),
        "T14": ("retained_dissent", "superseded"),
        "T15": ("retained_dissent", "revoked"),
        "T16": ("retained_dissent", "expired"),
        "T17": ("expired", "active"),
        "T18": ("expired", "superseded"),
        "T19": ("expired", "revoked"),
        "T20": ("superseded", "revoked"),
    }
)

LEGAL_TRANSITIONS: Mapping[tuple[str, str], str] = MappingProxyType(
    {pair: transition_id for transition_id, pair in TRANSITION_TABLE.items()}
)

ILLEGAL_TRANSITION_ID = "TXX"

REJECT_NOT_IN_TABLE = "GJR-E-002"
REJECT_ADJUDICATION_PENDING = "GJR-E-014"
REJECT_SUCCESSOR_MISSING = "GJR-E-015"
REJECT_EXPIRY_CONDITION_MISSING = "GJR-E-016"
REJECT_REVOCATION_REASON_MISSING = "GJR-E-017"
REJECT_REVOCATION_AUTHORITY_MISSING = "GJR-E-018"

REJECTION_CODES: Mapping[str, str] = MappingProxyType(
    {
        REJECT_NOT_IN_TABLE: (
            "from/to pair is not in the legal transition table (transitionId TXX)"
        ),
        REJECT_ADJUDICATION_PENDING: (
            "return to active requires every qualified dissent to be adjudicated"
            " (guard G-ADJ-AUTHORITY)"
        ),
        REJECT_SUCCESSOR_MISSING: (
            "supersession requires a named successor record (CHK-16, guard G-SUCCESSOR)"
        ),
        REJECT_EXPIRY_CONDITION_MISSING: (
            "expiry requires the fired condition id (CHK-17, guard G-EXPIRY-CONDITION)"
        ),
        REJECT_REVOCATION_REASON_MISSING: (
            "revocation requires a recorded reason (CHK-15, guard G-REVOKE-REASON)"
        ),
        REJECT_REVOCATION_AUTHORITY_MISSING: (
            "revocation requires a revoking authority (CHK-15, guard G-REVOKE-AUTHORITY)"
        ),
    }
)

BLOCKING_REASON_BY_STATE: Mapping[str, str] = MappingProxyType(
    {
        "draft": "not_yet_published",
        "contested": "challenge_open",
        "retained_dissent": "retained_dissent_pending_adjudication",
        "superseded": "superseded",
        "expired": "expired",
        "revoked": "revoked",
    }
)

REASON_RETAINED_DISSENT = "retained_dissent_pending_adjudication"

UNADJUDICATED_STATUSES = frozenset(
    {"not_started", "pending", "in_progress", "deadlocked"}
)

_SUCCESSOR_RECORD_ID_RE = re.compile(r"^GJR-[A-Za-z0-9_-]+$")


class TransitionRejected(ValueError):
    """An attempted transition was rejected; carries the schema-named code."""

    def __init__(
        self,
        code: str,
        from_state: str,
        to_state: str,
        *,
        guard_id: str | None = None,
        detail: str | None = None,
    ) -> None:
        self.code = code
        self.from_state = from_state
        self.to_state = to_state
        self.guard_id = guard_id
        self.detail = detail or REJECTION_CODES.get(code, code)
        super().__init__(
            f"{code}: {from_state} -> {to_state} rejected: {self.detail}"
        )


def export_transition_table() -> tuple[dict[str, str], ...]:
    """Enumerate the legal transition table as rows for docs and tests."""

    return tuple(
        {"transitionId": transition_id, "from": from_state, "to": to_state}
        for transition_id, (from_state, to_state) in TRANSITION_TABLE.items()
    )


def _dissent_fields(entry: Any) -> tuple[bool, str]:
    """Read (qualified, adjudication status) from a schema-shaped mapping or a
    ``records.DissentEntry``-style object."""

    if isinstance(entry, Mapping):
        qualified = bool(entry.get("qualified", False))
        adjudication = entry.get("adjudication") or {}
        status = adjudication.get("status", "not_started")
    else:
        qualified = bool(getattr(entry, "qualified", False))
        status = getattr(entry, "adjudication_status", "not_started")
    return qualified, status


def has_unadjudicated_qualified_dissent(retained_dissent: Iterable[Any]) -> bool:
    """True when any qualified dissent still awaits adjudication (CHK-14)."""

    for entry in retained_dissent:
        qualified, status = _dissent_fields(entry)
        if qualified and status in UNADJUDICATED_STATUSES:
            return True
    return False


def reuse_gate(
    state: str, retained_dissent: Iterable[Any] = ()
) -> dict[str, Any]:
    """Compute the record-side reuse gate from state plus retained dissent.

    Shaped like the schema's ``lifecycle.reuseGate``. Blocked for every
    non-active state (CHK-12) and for any unadjudicated qualified dissent,
    using the reason string the worked example records; read-side gates stay
    owned by SQ3 and are not decided here (CHK-13).
    """

    if state not in STATES:
        raise ValueError(f"unknown lifecycle state: {state!r}")
    blocking_reasons: list[str] = []
    state_reason = BLOCKING_REASON_BY_STATE.get(state)
    if state_reason is not None:
        blocking_reasons.append(state_reason)
    if (
        has_unadjudicated_qualified_dissent(retained_dissent)
        and REASON_RETAINED_DISSENT not in blocking_reasons
    ):
        blocking_reasons.append(REASON_RETAINED_DISSENT)
    return {
        "decision": "blocked" if blocking_reasons else "permitted",
        "derivedFrom": "lifecycle.state",
        "blockingReasons": blocking_reasons,
        "readSideGatesOwnedBy": "SQ3",
    }


class LifecycleEngine:
    """Explicit state machine over the schema's own state enum and table.

    Every attempt — accepted or rejected — is appended to ``transitions`` in
    the schema's ``transitionRecord`` shape. Rejections raise
    ``TransitionRejected`` with the named code after being recorded, and never
    change the current state.
    """

    def __init__(
        self,
        state: str = "draft",
        retained_dissent: Iterable[Any] = (),
    ) -> None:
        if state not in STATES:
            raise ValueError(f"unknown lifecycle state: {state!r}")
        self.state = state
        self.retained_dissent: tuple[Any, ...] = tuple(retained_dissent)
        self.transitions: list[dict[str, Any]] = []

    @classmethod
    def from_record(cls, record: Any) -> LifecycleEngine:
        """Build from a ``records.GovernedJudgmentRecord`` carrying a lifecycle."""

        state = record.lifecycle_state
        if state is None:
            raise ValueError("record carries no lifecycle content group")
        return cls(state=state, retained_dissent=record.retained_dissent)

    def reuse_gate(self) -> dict[str, Any]:
        return reuse_gate(self.state, self.retained_dissent)

    def attempt(
        self,
        to_state: str,
        *,
        actor_ref: str,
        attempted_at: str,
        actor_authority_ref: str | None = None,
        revocation_reason: str | None = None,
        revoked_by_authority_ref: str | None = None,
        superseded_by_record_id: str | None = None,
        fired_condition_id: str | None = None,
    ) -> dict[str, Any]:
        """Attempt ``state -> to_state``; return the recorded transition.

        Guard requirements, matching the schema's CHK comments:
        retained_dissent -> active needs every qualified dissent adjudicated
        (G-ADJ-AUTHORITY, GJR-E-014); -> superseded needs
        ``superseded_by_record_id`` (G-SUCCESSOR); -> expired needs
        ``fired_condition_id`` (G-EXPIRY-CONDITION); -> revoked needs
        ``revocation_reason`` and ``revoked_by_authority_ref``
        (G-REVOKE-REASON, G-REVOKE-AUTHORITY).
        """

        if to_state not in STATES:
            raise ValueError(f"unknown lifecycle state: {to_state!r}")
        from_state = self.state
        transition_id = LEGAL_TRANSITIONS.get((from_state, to_state))
        if transition_id is None:
            return self._reject(
                ILLEGAL_TRANSITION_ID,
                from_state,
                to_state,
                actor_ref=actor_ref,
                attempted_at=attempted_at,
                actor_authority_ref=actor_authority_ref,
                code=REJECT_NOT_IN_TABLE,
                guard_id=None,
                detail=(
                    f"{from_state} -> {to_state} is not in the transition table."
                ),
            )

        guard_evaluations: list[dict[str, Any]] = []
        rejection: tuple[str, str, str] | None = None

        if to_state == "active" and from_state == "retained_dissent":
            if has_unadjudicated_qualified_dissent(self.retained_dissent):
                rejection = (
                    REJECT_ADJUDICATION_PENDING,
                    "G-ADJ-AUTHORITY",
                    "Return to active requires every qualified dissent to be"
                    " adjudicated; at least one adjudication is still pending.",
                )
            else:
                guard_evaluations.append(
                    {"guardId": "G-ADJ-AUTHORITY", "result": "pass"}
                )
        if rejection is None and to_state == "superseded":
            if superseded_by_record_id is None or not _SUCCESSOR_RECORD_ID_RE.fullmatch(
                superseded_by_record_id
            ):
                rejection = (
                    REJECT_SUCCESSOR_MISSING,
                    "G-SUCCESSOR",
                    "Supersession requires a named successor record id.",
                )
            else:
                guard_evaluations.append({"guardId": "G-SUCCESSOR", "result": "pass"})
        if rejection is None and to_state == "expired":
            if not fired_condition_id:
                rejection = (
                    REJECT_EXPIRY_CONDITION_MISSING,
                    "G-EXPIRY-CONDITION",
                    "Expiry requires the id of the condition that fired.",
                )
            else:
                guard_evaluations.append(
                    {"guardId": "G-EXPIRY-CONDITION", "result": "pass"}
                )
        if rejection is None and to_state == "revoked":
            if not (isinstance(revocation_reason, str) and revocation_reason.strip()):
                rejection = (
                    REJECT_REVOCATION_REASON_MISSING,
                    "G-REVOKE-REASON",
                    "Revocation requires a recorded, non-empty reason.",
                )
            elif not revoked_by_authority_ref:
                rejection = (
                    REJECT_REVOCATION_AUTHORITY_MISSING,
                    "G-REVOKE-AUTHORITY",
                    "Revocation requires a revoking authority reference.",
                )
            else:
                guard_evaluations.append(
                    {"guardId": "G-REVOKE-REASON", "result": "pass"}
                )
                guard_evaluations.append(
                    {"guardId": "G-REVOKE-AUTHORITY", "result": "pass"}
                )

        if rejection is not None:
            code, guard_id, detail = rejection
            return self._reject(
                transition_id,
                from_state,
                to_state,
                actor_ref=actor_ref,
                attempted_at=attempted_at,
                actor_authority_ref=actor_authority_ref,
                code=code,
                guard_id=guard_id,
                detail=detail,
            )

        record = self._transition_record(
            transition_id,
            from_state,
            to_state,
            actor_ref=actor_ref,
            attempted_at=attempted_at,
            actor_authority_ref=actor_authority_ref,
            accepted=True,
            guard_evaluations=guard_evaluations,
            rejection_code=None,
        )
        self.transitions.append(record)
        self.state = to_state
        return record

    def _reject(
        self,
        transition_id: str,
        from_state: str,
        to_state: str,
        *,
        actor_ref: str,
        attempted_at: str,
        actor_authority_ref: str | None,
        code: str,
        guard_id: str | None,
        detail: str,
    ) -> dict[str, Any]:
        guard_evaluations: list[dict[str, Any]] = []
        if guard_id is not None:
            guard_evaluations.append(
                {
                    "guardId": guard_id,
                    "result": "fail",
                    "rejectionCode": code,
                    "detail": detail,
                }
            )
        record = self._transition_record(
            transition_id,
            from_state,
            to_state,
            actor_ref=actor_ref,
            attempted_at=attempted_at,
            actor_authority_ref=actor_authority_ref,
            accepted=False,
            guard_evaluations=guard_evaluations,
            rejection_code=code,
        )
        self.transitions.append(record)
        raise TransitionRejected(
            code, from_state, to_state, guard_id=guard_id, detail=detail
        )

    def _transition_record(
        self,
        transition_id: str,
        from_state: str,
        to_state: str,
        *,
        actor_ref: str,
        attempted_at: str,
        actor_authority_ref: str | None,
        accepted: bool,
        guard_evaluations: list[dict[str, Any]],
        rejection_code: str | None,
    ) -> dict[str, Any]:
        return {
            "attemptId": f"TR-{len(self.transitions) + 1:04d}",
            "transitionId": transition_id,
            "from": from_state,
            "to": to_state,
            "attemptedAt": attempted_at,
            "actorRef": actor_ref,
            "actorAuthorityRef": actor_authority_ref,
            "accepted": accepted,
            "guardEvaluations": guard_evaluations,
            "rejectionCode": rejection_code,
        }
