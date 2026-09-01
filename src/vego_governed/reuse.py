"""Reuse-gate engine for ReuseDecisionRecord-v1 (the C3 five-gate procedure).

Executable form of the five ordered gates, the four reuse-eligibility
outcomes, the frozen context-distance ladder, the per-use outcome receipt,
and the replication guard on a transferable-capability-gap claim, all named
by ``schemas/reuse-decision-record-v1.schema.json``. Deterministic and
offline: pure functions over local data, no LLM or network calls. Design
artifact: nothing here asserts an empirical outcome of any kind.

Constraints enforced by construction rather than by convention:

* Gate 1 (visibility/authorization) is evaluated first against the source
  judgment's envelope only. The payload is held behind
  :class:`SealedSourceJudgment` and is released only to a passing gate-1
  evaluation, so a gate-1 failure cannot place source content beyond the
  judgment id anywhere in the returned structure.
* A failing or undetermined gate short-circuits the procedure: later gates
  are recorded as ``not_evaluated`` with no timestamp and no evidence.
* Missing or conflicting evidence yields ``reuse_undetermined`` routed to
  independent review; it is never ``reuse_eligible`` and never
  ``reuse_blocked``.
* Every decision names both the producing rule id and the context dimension
  id, and every evaluation emits an outcome receipt whose
  ``recordedOutcome``/``recordedDimensionId`` are copied from the decision.
* A surfaced prior judgment is built only by the attributed-advice
  constructor, which requires attribution and pins
  ``presented_as_settled_label`` to ``False``.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

SCHEMA_VERSION = "ReuseDecisionRecord-v1"
PROCEDURE_ID = "C3-REUSE-PROC"

# Gate ids in the frozen order of the schema's gateEvaluations prefixItems.
GATE_IDS: tuple[str, ...] = (
    "g1_visibility_authorization",
    "g2_claim_relevance",
    "g3_context_fit",
    "g4_current_case_evidence",
    "g5_adaptation_risk",
)
GATE_RULE_IDS: dict[str, str] = {
    "g1_visibility_authorization": "R-G1-VISIBILITY-AUTHORIZATION",
    "g2_claim_relevance": "R-G2-CLAIM-RELEVANCE",
    "g3_context_fit": "R-G3-CONTEXT-FIT",
    "g4_current_case_evidence": "R-G4-CURRENT-CASE-EVIDENCE",
    "g5_adaptation_risk": "R-G5-ADAPTATION-RISK",
}
RULE_VERSION = "0.1"

RESULT_PASS = "pass"
RESULT_PASS_WITH_ADAPTATION = "pass_with_adaptation"
RESULT_FAIL = "fail"
RESULT_UNDETERMINED = "undetermined"
RESULT_NOT_EVALUATED = "not_evaluated"

OUTCOME_ELIGIBLE = "reuse_eligible"
OUTCOME_ELIGIBLE_WITH_ADAPTATION = "reuse_eligible_with_adaptation"
OUTCOME_BLOCKED = "reuse_blocked"
OUTCOME_UNDETERMINED = "reuse_undetermined"
OUTCOME_LABELS: dict[str, str] = {
    OUTCOME_ELIGIBLE: "Eligible",
    OUTCOME_ELIGIBLE_WITH_ADAPTATION: "Eligible with adaptation",
    OUTCOME_BLOCKED: "Blocked",
    OUTCOME_UNDETERMINED: "Undetermined",
}
EFFECTS: dict[str, str] = {
    OUTCOME_ELIGIBLE: "prior_judgment_surfaced_as_attributed_advice",
    OUTCOME_ELIGIBLE_WITH_ADAPTATION: "prior_judgment_surfaced_as_attributed_advice",
    OUTCOME_BLOCKED: "prior_judgment_withheld",
    OUTCOME_UNDETERMINED: "no_effect_pending_review",
}

# Frozen ladder dimension ids and ranks (schema $defs/contextDistanceSchema).
LADDER_DIMENSIONS: tuple[tuple[str, int], ...] = (
    ("same_case", 0),
    ("submission", 1),
    ("cohort", 2),
    ("modeling_language", 3),
    ("institution", 4),
    ("scenario_family", 5),
)
CONTEXT_DIMENSION_IDS: tuple[str, ...] = tuple(name for name, _ in LADDER_DIMENSIONS)

TOLERANCE_WITHIN = "within_tolerance"
TOLERANCE_ADAPTATION = "adaptation_required"
TOLERANCE_BEYOND = "beyond_tolerance"
TOLERANCES = frozenset({TOLERANCE_WITHIN, TOLERANCE_ADAPTATION, TOLERANCE_BEYOND})

COHORT_RANK = 2
MIN_DISTINCT_CONTEXTS = 2

LIFECYCLE_BLOCKING = frozenset({"expired", "superseded", "revoked"})

ALTERNATIVE_CAUSE_KEYS: tuple[str, ...] = (
    "localGuideline",
    "taskDesign",
    "modelOrSystemVersion",
    "data",
    "reviewerPopulation",
)
CAPABILITY_GAP_DECLARED = "declared_transferable_capability_gap"

C2_CONTRACT_ID = "GovernedJudgmentRecord-v1"
CONTENT_OWNED_BY = "C2 governed-judgment contract (SQ2)"
ISSUANCE_TRIGGER = "every_reuse_decision_evaluation"
CONSUMER_TYPES = frozenset({"agent", "reviewer_interface", "offline_evaluation", "external_system"})
INDEPENDENT_REVIEW_CAUSES = frozenset(
    {
        "missing_evidence",
        "conflicting_evidence",
        "unknown_lifecycle_state",
        "retained_dissent",
        "rule_not_applicable",
    }
)

CANONICALIZATION_METHOD = (
    "Canonical JSON (sorted keys, compact separators, UTF-8), SHA-256 of the result. "
    "decisionRecordSha256 is taken over the evaluation result with the outcomeReceipt "
    "member removed; receiptSha256 is taken over outcomeReceipt with receiptSha256 removed."
)

_EPOCH = "1970-01-01T00:00:00+00:00"

__all__ = [
    "ReuseEngineError",
    "SealedSourceError",
    "CapabilityGapRefusal",
    "SealedSourceJudgment",
    "context_distance",
    "evaluate",
    "claim_capability_gap",
    "GATE_IDS",
    "GATE_RULE_IDS",
    "OUTCOME_LABELS",
    "LADDER_DIMENSIONS",
]


class ReuseEngineError(ValueError):
    """Raised when an input violates the structural obligations of the procedure."""


class SealedSourceError(ReuseEngineError):
    """Raised on any attempt to read a source-judgment payload before gate 1 passed."""


class CapabilityGapRefusal(ReuseEngineError):
    """Raised when a transferable-capability-gap claim fails the replication guard."""


def canonical_json(value: Any) -> str:
    """Return the stable JSON form used for record and receipt digests."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_of(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


