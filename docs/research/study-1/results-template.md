# Study 1 descriptive results template

**Required label:** `descriptive_candidate_escalation_only_no_outcome_evidence`

Complete only with sanitized aggregate values. Leave outcome fields blank until independently reviewed evidence exists.

## Sanitized summary field parity

Every top-level key below is emitted by the sanitized summary. Nested rows name the exact emitted field that supplies the value.

| Safe summary top-level key | Value |
| --- | --- |
| `claim_boundary` | `descriptive_candidate_escalation_only_no_outcome_evidence` |
| `seed` | `20260902` |
| `frozen_manifest` | Safe hash and mutation-check status; see exact nested fields below. |
| `candidate_count_by_stage` | |
| `candidate_signal_availability_by_stage` | |
| `rates` | The three matched-budget summaries used in the ledger sections below. |
| `selection_stability_by_arm` | Pairwise Jaccard values across 5%, 10%, and 20%. |
| `report_hashes` | SHA-256 hashes of the exact serialized artifact file bytes, including the terminal newline; see nested fields below. |

| Exact nested summary field | Value |
| --- | --- |
| `frozen_manifest.manifest_hash` | |
| `frozen_manifest.mutation_check` | `passed` or run aborts before summary emission |
| `report_hashes.frozen_manifest` | |
| `report_hashes.candidate_events` | |
| `report_hashes.replay_ledgers` | |

## Arm and budget ledger

| Budget | Arm | Configured review-item units | Consumed | Remaining | Escalated | Deferred | Declined |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 5% | `never_ask` | | | | | | |
| 5% | `always_ask` | | | | | | |
| 5% | `random_at_budget` | | | | | | |
| 5% | `uncertainty_only` | | | | | | |
| 5% | `fixed_threshold` | | | | | | |
| 5% | `proposed_joint_policy` | | | | | | |
| 10% | `never_ask` | | | | | | |
| 10% | `always_ask` | | | | | | |
| 10% | `random_at_budget` | | | | | | |
| 10% | `uncertainty_only` | | | | | | |
| 10% | `fixed_threshold` | | | | | | |
| 10% | `proposed_joint_policy` | | | | | | |
| 20% | `never_ask` | | | | | | |
| 20% | `always_ask` | | | | | | |
| 20% | `random_at_budget` | | | | | | |
| 20% | `uncertainty_only` | | | | | | |
| 20% | `fixed_threshold` | | | | | | |
| 20% | `proposed_joint_policy` | | | | | | |

## Trigger attribution and overlap

| Budget | Arm | Trigger or decision reason | Count |
| ---: | --- | --- | ---: |
| | | | |

| Budget | Arm pair | Jaccard overlap of escalated event IDs |
| ---: | --- | ---: |
| | | |

## Candidate coverage distribution

These are descriptive review-item selection fractions, not correctness, performance, benefit, or human-effort measurements.

| Budget | Arm | Stage | Candidate count | Escalated count | Escalation fraction |
| ---: | --- | --- | ---: | ---: | ---: |
| | | | | | |

## Selection stability across budgets

| Arm | Budget pair | Jaccard overlap of escalated event IDs |
| --- | --- | ---: |
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
