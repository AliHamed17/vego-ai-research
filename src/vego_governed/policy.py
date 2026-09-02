"""Selective-intervention policy engine v2: the six section 3.3 comparator arms.

One engine, six configurations. Each comparator arm named in proposal section
3.3 (never ask, always ask, random review at the same budget, uncertainty only,
a fixed threshold, and the proposed policy) is expressed as an ``Arm``
configuration of this single engine, so all six are replayable head-to-head
over identical frozen event inputs. Engine arm ids map onto the
ReviewPolicySignalContract-v1 ``policyArm.family`` enumeration via
``ARM_TO_SCHEMA_FAMILY``.

Vocabulary sources (restated, never invented)
---------------------------------------------
- ``SIGNAL_IDS``: the eight signal ids fixed by
  schemas/review-policy-signal-contract-v1.schema.json ($defs/signalId).
- ``AUTHORITY_LADDER``: the ordered mandate ladder from
  $defs/assertedAuthority.value of the same schema.
- ``BUDGET_STATES``: the shared H-layer budget vocabulary
  {within_budget, capped, deferred, evaluation_only}
  (src/vego_hlayer/contracts.py, read-only sibling).
- ``TRIGGER_*``: trigger-reason codes verbatim from the protected
  VEGO-AI/framework/selective_intervention_policy.py (read-only dependency).
- ``DEFAULT_PROPOSED_WEIGHTS``: mirrors the combinationRule.weights shape and
  illustrative values of
  schemas/examples/review-policy-signal-contract.valid.json.

Constraints
-----------
- Pure deterministic Python over local data: no LLM/API calls, no network, no
  wall-clock reads, no OS randomness. The random arm is seeded explicitly and
  draws via SHA-256 over ``(seed, event_id)``, so replays are reproducible and
  order-independent.
- Budget ledger is unit-based; an exhausted budget turns demanded escalations
  into ``deferred`` decisions. Nothing is silently dropped: every input event
  appears in exactly one of the escalated / deferred / declined sets.
- Selective-risk accounting: ``replay`` returns per-event decisions plus the
  not-escalated event-id set, so an error-remaining denominator is computable
  later once independently established labels exist. The fixture events carry
  NO ground-truth labels and this module fabricates none.

Claim boundary
--------------
Mechanism/design artifact only. Nothing in this module, its fixtures, or its
tests asserts improved accuracy, reduced effort, generalization, or any other
empirical outcome. EXP-005 labels remain 0/24; no outcome is computable.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any

ENGINE_VERSION = "selective-intervention-policy-v2"

SIGNAL_CLAIM_UNCERTAINTY = "claim_uncertainty"
SIGNAL_UNREVIEWED_ERROR_CONSEQUENCE = "unreviewed_error_consequence"
SIGNAL_EVIDENCE_QUALITY = "evidence_quality"
SIGNAL_REVIEWER_COMPETENCE = "reviewer_competence_for_claim"
SIGNAL_QUEUE_CONDITIONS = "current_queue_conditions"
SIGNAL_NOVELTY = "novelty_vs_judgment_store"
SIGNAL_CROSS_AGENT_DISAGREEMENT = "cross_agent_disagreement"
SIGNAL_EXPECTED_REUSE = "expected_future_reuse_value"
SIGNAL_IDS: tuple[str, ...] = (
    SIGNAL_CLAIM_UNCERTAINTY,
    SIGNAL_UNREVIEWED_ERROR_CONSEQUENCE,
    SIGNAL_EVIDENCE_QUALITY,
    SIGNAL_REVIEWER_COMPETENCE,
    SIGNAL_QUEUE_CONDITIONS,
    SIGNAL_NOVELTY,
    SIGNAL_CROSS_AGENT_DISAGREEMENT,
    SIGNAL_EXPECTED_REUSE,
)

ARM_NEVER_ASK = "never_ask"
ARM_ALWAYS_ASK = "always_ask"
ARM_RANDOM_AT_BUDGET = "random_at_budget"
ARM_UNCERTAINTY_ONLY = "uncertainty_only"
ARM_FIXED_THRESHOLD = "fixed_threshold"
ARM_PROPOSED_JOINT_POLICY = "proposed_joint_policy"
ARM_TO_SCHEMA_FAMILY: Mapping[str, str] = {
    ARM_NEVER_ASK: "never_ask",
    ARM_ALWAYS_ASK: "always_ask",
    ARM_RANDOM_AT_BUDGET: "random_at_matched_budget",
    ARM_UNCERTAINTY_ONLY: "uncertainty_only",
    ARM_FIXED_THRESHOLD: "fixed_threshold",
    ARM_PROPOSED_JOINT_POLICY: "proposed_policy",
}
ARM_IDS: tuple[str, ...] = tuple(ARM_TO_SCHEMA_FAMILY)

BUDGET_STATE_WITHIN = "within_budget"
BUDGET_STATE_CAPPED = "capped"
BUDGET_STATE_DEFERRED = "deferred"
BUDGET_STATE_EVALUATION_ONLY = "evaluation_only"
BUDGET_STATES: tuple[str, ...] = (
    BUDGET_STATE_WITHIN,
    BUDGET_STATE_CAPPED,
    BUDGET_STATE_DEFERRED,
    BUDGET_STATE_EVALUATION_ONLY,
)

AUTHORITY_LADDER: tuple[str, ...] = (
    "none",
    "advisory",
    "decides_with_review",
    "decides",
    "decides_and_may_amend_guideline",
)

TRIGGER_AGENT_REQUESTED = "agent_requested_human_review"
TRIGGER_UNDETERMINED = "undetermined_classification"
TRIGGER_LOW_CONFIDENCE = "low_confidence"
TRIGGER_MEDIUM_CONFIDENCE = "medium_confidence"
TRIGGER_GUIDELINE_UPDATE = "guideline_update_proposed"

ESCALATION_UNIT_COST = 1

DEFAULT_PROPOSED_WEIGHTS: tuple[Mapping[str, Any], ...] = (
    {"signalId": SIGNAL_CLAIM_UNCERTAINTY, "weight": 0.26, "weightVersion": "weights-1.0.0"},
    {
        "signalId": SIGNAL_UNREVIEWED_ERROR_CONSEQUENCE,
        "weight": 0.22,
        "weightVersion": "weights-1.0.0",
    },
    {"signalId": SIGNAL_EVIDENCE_QUALITY, "weight": -0.16, "weightVersion": "weights-1.0.0"},
    {"signalId": SIGNAL_REVIEWER_COMPETENCE, "weight": 0.12, "weightVersion": "weights-1.0.0"},
    {"signalId": SIGNAL_QUEUE_CONDITIONS, "weight": -0.14, "weightVersion": "weights-1.0.0"},
    {"signalId": SIGNAL_NOVELTY, "weight": 0.14, "weightVersion": "weights-1.0.0"},
    {
        "signalId": SIGNAL_CROSS_AGENT_DISAGREEMENT,
        "weight": 0.12,
        "weightVersion": "weights-1.0.0",
    },
    {"signalId": SIGNAL_EXPECTED_REUSE, "weight": 0.10, "weightVersion": "weights-1.0.0"},
)


class PolicyValidationError(ValueError):
    """Raised when an arm configuration, ledger, or event violates the engine contract."""


def canonical_json(value: Any) -> str:
    """Return stable JSON used for byte-identical replay comparisons."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class Arm:
    """One comparator-arm configuration of the single policy engine.

    ``arm_id`` must be one of ``ARM_IDS``. ``params`` carries arm-specific
    configuration; unknown keys are rejected so a frozen configuration cannot
    silently carry dead knobs.

    Recognized params per arm
    -------------------------
    - random_at_budget: ``seed`` (required int; never wall-clock, never OS
      randomness) and ``selection_probability`` (float in [0, 1], default 0.5).
    - uncertainty_only: ``include_medium`` (default True),
      ``low_confidence_floor`` (default 0.75), ``medium_confidence_floor``
      (default 0.5), ``guideline_novelty_floor`` (default 0.9).
    - fixed_threshold: ``threshold`` (default 0.6) and ``signal_ids`` (declared
      signal subset; default claim_uncertainty + unreviewed_error_consequence).
    - proposed_joint_policy: ``weights`` (combinationRule.weights-shaped list,
      default DEFAULT_PROPOSED_WEIGHTS), ``escalation_threshold`` (default
      0.35), ``competence_floor`` (default 0.4).
    """

    arm_id: str
    params: Mapping[str, Any] = field(default_factory=dict)

    _ALLOWED_PARAMS = {
        ARM_NEVER_ASK: frozenset(),
        ARM_ALWAYS_ASK: frozenset(),
        ARM_RANDOM_AT_BUDGET: frozenset({"seed", "selection_probability"}),
        ARM_UNCERTAINTY_ONLY: frozenset(
            {
                "include_medium",
                "low_confidence_floor",
                "medium_confidence_floor",
                "guideline_novelty_floor",
            }
        ),
        ARM_FIXED_THRESHOLD: frozenset({"threshold", "signal_ids"}),
        ARM_PROPOSED_JOINT_POLICY: frozenset(
            {"weights", "escalation_threshold", "competence_floor"}
        ),
    }

    def __post_init__(self) -> None:
        if self.arm_id not in ARM_TO_SCHEMA_FAMILY:
            raise PolicyValidationError(
                f"arm_id must be one of {sorted(ARM_IDS)}, got {self.arm_id!r}"
            )
        if not isinstance(self.params, Mapping):
            raise PolicyValidationError("params must be a mapping")
        unknown = set(self.params) - self._ALLOWED_PARAMS[self.arm_id]
        if unknown:
            raise PolicyValidationError(
                f"unknown params for arm {self.arm_id}: {sorted(unknown)}"
            )
        if self.arm_id == ARM_RANDOM_AT_BUDGET:
            seed = self.params.get("seed")
            if not isinstance(seed, int) or isinstance(seed, bool):
                raise PolicyValidationError(
                    "random_at_budget requires an explicit integer 'seed' param"
                )
            probability = self.params.get("selection_probability", 0.5)
            if not isinstance(probability, (int, float)) or not 0.0 <= float(probability) <= 1.0:
                raise PolicyValidationError("selection_probability must be within [0, 1]")
        if self.arm_id == ARM_FIXED_THRESHOLD:
            for signal_id in self.params.get("signal_ids", ()):
                if signal_id not in SIGNAL_IDS:
                    raise PolicyValidationError(f"unknown signal id {signal_id!r}")
        if self.arm_id == ARM_PROPOSED_JOINT_POLICY:
            for entry in self.params.get("weights", ()):
                if (
                    not isinstance(entry, Mapping)
                    or entry.get("signalId") not in SIGNAL_IDS
                    or not isinstance(entry.get("weight"), (int, float))
                    or not isinstance(entry.get("weightVersion"), str)
                ):
                    raise PolicyValidationError(
                        "weights entries must carry signalId/weight/weightVersion "
                        "per the combinationRule.weights contract shape"
                    )

    @property
    def schema_family(self) -> str:
        return ARM_TO_SCHEMA_FAMILY[self.arm_id]