class SealedSourceJudgment:
    """Gate-1 seal around a source judgment.

    Before ``unseal`` only the judgment id and the authorization envelope
    (visibility scope, lifecycle read, contract reference) are readable.
    ``unseal`` releases the payload only to a passing gate-1 evaluation, so
    no code path can read judgment content ahead of the authorization gate.
    """

    __slots__ = ("_record", "_unsealed")

    def __init__(self, record: Mapping[str, Any]) -> None:
        if not isinstance(record, Mapping):
            raise ReuseEngineError("source judgment must be a mapping")
        judgment_id = record.get("judgmentId")
        if not isinstance(judgment_id, str) or not judgment_id.strip():
            raise ReuseEngineError("source judgment must carry a non-empty judgmentId")
        self._record = record
        self._unsealed = False

    @property
    def judgment_id(self) -> str:
        return str(self._record["judgmentId"])

    @property
    def envelope(self) -> Mapping[str, Any]:
        """Authorization/lifecycle metadata readable before gate 1."""

        envelope = self._record.get("envelope")
        return envelope if isinstance(envelope, Mapping) else {}

    @property
    def unsealed(self) -> bool:
        return self._unsealed

    def unseal(self, gate_one: Mapping[str, Any]) -> Mapping[str, Any]:
        """Release the payload; callable only with a passing gate-1 evaluation."""

        if gate_one.get("gateId") != GATE_IDS[0] or gate_one.get("result") != RESULT_PASS:
            raise SealedSourceError("source payload stays sealed unless gate 1 passed")
        self._unsealed = True
        return self.payload()

    def payload(self) -> Mapping[str, Any]:
        if not self._unsealed:
            raise SealedSourceError("gate 1 has not passed; the source payload is sealed")
        payload = self._record.get("payload")
        return payload if isinstance(payload, Mapping) else {}


