# Study 1 descriptive results template

**Required label:** `descriptive_candidate_escalation_only_no_outcome_evidence`

Complete only with sanitized aggregate values. Leave outcome fields blank until independently reviewed evidence exists.

## Receipt and availability

| Field | Value |
| --- | --- |
| Run identifier | |
| Frozen manifest receipt hash | |
| Manifest mutation check | pass / abort |
| Seed | `20260902` |
| Claim boundary | `descriptive_candidate_escalation_only_no_outcome_evidence` |
| Candidate count by stage | |
| Signal availability by stage and evidence state | |
| Source-manifest receipt status | |

## Arm and budget ledger

| Budget | Arm | Configured review-item units | Consumed | Remaining | Escalated | Deferred | Declined |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 5% | `never_ask` | | | | | | |
| 5% | `always_ask` | | | | | | |
| 5% | `random_at_budget` | | | | | | |
| 5% | `uncertainty_only` | | | | | | |
| 5% | `fixed_threshold` | | | | | | |
| 5% | `proposed_joint_policy` | | | | | | |
| 10% | all six arms | | | | | | |
| 20% | all six arms | | | | | | |

## Trigger attribution and overlap

| Budget | Arm | Trigger or decision reason | Count |
| ---: | --- | --- | ---: |
| | | | |

| Budget | Arm pair | Jaccard overlap of escalated event IDs |
| ---: | --- | ---: |
| | | |

## Readiness and notes status

| Gate | Status | Permitted interpretation |
| --- | --- | --- |
| StateDiagram inventory | `blocked_pending_data_processing_authorization` or current receipt status | Inventory only; no evaluation or C0 comparison. |
| Controlled notes | development-only receipt status | Development provenance only; no public outcome evidence. |
| Independent review | pending / complete | Required before any empirical benchmark. |
| Adjudication | pending / complete | Required before any outcome interpretation. |

## Forbidden-claim and human-review checklist

| Check | Confirmed |
| --- | --- |
| No accuracy claim | [ ] |
| No human-benefit or human-effort claim | [ ] |
| No generalization claim | [ ] |
| No policy-superiority claim | [ ] |
| No reviewer-authority claim | [ ] |
| No StateDiagram-versus-C0 comparison claim | [ ] |
| Independent reviewers have reviewed any empirical benchmark | [ ] |
| Adjudication has been completed for any empirical benchmark | [ ] |
| Output remains descriptive candidate escalation only | [ ] |