@dataclass(frozen=True)
class BudgetLedger:
    """Unit-based attention budget. Immutable: charging returns a new ledger.

    ``evaluation_only`` marks a ledger that never charges units; every decision
    made against it reports the ``evaluation_only`` budget state. When the
    budget is exhausted, demanded escalations become ``deferred`` decisions and
    are never silently dropped.
    """

    amount: int
    consumed: int = 0
    evaluation_only: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.amount, int) or isinstance(self.amount, bool) or self.amount < 0:
            raise PolicyValidationError("amount must be a non-negative integer unit count")
        if (
            not isinstance(self.consumed, int)
            or isinstance(self.consumed, bool)
            or not 0 <= self.consumed <= self.amount
        ):
            raise PolicyValidationError("consumed must be an integer within [0, amount]")

    @property
    def remaining(self) -> int:
        return self.amount - self.consumed

    def charge(self, units: int) -> BudgetLedger:
        if units > self.remaining:
            raise PolicyValidationError("cannot charge past the budget cap")
        return BudgetLedger(self.amount, self.consumed + units, self.evaluation_only)

    def to_dict(self) -> dict[str, Any]:
        return {
            "amount": self.amount,
            "consumed": self.consumed,
            "remaining": self.remaining,
            "evaluation_only": self.evaluation_only,
        }