def _validate_ladder(ladder: Mapping[str, Any]) -> None:
    dimensions = (ladder or {}).get("dimensions")
    if not isinstance(dimensions, Sequence) or len(dimensions) != len(LADDER_DIMENSIONS):
        raise ReuseEngineError("ladder must carry the six frozen dimensions of CDS-C3-v1")
    for (expected_id, expected_rank), dimension in zip(LADDER_DIMENSIONS, dimensions, strict=True):
        if dimension.get("dimensionId") != expected_id or dimension.get("rank") != expected_rank:
            raise ReuseEngineError(
                f"ladder dimension order is frozen; expected {expected_id} at rank {expected_rank}"
            )
        if dimension.get("tolerance") not in TOLERANCES:
            raise ReuseEngineError(f"ladder dimension {expected_id} carries no known tolerance")


def context_distance(
    source_values: Mapping[str, Any],
    target_values: Mapping[str, Any],
    ladder: Mapping[str, Any],
) -> dict[str, Any]:
    """Compare two context descriptors dimension-by-dimension against the frozen ladder.

    Returns the schema-shaped comparison set plus ``max_differing_rank`` and
    ``exceeds_cohort``. ``exceedsCohort`` is the frozen above-cohort
    threshold, not a free judgment: true exactly when the highest differing
    dimension outranks cohort (rank 2).
    """

    _validate_ladder(ladder)
    threshold = (ladder.get("capabilityGapThreshold") or {}).get(
        "minRankStrictlyAbove", COHORT_RANK
    )
    comparisons: list[dict[str, Any]] = []
    for dimension in ladder["dimensions"]:
        dimension_id = dimension["dimensionId"]
        rank = int(dimension["rank"])
        source_value = source_values.get(dimension_id)
        target_value = target_values.get(dimension_id)
        if not source_value or not target_value:
            raise ReuseEngineError(
                f"context distance requires a value for dimension '{dimension_id}' on both sides"
            )
        differs = source_value != target_value
        tolerance = dimension["tolerance"] if differs else TOLERANCE_WITHIN
        comparisons.append(
            {
                "dimensionId": dimension_id,
                "rank": rank,
                "sourceValue": source_value,
                "targetValue": target_value,
                "differs": differs,
                "toleranceApplied": tolerance,
                "withinTolerance": tolerance == TOLERANCE_WITHIN,
            }
        )
    differing = [comparison for comparison in comparisons if comparison["differs"]]
    if differing:
        worst = max(differing, key=lambda comparison: comparison["rank"])
        max_differing_dimension_id: str | None = worst["dimensionId"]
        max_differing_rank = int(worst["rank"])
    else:
        max_differing_dimension_id = None
        max_differing_rank = 0
    exceeds_cohort = max_differing_rank > int(threshold)
    return {
        "comparisons": comparisons,
        "maxDifferingDimensionId": max_differing_dimension_id,
        "maxDifferingRank": max_differing_rank,
        "exceedsCohort": exceeds_cohort,
        "computedFromSchemaSha256": ladder.get("sha256") or _sha256_of(ladder),
        "max_differing_rank": max_differing_rank,
        "exceeds_cohort": exceeds_cohort,
    }


def _gate(
    order: int,
    result: str,
    dimension: str | None,
    reason: str,
    *,
    evidence: Sequence[Mapping[str, Any]] | None = None,
    evaluated_at: str | None = None,
    cause: str | None = None,
) -> dict[str, Any]:
    gate_id = GATE_IDS[order - 1]
    return {
        "gateOrder": order,
        "gateId": gate_id,
        "result": result,
        "ruleId": GATE_RULE_IDS[gate_id],
        "ruleVersion": RULE_VERSION,
        "contextDimensionId": dimension,
        "reason": reason,
        "evidenceRefs": [dict(ref) for ref in (evidence or [])],
        "evaluatedAt": evaluated_at,
        "_cause": cause,
    }


def _not_evaluated(order: int, stopped_by: Mapping[str, Any]) -> dict[str, Any]:
    """A gate that never ran: no dimension, no timestamp, no evidence (schema rule)."""

    return _gate(
        order,
        RESULT_NOT_EVALUATED,
        None,
        (
            f"Not evaluated: gate {stopped_by['gateId']} returned "
            f"'{stopped_by['result']}' and the frozen gate order short-circuits."
        ),
    )


def _gate_one(sealed: SealedSourceJudgment, requester_id: str, when: str) -> dict[str, Any]:
    """Visibility/authorization, evaluated before any source content is read."""

    scope = sealed.envelope.get("visibilityScope")
    if not requester_id:
        return _gate(
            1,
            RESULT_UNDETERMINED,
            "institution",
            "Requester identity is missing, so entitlement cannot be established.",
            evaluated_at=when,
            cause="missing_evidence",
        )
    if scope is None:
        return _gate(
            1,
            RESULT_UNDETERMINED,
            "institution",
            f"Source judgment '{sealed.judgment_id}' carries no visibility scope; "
            "entitlement evidence is missing.",
            evaluated_at=when,
            cause="missing_evidence",
        )
    if requester_id in scope:
        return _gate(
            1,
            RESULT_PASS,
            "institution",
            "Evaluated first, before any content of the source judgment was read. "
            f"Requester '{requester_id}' is named in the source judgment's visibility scope.",
            evaluated_at=when,
        )
    return _gate(
        1,
        RESULT_FAIL,
        "institution",
        f"Requester '{requester_id}' is not named in the visibility scope of source "
        f"judgment '{sealed.judgment_id}'. No content of the source judgment was read.",
        evaluated_at=when,
    )


def _gate_two(
    envelope: Mapping[str, Any],
    payload: Mapping[str, Any],
    target_context: Mapping[str, Any],
    when: str,
) -> dict[str, Any]:
    """Read-side currency plus claim relevance."""

    lifecycle = envelope.get("lifecycleStateAtUse", "unknown")
    if lifecycle in LIFECYCLE_BLOCKING:
        return _gate(
            2,
            RESULT_FAIL,
            "same_case",
            f"Source judgment lifecycle state at use is '{lifecycle}'; a judgment that is "
            "not active at the moment of use may not travel.",
            evaluated_at=when,
        )
    if lifecycle == "dissent_retained":
        return _gate(
            2,
            RESULT_UNDETERMINED,
            "same_case",
            "Source judgment retains recorded dissent; the claim's standing is contested "
            "and is routed rather than reused or prohibited.",
            evaluated_at=when,
            cause="retained_dissent",
        )
    if lifecycle != "active":
        return _gate(
            2,
            RESULT_UNDETERMINED,
            "same_case",
            "Source judgment lifecycle state at use is unknown; missing evidence is "
            "neither safe reuse nor permanent prohibition.",
            evaluated_at=when,
            cause="unknown_lifecycle_state",
        )
    source_claim = payload.get("claimKey")
    target_claim = target_context.get("claimKey")
    if not source_claim or not target_claim:
        return _gate(
            2,
            RESULT_UNDETERMINED,
            "scenario_family",
            "The claim answered by the source judgment or raised by the target case is "
            "not recorded; relevance cannot be established.",
            evaluated_at=when,
            cause="missing_evidence",
        )
    if source_claim == target_claim:
        return _gate(
            2,
            RESULT_PASS,
            "scenario_family",
            "The target case raises the same claim the prior ruling answers; relevance is "
            "asserted about the claim, not about textual resemblance.",
            evaluated_at=when,
        )
    return _gate(
        2,
        RESULT_FAIL,
        "scenario_family",
        "The target case raises a different claim than the one the prior ruling answers.",
        evaluated_at=when,
    )