@dataclass(frozen=True)
class Decision:
    """One arm's routing decision over one claim event. Carries no labels."""

    event_id: str
    arm_id: str
    escalate: bool
    reason: str
    budget_state: str
    selected_reviewer_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "arm_id": self.arm_id,
            "escalate": self.escalate,
            "reason": self.reason,
            "budget_state": self.budget_state,
            "selected_reviewer_id": self.selected_reviewer_id,
        }


@dataclass(frozen=True)
class ArmReplayLedger:
    """Replay result for one arm over one frozen event sequence.

    The three event-id sets partition the input exactly:
    ``escalated_event_ids`` (charged escalations), ``deferred_event_ids``
    (escalations demanded after budget exhaustion; queued, never dropped), and
    ``declined_event_ids`` (the arm chose not to escalate).
    ``not_escalated_event_ids`` (declined + deferred, in input order) is the
    selective-risk denominator candidate set: the error-remaining numerator is
    NOT computable here because the fixture events carry no ground-truth labels
    and this module fabricates none.
    """

    arm_id: str
    decisions: tuple[Decision, ...]
    escalated_event_ids: tuple[str, ...]
    deferred_event_ids: tuple[str, ...]
    declined_event_ids: tuple[str, ...]
    budget: BudgetLedger

    @property
    def not_escalated_event_ids(self) -> tuple[str, ...]:
        not_escalated = set(self.declined_event_ids) | set(self.deferred_event_ids)
        return tuple(d.event_id for d in self.decisions if d.event_id in not_escalated)

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine_version": ENGINE_VERSION,
            "arm_id": self.arm_id,
            "schema_family": ARM_TO_SCHEMA_FAMILY[self.arm_id],
            "decisions": [d.to_dict() for d in self.decisions],
            "escalated_event_ids": list(self.escalated_event_ids),
            "deferred_event_ids": list(self.deferred_event_ids),
            "declined_event_ids": list(self.declined_event_ids),
            "not_escalated_event_ids": list(self.not_escalated_event_ids),
            "budget": self.budget.to_dict(),
            "event_count": len(self.decisions),
        }

    def to_json(self) -> str:
        return canonical_json(self.to_dict())


def _observation(event: Mapping[str, Any], signal_id: str) -> Mapping[str, Any] | None:
    for obs in event.get("signalObservations", ()):
        if isinstance(obs, Mapping) and obs.get("signalId") == signal_id:
            return obs
    return None


def _has_explicit_escalation_request(event: Mapping[str, Any], signal_id: str) -> bool:
    """Return whether an independently observed human-review request exists."""
    return any(
        isinstance(request, Mapping)
        and request.get("signalId") == signal_id
        and request.get("trigger") == TRIGGER_AGENT_REQUESTED
        and request.get("evidenceState") == "observed"
        for request in event.get("explicitEscalationRequests", ())
    )


def _normalized(observation: Mapping[str, Any] | None) -> float | None:
    if observation is None or observation.get("missing") is True:
        return None
    value = observation.get("normalizedValue")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


def _seeded_unit_draw(seed: int, event_id: str) -> float:
    """Map (seed, event_id) onto [0, 1) via SHA-256; no wall clock, no OS entropy."""

    digest = sha256(f"{seed}|{event_id}".encode()).digest()
    return int.from_bytes(digest[:8], "big") / 2**64


def select_reviewer(
    candidates: Sequence[Mapping[str, Any]],
    *,
    competence_floor: float = 0.4,
    fragment_id: str | None = None,
) -> str | None:
    """Competence/authority-aware reviewer selection over a candidate list.

    DESIGN PLACEHOLDER pending supervisor decision ISS-043: the selection
    function below (highest asserted authority among available candidates whose
    fragment-scoped assessed competence clears ``competence_floor``; ties break
    to higher competence, then lexicographically smallest candidateId) is one
    admissible instantiation of ``selectionFunction ==
    competence_and_authority_jointly`` and has NOT been ratified. It exists so
    the proposed arm is executable in replay; the ratified function may differ.

    A candidate is selectable only when ``available`` is true, the authority
    assertion is ``active`` with fragment scope matching ``fragment_id`` (when
    given), and the competence assessment is fragment-scoped
    (``assessmentScope == "contested_fragment"``) with a numeric value at or
    above the floor. Authority is compared on the contract's ordered mandate
    ladder, never summed with competence: the two stay on separate value spaces
    per the contract's independence constraint. The candidateId tie-break is
    compared explicitly (smaller wins) because it sorts opposite to the two
    value components.
    """

    best_key: tuple[int, float, str] | None = None
    best_candidate: str | None = None
    for candidate in candidates:
        if not isinstance(candidate, Mapping) or candidate.get("available") is not True:
            continue
        candidate_id = candidate.get("candidateId")
        competence = candidate.get("assessedCompetence")
        authority = candidate.get("assertedAuthority")
        if not isinstance(candidate_id, str) or not candidate_id:
            continue
        if not isinstance(competence, Mapping) or not isinstance(authority, Mapping):
            continue
        if authority.get("status") != "active":
            continue
        if competence.get("assessmentScope") != "contested_fragment":
            continue
        if fragment_id is not None and (
            competence.get("fragmentId") != fragment_id
            or authority.get("fragmentId") != fragment_id
        ):
            continue
        competence_value = competence.get("value")
        if (
            not isinstance(competence_value, (int, float))
            or isinstance(competence_value, bool)
            or competence_value < competence_floor
        ):
            continue
        authority_value = authority.get("value")
        if authority_value not in AUTHORITY_LADDER:
            continue
        key = (AUTHORITY_LADDER.index(authority_value), float(competence_value), candidate_id)
        if (
            best_key is None
            or key[0] > best_key[0]
            or (key[0] == best_key[0] and key[1] > best_key[1])
            or (key[0] == best_key[0] and key[1] == best_key[1] and key[2] < best_key[2])
        ):
            best_key = key
            best_candidate = candidate_id
    return best_candidate