def _gate_three(
    payload: Mapping[str, Any],
    target_context: Mapping[str, Any],
    ladder: Mapping[str, Any],
    when: str,
) -> tuple[dict[str, Any], dict[str, Any] | None, dict[str, Any] | None]:
    """Context fit against the frozen ladder; returns (gate, distance, adaptation)."""

    source_values = (payload.get("sourceContext") or {}).get("dimensionValues") or {}
    target_values = target_context.get("dimensionValues") or {}
    missing = [
        dimension_id
        for dimension_id, _ in LADDER_DIMENSIONS
        if not source_values.get(dimension_id) or not target_values.get(dimension_id)
    ]
    if missing:
        return (
            _gate(
                3,
                RESULT_UNDETERMINED,
                missing[0],
                f"Dimension '{missing[0]}' has no recorded value on both sides; context "
                "distance cannot be computed from missing evidence.",
                evaluated_at=when,
                cause="missing_evidence",
            ),
            None,
            None,
        )
    distance = context_distance(source_values, target_values, ladder)
    differing = [c for c in distance["comparisons"] if c["differs"]]
    beyond = [c for c in differing if c["toleranceApplied"] == TOLERANCE_BEYOND]
    if beyond:
        worst = max(beyond, key=lambda c: c["rank"])
        return (
            _gate(
                3,
                RESULT_FAIL,
                worst["dimensionId"],
                f"Dimension '{worst['dimensionId']}' (rank {worst['rank']}, tolerance "
                f"{TOLERANCE_BEYOND}) differs: source '{worst['sourceValue']}' vs target "
                f"'{worst['targetValue']}'. Reuse is refused rather than adapted.",
                evaluated_at=when,
            ),
            distance,
            None,
        )
    needs_adaptation = [c for c in differing if c["toleranceApplied"] == TOLERANCE_ADAPTATION]
    if needs_adaptation:
        worst = max(needs_adaptation, key=lambda c: c["rank"])
        named = target_context.get("adaptation")
        if not isinstance(named, Mapping) or not named.get("adaptationId"):
            return (
                _gate(
                    3,
                    RESULT_UNDETERMINED,
                    worst["dimensionId"],
                    f"Dimension '{worst['dimensionId']}' (rank {worst['rank']}) requires a "
                    "named adaptation and none is recorded; missing evidence routes to "
                    "independent review.",
                    evaluated_at=when,
                    cause="missing_evidence",
                ),
                distance,
                None,
            )
        adaptation = dict(named)
        adaptation.setdefault("triggeringDimensionId", worst["dimensionId"])
        return (
            _gate(
                3,
                RESULT_PASS_WITH_ADAPTATION,
                worst["dimensionId"],
                f"Dimension '{worst['dimensionId']}' (rank {worst['rank']}, tolerance "
                f"{TOLERANCE_ADAPTATION}) differs: source '{worst['sourceValue']}' vs "
                f"target '{worst['targetValue']}'. The ruling may travel only with the "
                f"named adaptation {adaptation['adaptationId']}.",
                evaluated_at=when,
            ),
            distance,
            adaptation,
        )
    dimension = distance["maxDifferingDimensionId"] or "same_case"
    return (
        _gate(
            3,
            RESULT_PASS,
            dimension,
            "No differing ladder dimension exceeds within_tolerance; the highest differing "
            f"rank is {distance['maxDifferingRank']}.",
            evaluated_at=when,
        ),
        distance,
        None,
    )


def _gate_four(target_context: Mapping[str, Any], when: str) -> dict[str, Any]:
    """Current-case evidence: the case must be decidable on its own terms."""

    if target_context.get("currentCaseEvidenceConflicting") is True:
        return _gate(
            4,
            RESULT_UNDETERMINED,
            "submission",
            "Current-case evidence is recorded as conflicting; conflicting evidence is "
            "neither safe reuse nor permanent prohibition.",
            evaluated_at=when,
            cause="conflicting_evidence",
        )
    if target_context.get("currentCaseDecidableIndependently") is False:
        return _gate(
            4,
            RESULT_FAIL,
            "submission",
            "The only ground for a conclusion in the current case would be the prior "
            "ruling itself; the gate fails.",
            evaluated_at=when,
        )
    evidence = target_context.get("currentCaseEvidenceRefs")
    if not evidence:
        return _gate(
            4,
            RESULT_UNDETERMINED,
            "submission",
            "No current-case evidence is recorded; the case cannot be shown decidable on "
            "its own terms.",
            evaluated_at=when,
            cause="missing_evidence",
        )
    return _gate(
        4,
        RESULT_PASS,
        "submission",
        "The current case carries evidence sufficient to reach a conclusion without the "
        "prior ruling.",
        evidence=evidence,
        evaluated_at=when,
    )