def _never_ask_trigger(
    arm: Arm, event: Mapping[str, Any]
) -> tuple[bool, str, str | None]:
    return False, "arm_never_asks", None


def _always_ask_trigger(
    arm: Arm, event: Mapping[str, Any]
) -> tuple[bool, str, str | None]:
    return True, "arm_always_asks", None


def _random_trigger(arm: Arm, event: Mapping[str, Any]) -> tuple[bool, str, str | None]:
    seed = arm.params["seed"]
    probability = float(arm.params.get("selection_probability", 0.5))
    draw = _seeded_unit_draw(seed, str(event.get("eventId")))
    if draw < probability:
        return True, f"seeded_draw={draw:.6f}<selection_probability={probability:.4f}", None
    return False, f"seeded_draw={draw:.6f}>=selection_probability={probability:.4f}", None


def _uncertainty_only_trigger(
    arm: Arm, event: Mapping[str, Any]
) -> tuple[bool, str, str | None]:
    """Trigger semantics of the protected shipped policy, expressed over contract signals.

    This arm IS the shipped VEGO-AI selective-intervention policy
    (VEGO-AI/framework/selective_intervention_policy.py, POLICY_VERSION
    human-review-policy-v1) restated as a section 3.3 comparator: escalate iff
    the agent requested review, the classification is undetermined, confidence
    is low, confidence is medium (when ``include_medium``), or a guideline
    update is proposed. The protected module reads raw Agent 4 fields; this
    comparator reads the same triggers mapped onto ReviewPolicySignalContract-v1
    signal fields as follows:

    - agent_requested_human_review (requires_human_review == True): an
      independently observed ``explicitEscalationRequests`` fact for
      claim_uncertainty. The legacy claim_uncertainty representation with
      ``missing == true`` and ``missingValuePolicy == "force_escalation"``
      remains supported when no numeric value exists.
    - undetermined_classification (classification == "Undetermined"):
      evidence_quality observation with ``missing == true`` and
      ``missingValuePolicy == "force_undetermined"`` (no evidence-quality
      value is computable for an undetermined classification).
    - low_confidence (confidence == "Low"): claim_uncertainty
      ``normalizedValue >= low_confidence_floor`` (default 0.75).
    - medium_confidence (confidence == "Medium", only if ``include_medium``):
      ``medium_confidence_floor <= normalizedValue < low_confidence_floor``
      (default band [0.5, 0.75)); the bands are disjoint, mirroring the
      protected module's low-elif-medium evaluation order.
    - guideline_update_proposed (flag_for_guidelines_update == True):
      novelty_vs_judgment_store ``normalizedValue >= guideline_novelty_floor``
      (default 0.9; a proposed guideline change is extreme novelty relative to
      the judgment store, and the human owns the rubric).

    All firing trigger codes are collected into the reason string in the
    protected module's evaluation order.
    """

    params = arm.params
    include_medium = bool(params.get("include_medium", True))
    low_floor = float(params.get("low_confidence_floor", 0.75))
    medium_floor = float(params.get("medium_confidence_floor", 0.5))
    novelty_floor = float(params.get("guideline_novelty_floor", 0.9))

    reasons: list[str] = []
    uncertainty = _observation(event, SIGNAL_CLAIM_UNCERTAINTY)
    if (
        _has_explicit_escalation_request(event, SIGNAL_CLAIM_UNCERTAINTY)
        or (
            uncertainty is not None
            and uncertainty.get("missing") is True
            and uncertainty.get("missingValuePolicy") == "force_escalation"
        )
    ):
        reasons.append(TRIGGER_AGENT_REQUESTED)
    evidence = _observation(event, SIGNAL_EVIDENCE_QUALITY)
    if (
        evidence is not None
        and evidence.get("missing") is True
        and evidence.get("missingValuePolicy") == "force_undetermined"
    ):
        reasons.append(TRIGGER_UNDETERMINED)
    uncertainty_value = _normalized(uncertainty)
    if uncertainty_value is not None:
        if uncertainty_value >= low_floor:
            reasons.append(TRIGGER_LOW_CONFIDENCE)
        elif uncertainty_value >= medium_floor and include_medium:
            reasons.append(TRIGGER_MEDIUM_CONFIDENCE)
    novelty_value = _normalized(_observation(event, SIGNAL_NOVELTY))
    if novelty_value is not None and novelty_value >= novelty_floor:
        reasons.append(TRIGGER_GUIDELINE_UPDATE)

    if reasons:
        return True, "+".join(reasons), None
    return False, "no_trigger_fired", None


def _fixed_threshold_trigger(
    arm: Arm, event: Mapping[str, Any]
) -> tuple[bool, str, str | None]:
    """Fixed threshold over the unweighted mean of the declared signals.

    Missing observations are excluded from the mean (they carry no
    normalizedValue); an event with no computable declared signal is not
    escalated and says so in the reason.
    """

    threshold = float(arm.params.get("threshold", 0.6))
    signal_ids = tuple(
        arm.params.get(
            "signal_ids", (SIGNAL_CLAIM_UNCERTAINTY, SIGNAL_UNREVIEWED_ERROR_CONSEQUENCE)
        )
    )
    values = [
        value
        for value in (_normalized(_observation(event, signal_id)) for signal_id in signal_ids)
        if value is not None
    ]
    if not values:
        return False, "no_declared_signal_values_available", None
    score = sum(values) / len(values)
    if score >= threshold:
        return True, f"mean_signal_score={score:.4f}>=fixed_threshold={threshold:.4f}", None
    return False, f"mean_signal_score={score:.4f}<fixed_threshold={threshold:.4f}", None


def _proposed_trigger(arm: Arm, event: Mapping[str, Any]) -> tuple[bool, str, str | None]:
    """Joint weighted combination of the declared signals plus reviewer selection.

    Combined score follows the contract's combinationRule shape: a weighted sum
    of per-signal normalized values with signed coefficients (burden and
    evidence quality enter negatively in the default weights). An explicit
    escalation request, or a legacy missing signal whose declared
    ``missingValuePolicy`` is ``force_escalation``, escalates outright; other
    missing signals are excluded from the score. When the score clears
    ``escalation_threshold``, the reviewer is chosen by
    ``select_reviewer`` (a DESIGN PLACEHOLDER pending supervisor decision
    ISS-043; see its docstring).
    """

    weights = tuple(arm.params.get("weights", DEFAULT_PROPOSED_WEIGHTS))
    threshold = float(arm.params.get("escalation_threshold", 0.35))
    competence_floor = float(arm.params.get("competence_floor", 0.4))
    fragment_id = event.get("fragmentId")
    candidates = event.get("reviewerCandidates", ())

    for entry in weights:
        if _has_explicit_escalation_request(event, str(entry["signalId"])):
            reviewer = select_reviewer(
                candidates,
                competence_floor=competence_floor,
                fragment_id=fragment_id if isinstance(fragment_id, str) else None,
            )
            reason = f"explicit_review_request:{entry['signalId']}"
            reason += (
                f"+selected_reviewer={reviewer}" if reviewer else "+no_selectable_reviewer"
            )
            return True, reason, reviewer
        observation = _observation(event, str(entry["signalId"]))
        if (
            observation is not None
            and observation.get("missing") is True
            and observation.get("missingValuePolicy") == "force_escalation"
        ):
            reviewer = select_reviewer(
                candidates,
                competence_floor=competence_floor,
                fragment_id=fragment_id if isinstance(fragment_id, str) else None,
            )
            reason = f"missing_signal_force_escalation:{entry['signalId']}"
            reason += (
                f"+selected_reviewer={reviewer}" if reviewer else "+no_selectable_reviewer"
            )
            return True, reason, reviewer

    score = 0.0
    for entry in weights:
        value = _normalized(_observation(event, str(entry["signalId"])))
        if value is not None:
            score += float(entry["weight"]) * value
    if score >= threshold:
        reviewer = select_reviewer(
            candidates,
            competence_floor=competence_floor,
            fragment_id=fragment_id if isinstance(fragment_id, str) else None,
        )
        reason = f"combined_score={score:.4f}>=escalation_threshold={threshold:.4f}"
        reason += f"+selected_reviewer={reviewer}" if reviewer else "+no_selectable_reviewer"
        return True, reason, reviewer
    return False, f"combined_score={score:.4f}<escalation_threshold={threshold:.4f}", None