def _gate_five(
    gate_three: Mapping[str, Any],
    adaptation: Mapping[str, Any] | None,
    when: str,
) -> dict[str, Any]:
    """Adaptation risk: bounded and checkable inside the target context."""

    if adaptation is None:
        return _gate(
            5,
            RESULT_PASS,
            gate_three["contextDimensionId"] or "same_case",
            "No adaptation is engaged, so no adaptation risk is carried.",
            evaluated_at=when,
        )
    dimension = adaptation.get("triggeringDimensionId") or gate_three["contextDimensionId"]
    risk = adaptation.get("residualRisk", "unassessed")
    if risk == "high":
        return _gate(
            5,
            RESULT_FAIL,
            dimension,
            f"Adaptation {adaptation.get('adaptationId')} carries high residual risk; the "
            "ruling is withheld rather than adapted.",
            evaluated_at=when,
        )
    if risk in ("low", "moderate"):
        return _gate(
            5,
            RESULT_PASS,
            dimension,
            f"Adaptation {adaptation.get('adaptationId')} carries {risk} residual risk and "
            "is bounded and checkable inside the target context.",
            evaluated_at=when,
        )
    return _gate(
        5,
        RESULT_UNDETERMINED,
        dimension,
        f"Residual risk of adaptation {adaptation.get('adaptationId')} is unassessed; "
        "missing evidence routes to independent review.",
        evaluated_at=when,
        cause="missing_evidence",
    )