_TRIGGERS = {
    ARM_NEVER_ASK: _never_ask_trigger,
    ARM_ALWAYS_ASK: _always_ask_trigger,
    ARM_RANDOM_AT_BUDGET: _random_trigger,
    ARM_UNCERTAINTY_ONLY: _uncertainty_only_trigger,
    ARM_FIXED_THRESHOLD: _fixed_threshold_trigger,
    ARM_PROPOSED_JOINT_POLICY: _proposed_trigger,
}


def decide(
    arm: Arm, event: Mapping[str, Any], ledger: BudgetLedger
) -> tuple[Decision, BudgetLedger]:
    """Pure decision function: (event signals, budget ledger, arm params) -> decision.

    Budget resolution is shared by all six arms so they are compared at a
    matched budget: an evaluation-only ledger records the demanded outcome
    without charging; a demanded escalation with units remaining charges
    ``ESCALATION_UNIT_COST`` (``capped`` when it consumes the final unit,
    ``within_budget`` otherwise); a demanded escalation with no units remaining
    becomes a ``deferred`` decision, never a silent drop.
    """

    event_id = event.get("eventId")
    if not isinstance(event_id, str) or not event_id:
        raise PolicyValidationError("event must carry a non-empty string eventId")
    wants, reason, reviewer = _TRIGGERS[arm.arm_id](arm, event)

    if ledger.evaluation_only:
        decision = Decision(
            event_id, arm.arm_id, wants, reason, BUDGET_STATE_EVALUATION_ONLY, reviewer
        )
        return decision, ledger
    if wants:
        if ledger.remaining >= ESCALATION_UNIT_COST:
            charged = ledger.charge(ESCALATION_UNIT_COST)
            state = BUDGET_STATE_CAPPED if charged.remaining == 0 else BUDGET_STATE_WITHIN
            return Decision(event_id, arm.arm_id, True, reason, state, reviewer), charged
        deferred_reason = f"deferred_due_to_budget_exhaustion:{reason}"
        decision = Decision(
            event_id, arm.arm_id, False, deferred_reason, BUDGET_STATE_DEFERRED, None
        )
        return decision, ledger
    state = BUDGET_STATE_WITHIN if ledger.remaining > 0 else BUDGET_STATE_CAPPED
    return Decision(event_id, arm.arm_id, False, reason, state, None), ledger


def _as_ledger(budget: int | BudgetLedger) -> BudgetLedger:
    if isinstance(budget, BudgetLedger):
        return budget
    return BudgetLedger(amount=budget)


def _validate_events(events: Sequence[Mapping[str, Any]]) -> None:
    seen: set[str] = set()
    for event in events:
        if not isinstance(event, Mapping):
            raise PolicyValidationError("each event must be a mapping")
        event_id = event.get("eventId")
        if not isinstance(event_id, str) or not event_id:
            raise PolicyValidationError("each event must carry a non-empty string eventId")
        if event_id in seen:
            raise PolicyValidationError(f"duplicate eventId {event_id!r}")
        seen.add(event_id)
        observed: set[str] = set()
        for observation in event.get("signalObservations", ()):
            if not isinstance(observation, Mapping):
                raise PolicyValidationError(f"{event_id}: signal observations must be mappings")
            signal_id = observation.get("signalId")
            if signal_id not in SIGNAL_IDS:
                raise PolicyValidationError(f"{event_id}: unknown signalId {signal_id!r}")
            if signal_id in observed:
                raise PolicyValidationError(f"{event_id}: duplicate signalId {signal_id!r}")
            observed.add(signal_id)
        requests = event.get("explicitEscalationRequests", ())
        if not isinstance(requests, Sequence) or isinstance(requests, (str, bytes)):
            raise PolicyValidationError(
                f"{event_id}: explicit escalation requests must be a sequence"
            )
        requested_signals: set[str] = set()
        for request in requests:
            if not isinstance(request, Mapping) or set(request) != {
                "signalId",
                "trigger",
                "evidenceState",
            }:
                raise PolicyValidationError(
                    f"{event_id}: explicit escalation requests must use the bounded shape"
                )
            signal_id = request.get("signalId")
            if signal_id not in SIGNAL_IDS:
                raise PolicyValidationError(
                    f"{event_id}: explicit escalation request has unknown signalId"
                )
            if (
                request.get("trigger") != TRIGGER_AGENT_REQUESTED
                or request.get("evidenceState") != "observed"
            ):
                raise PolicyValidationError(
                    f"{event_id}: explicit escalation request has invalid semantics"
                )
            if signal_id in requested_signals:
                raise PolicyValidationError(
                    f"{event_id}: duplicate explicit escalation request signalId"
                )
            requested_signals.add(str(signal_id))


def replay(
    arm: Arm, events: Sequence[Mapping[str, Any]], budget: int | BudgetLedger
) -> ArmReplayLedger:
    """Replay one arm over a frozen event sequence at a unit budget.

    Returns per-event decisions in input order plus the escalated / deferred /
    declined event-id partition. The caller's ledger is never mutated (ledgers
    are immutable), so two replays over the same inputs are byte-identical.
    """

    _validate_events(events)
    ledger = _as_ledger(budget)
    decisions: list[Decision] = []
    escalated: list[str] = []
    deferred: list[str] = []
    declined: list[str] = []
    for event in events:
        decision, ledger = decide(arm, event, ledger)
        decisions.append(decision)
        if decision.escalate:
            escalated.append(decision.event_id)
        elif decision.budget_state == BUDGET_STATE_DEFERRED:
            deferred.append(decision.event_id)
        else:
            declined.append(decision.event_id)
    return ArmReplayLedger(
        arm_id=arm.arm_id,
        decisions=tuple(decisions),
        escalated_event_ids=tuple(escalated),
        deferred_event_ids=tuple(deferred),
        declined_event_ids=tuple(declined),
        budget=ledger,
    )


def default_arms(seed: int) -> tuple[Arm, ...]:
    """The six section 3.3 comparator arms at their default parameters."""

    return (
        Arm(ARM_NEVER_ASK),
        Arm(ARM_ALWAYS_ASK),
        Arm(ARM_RANDOM_AT_BUDGET, {"seed": seed}),
        Arm(ARM_UNCERTAINTY_ONLY),
        Arm(ARM_FIXED_THRESHOLD),
        Arm(ARM_PROPOSED_JOINT_POLICY),
    )


def replay_all(
    events: Sequence[Mapping[str, Any]], budget: int | BudgetLedger, seed: int
) -> dict[str, ArmReplayLedger]:
    """Run all six comparator arms over identical inputs at a matched budget.

    Every arm receives the same event sequence and an independent ledger built
    from the same ``budget`` value, so the arms are evaluable head-to-head.
    ``seed`` parameterizes only the random arm.
    """

    return {arm.arm_id: replay(arm, events, budget) for arm in default_arms(seed)}