def _attributed_advice(
    payload: Mapping[str, Any],
    judgment_id: str,
    adaptation: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Sole constructor of a surfaced prior judgment: attribution is mandatory."""

    attribution = str(payload.get("attribution") or "").strip()
    if not attribution:
        raise ReuseEngineError(
            "a prior judgment may surface only as attributed advice; attribution is required"
        )
    return {
        "presented_as": "attributed_advice",
        "presented_as_settled_label": False,
        "attribution": attribution,
        "attribution_shown": True,
        "judgment_id": judgment_id,
        "judgment_version": payload.get("judgmentVersion"),
        "content": payload.get("rationale"),
        "adaptation": dict(adaptation) if adaptation else None,
    }


def _derive_decision(gates: Sequence[Mapping[str, Any]]) -> tuple[str, Mapping[str, Any]]:
    for gate in gates:
        if gate["result"] == RESULT_FAIL:
            return OUTCOME_BLOCKED, gate
    for gate in gates:
        if gate["result"] == RESULT_UNDETERMINED:
            return OUTCOME_UNDETERMINED, gate
    for gate in gates:
        if gate["result"] == RESULT_PASS_WITH_ADAPTATION:
            return OUTCOME_ELIGIBLE_WITH_ADAPTATION, gate
    return OUTCOME_ELIGIBLE, gates[-1]


def evaluate(
    source_judgment: Mapping[str, Any],
    target_context: Mapping[str, Any],
    requester: Mapping[str, Any],
    ladder: Mapping[str, Any],
    *,
    evaluated_at: str | None = None,
) -> dict[str, Any]:
    """Run the five-gate reuse procedure and emit a decision plus outcome receipt.

    ``source_judgment`` splits into ``judgmentId``, an ``envelope`` (visibility
    scope, lifecycle read, contract reference) readable at gate 1, and a
    ``payload`` (claim, rationale, attribution, source context) sealed until
    gate 1 passes. ``target_context`` is a TargetContextDescriptor-shaped
    mapping plus the current-case evidence inputs. ``ladder`` is the frozen
    CDS-C3-v1 context-distance schema. ``evaluated_at`` fixes every timestamp
    in the result; no clock is read.
    """

    _validate_ladder(ladder)
    sealed = SealedSourceJudgment(source_judgment)
    when = evaluated_at or str(target_context.get("capturedAt") or _EPOCH)
    requester_id = str(requester.get("requesterId") or "").strip()

    gates: list[dict[str, Any]] = []
    distance: dict[str, Any] | None = None
    adaptation: dict[str, Any] | None = None

    gate_one = _gate_one(sealed, requester_id, when)
    gates.append(gate_one)
    if gate_one["result"] == RESULT_PASS:
        payload = sealed.unseal(gate_one)
        gate_two = _gate_two(sealed.envelope, payload, target_context, when)
        gates.append(gate_two)
        if gate_two["result"] == RESULT_PASS:
            gate_three, distance, adaptation = _gate_three(payload, target_context, ladder, when)
            gates.append(gate_three)
            if gate_three["result"] in (RESULT_PASS, RESULT_PASS_WITH_ADAPTATION):
                gate_four = _gate_four(target_context, when)
                gates.append(gate_four)
                if gate_four["result"] == RESULT_PASS:
                    gates.append(_gate_five(gate_three, adaptation, when))
    stopped_by = gates[-1]
    while len(gates) < len(GATE_IDS):
        gates.append(_not_evaluated(len(gates) + 1, stopped_by))

    outcome, deciding_gate = _derive_decision(gates)
    cause = deciding_gate.get("_cause")
    for gate in gates:
        gate.pop("_cause", None)

    decision_dimension = deciding_gate["contextDimensionId"] or "same_case"
    decision = {
        "outcome": outcome,
        "outcomeLabel": OUTCOME_LABELS[outcome],
        "gateId": deciding_gate["gateId"],
        "ruleId": deciding_gate["ruleId"],
        "ruleVersion": deciding_gate["ruleVersion"],
        "contextDimensionId": decision_dimension,
        "statement": (
            f"{OUTCOME_LABELS[outcome]}. Produced by rule {deciding_gate['ruleId']} "
            f"v{deciding_gate['ruleVersion']} at gate {deciding_gate['gateId']}; the "
            f"responsible context dimension is {decision_dimension}. "
            f"{deciding_gate['reason']}"
        ),
    }
    if outcome == OUTCOME_UNDETERMINED:
        decision["statement"] += (
            " Routed to independent review; treated neither as safe reuse nor as "
            "permanent prohibition."
        )

    if sealed.unsealed:
        envelope = sealed.envelope
        payload = sealed.payload()
        source_ref: dict[str, Any] = {
            "judgmentId": sealed.judgment_id,
            "judgmentVersion": payload.get("judgmentVersion", "unknown"),
            "judgmentSha256": payload.get("judgmentSha256"),
            "contractId": envelope.get("contractId", C2_CONTRACT_ID),
            "contractVersion": envelope.get("contractVersion", "1.0"),
            "lifecycleStateAtUse": envelope.get("lifecycleStateAtUse", "unknown"),
            "lifecycleReadAt": envelope.get("lifecycleReadAt", when),
        }
        contract_id = envelope.get("contractId", C2_CONTRACT_ID)
        contract_version = envelope.get("contractVersion", "1.0")
    else:
        # Gate 1 did not pass: the payload was never read, so nothing of the
        # source judgment beyond its id can enter the result.
        source_ref = {"judgmentId": sealed.judgment_id}
        contract_id = C2_CONTRACT_ID
        contract_version = "1.0"

    seed = _sha256_of(
        {
            "judgmentId": sealed.judgment_id,
            "useSiteRef": target_context.get("caseRef"),
            "requesterId": requester_id,
            "evaluatedAt": when,
            "outcome": outcome,
        }
    )[:16]

    result: dict[str, Any] = {
        "recordId": f"RDR-{seed}",
        "emittedAt": when,
        "procedure": {
            "procedureId": PROCEDURE_ID,
            "gateCount": len(GATE_IDS),
            "gateOrderFrozen": True,
        },
        "sourceJudgmentRef": source_ref,
        "targetContextRef": {
            "descriptorId": target_context.get("descriptorId"),
            "caseRef": target_context.get("caseRef"),
        },
        "contextDistance": distance,
        "restrictedEvidenceExposed": sealed.unsealed,
        "gateEvaluations": gates,
        "decision": decision,
        "effect": EFFECTS[outcome],
        "routed_to_independent_review": outcome == OUTCOME_UNDETERMINED,
    }
    if outcome == OUTCOME_UNDETERMINED:
        review_cause = cause if cause in INDEPENDENT_REVIEW_CAUSES else "missing_evidence"
        result["independentReview"] = {
            "routed": True,
            "routedTo": "independent_review",
            "reviewRequestId": f"IRR-{seed}",
            "routedAt": when,
            "reviewStatus": "routed",
            "treatedAsSafeReuse": False,
            "treatedAsPermanentProhibition": False,
            "cause": review_cause,
        }
    if outcome in (OUTCOME_ELIGIBLE, OUTCOME_ELIGIBLE_WITH_ADAPTATION):
        result["advice"] = _attributed_advice(sealed.payload(), sealed.judgment_id, adaptation)
        if outcome == OUTCOME_ELIGIBLE_WITH_ADAPTATION and adaptation is not None:
            result["adaptation"] = dict(adaptation)

    consumer_type = requester.get("consumerType", "agent")
    if consumer_type not in CONSUMER_TYPES:
        raise ReuseEngineError(f"unknown consumerType '{consumer_type}'")
    receipt = {
        "receiptId": f"RDR-RCPT-{seed}",
        "issuedAt": when,
        "issuanceTrigger": ISSUANCE_TRIGGER,
        "consumerId": requester_id or "unspecified-consumer",
        "consumerType": consumer_type,
        "useSiteRef": str(
            target_context.get("caseRef")
            or target_context.get("descriptorId")
            or "unspecified-use-site"
        ),
        "recordedOutcome": decision["outcome"],
        "recordedDimensionId": decision["contextDimensionId"],
        "decisionRecordSha256": _sha256_of(result),
        "canonicalizationMethod": CANONICALIZATION_METHOD,
        "contentContract": {
            "contractId": contract_id,
            "contractVersion": contract_version,
            "contentOwnedBy": CONTENT_OWNED_BY,
        },
        "linkedFromSourceJudgment": False,
    }
    receipt["receiptSha256"] = _sha256_of(receipt)
    result["outcomeReceipt"] = receipt
    return result


def claim_capability_gap(
    candidate: Mapping[str, Any],
    replications: Sequence[Mapping[str, Any]],
    *,
    ladder: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Apply the replication guard to a transferable-capability-gap candidate.

    Refuses (raises :class:`CapabilityGapRefusal`) unless the candidate's
    failure signature is predeclared, at least ``minDistinctContexts`` (2)
    pairwise-distinct frozen replication contexts each matched the signature
    at a rank strictly above cohort (rank 2), independent confirmation is
    recorded, and all five alternative causes are assessed and ruled out.
    Requiring every qualifying context to sit strictly above cohort is at
    least as strict as the stored-record schema floor (two distinct contexts
    of which at least one exceeds cohort), so every accepted claim also
    satisfies the schema's replication clause.
    """

    threshold = (ladder or {}).get("capabilityGapThreshold") or {}
    min_rank = int(threshold.get("minRankStrictlyAbove", COHORT_RANK))
    min_contexts = int(threshold.get("minDistinctContexts", MIN_DISTINCT_CONTEXTS))
    refusals: list[str] = []

    signature = (candidate or {}).get("failureSignature") or {}
    if not signature.get("signatureId") or not signature.get("predeclaredAt"):
        refusals.append("the failure signature is not predeclared")

    qualifying: dict[str, Mapping[str, Any]] = {}
    for replication in replications or []:
        context_sha = replication.get("contextSha256")
        rank = replication.get("distanceFromSourceRank")
        if (
            isinstance(context_sha, str)
            and context_sha
            and replication.get("contextFrozenAt")
            and replication.get("signatureMatched") is True
            and isinstance(rank, int)
            and rank > min_rank
        ):
            qualifying[context_sha] = replication
    if len(qualifying) < min_contexts:
        refusals.append(
            f"requires at least {min_contexts} pairwise-distinct frozen replication "
            f"contexts matched strictly above rank {min_rank}; found {len(qualifying)}"
        )
    if candidate.get("distinctFrozenContextsConfirmed") is not True:
        refusals.append("distinct frozen contexts are not confirmed")
    confirmation = candidate.get("independentConfirmation") or {}
    if confirmation.get("confirmed") is not True:
        refusals.append("independent confirmation is not recorded")
    causes = candidate.get("alternativeCausesRuledOut") or {}
    unresolved = [
        key
        for key in ALTERNATIVE_CAUSE_KEYS
        if (causes.get(key) or {}).get("status") != "ruled_out"
    ]
    if unresolved:
        refusals.append("alternative causes not assessed and ruled out: " + ", ".join(unresolved))
    if refusals:
        raise CapabilityGapRefusal(
            "transferable-capability-gap claim refused: " + "; ".join(refusals)
        )

    declared = dict(candidate)
    declared["status"] = CAPABILITY_GAP_DECLARED
    declared["replications"] = [dict(replication) for replication in replications]
    return declared
