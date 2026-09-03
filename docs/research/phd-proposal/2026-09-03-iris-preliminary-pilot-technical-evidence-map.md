# Iris preliminary pilot — technical evidence map

**Audit date:** 2026-09-03

**Scope:** repository evidence, integrity, deterministic replay feasibility, and claim boundaries only

**Status:** ready for human review; not supervisor-approved and not an outcome evaluation

Run the fail-closed local audit from repository root:

```powershell
uv run python scripts/verify_iris_preliminary_pilot.py --repo-root . --vego-root VEGO-AI
```

The verifier is read-only. It writes no artifact, calls no model or API, does not
open the sealed EXP-003 mapping as structured data, and returns non-zero if a
protected count, baseline artifact, milestone artifact, or label gate changes.

## 1. Repository and evidence-state verification

- `main` is the required audit branch; the verifier records the live `HEAD`.
- `official-vego-ai-baseline` resolves to
  `2eeccb1cbb2d01faa3e8ceb43466a52e0fee23cf`.
- All 250 tagged `analysis/` and `eval_output/` artifacts have a corresponding
  local `VEGO-AI/` artifact and are content-equivalent. Only 9 are byte-identical
  because Windows checkout line endings alter JSON bytes; structural JSON and
  normalized XLSX-member comparison found no semantic drift.
- M1, M1.2, M2, M3, M4A, and M4B-1 implementation and test paths exist. The
  frozen extension run contains 11 queue rows, 11 signed review identities, 4
  resolved feedback rows, 3 memory rows, 27 advice rows, and 27 comparison rows.
- M4A changed 0 classifications and found 0 memory conflicts. M4B-1 changed 0
  of 27 classifications and flagged 2 rows for review after memory.
- `experiments/registry.md` contains 47 unique, contiguous entries from EXP-000
  through EXP-046. The current-run index contains 26 entries and the accepted-run
  directory contains 111 manifests. Registration or a manifest is not evidence
  that an experiment is complete; each registry row's status remains controlling.

## 2. Machine-verifiable evidence map

Hashes below are canonical tree receipts over sorted relative path plus normalized
content. Private/ignored files contribute hashes only; their contents are not
copied into this tracked document.

| Source | Source path | Type | Evidence layer | Files | Verified | Canonical tree SHA-256 | Notes |
| --- | --- | --- | --- | ---: | --- | --- | --- |
| Agent 1 outputs | `VEGO-AI/eval_output/*/agentA_*` | artifact set | original baseline | 28 | yes | `cfc81cd9401f0a67f2e1a8c3cf764a817a3de545df38508c4470d09152003b95` | Template/language-advisor outputs and evaluations. |
| Agent 2 outputs | `VEGO-AI/eval_output/*/agentB_*` | artifact set | original baseline | 28 | yes | `509a731a85d090175ca7feb9aac5514538c35435ffc731f4d34e5ddf8c479f20` | Domain-guideline outputs and evaluator comparisons. |
| Agent 3 outputs | `VEGO-AI/eval_output/*/agentC_*` | artifact set | original baseline | 169 | yes | `1810d517da7400cf108630bce0dd3d377752023f353cf8e19c46c439ca3c13a4` | Four rankings plus 165 per-case reports. |
| Agent 4 outputs | `VEGO-AI/eval_output/*/agentD_*` | artifact set | original baseline | 8 | yes | `17983388de114a8a50889c734a1d081c73a3c6dc8f5f2f1bf3289d44b5a68118` | Deviation-pattern and variability-class files. |
| Human-review queue | `VEGO-AI/runs/20260614-122150/human/*/human_review_queue.jsonl` | JSONL set | extension M1/M1.2 | 4 | yes | `e07bbae5a048354cb0ac36119f5aab93f4bc71343ef69040958886d8d4463ea4` | 11 queue rows; all have stable ID and signature. |
| Structured feedback | `VEGO-AI/runs/20260614-122150/human/*/human_review_queue_resolved.jsonl` | JSONL set | extension M2 | 1 | yes | `aeffa728ef3e7987d77e39e251831cfe32934f7088d102aac32ee8d681d09870` | 4 resolved feedback rows; not independent held-out labels. |
| Human Judgment Memory | `VEGO-AI/runs/20260614-122150/human/*/human_judgment_memory.jsonl` | JSONL set | extension M3 | 1 | yes | `a2a09ed94586eb69b9205bd3d6f8c91b8a27154648b2791bef32076849a8af1e` | 3 reusable memory rows; development/mechanism evidence. |
| Memory advice | `VEGO-AI/runs/20260614-122150/human/*/memory_advice.json` | JSON set | extension M4A | 4 | yes | `fefffd30c59a72c805c4142e303a2ad9b2d57f277af65bfaacf355e216575b45` | 27 advisory rows; 0 AI classification changes. |
| Memory-informed comparison | `VEGO-AI/runs/20260614-122150/human/*/memory_informed_comparison.json` | JSON set | extension M4B-1 | 4 | yes | `96cb84dcfb20cf2ba0a1de8d35bcea5aa15e8521fe5500e598249e759e81a7cb` | 27 deterministic sidecar comparisons; 0 classification differences. |
| Expert annotation package | `reports/generated/exp003/annotation_package/*` | controlled package | ignored/private evaluation boundary | 11 | yes | `2ad667084280c2f9a26379c94298996c2c60b35fe8c17e90d2eece71470ea8ce` | Hash receipt only; reviewer sheets remain unlabeled. |
| EXP-005 gate | `reports/generated/exp005_label_review/*` | controlled package | ignored/private evaluation boundary | 14 | yes | `9f00581bdb20d36c92dd22eac3f5965903884ac4ca4a02bd6afd539fe68a2e79` | 27 rows, 24 safe candidates, 0 valid safe labels. |

## 3. Denominator reconciliation

| Setting | Ranked rows | Unique setting-case rows / reports | Duplicate ranking rows | Patterns |
| --- | ---: | ---: | ---: | ---: |
| `ucd_ch` | 46 | 45 | 1 | 8 |
| `ucd_pw` | 44 | 37 | 7 | 8 |
| `cd_ch` | 48 | 46 | 2 | 4 |
| `cd_pw` | 41 | 37 | 4 | 7 |
| **Total** | **179** | **165** | **14** | **27** |

The four ranking files contain 179 rows. Fourteen rows repeat a case ID within
the same setting, so the frozen output has 165 unique setting-case reports. Across
the four settings there are 83 distinct case IDs because one submission can appear
in multiple diagram settings. These are three different denominators and must not
be substituted for one another.

The reviewed paper snapshot in
`docs/research/bigui/paper-baseline-snapshot-v1.json` reports 178 case models and
26 patterns. That is a separate paper-reported scope. The current frozen repository
reports 179/27. The one-row/one-pattern difference is contextual, not an accuracy
or quality improvement.

## 4. Agent 4 ground-truth audit

Direct SHA-256 comparison found every `VEGO-AI/analysis/agentD_variability_classes_*`
file byte-identical to its `VEGO-AI/eval_output/<setting>/` Agent 4 source:

| Setting | Patterns | Shared SHA-256 |
| --- | ---: | --- |
| `ucd_ch` | 8 | `e42e5199d393c706863f531737d06ff8484790a1f5c2308e9acea027e07f4809` |
| `ucd_pw` | 8 | `35a97ca7d5486343f0b7c3894fd925b6dc58980334e217d95eacbd46594f8e6e` |
| `cd_ch` | 4 | `b056e22d196a0fe8dabe275f3d8a2fcb8acc0eae4bf64a080076fef8ac65629f` |
| `cd_pw` | 7 | `20b36f740e3152866257e721c9f2901a2fb39b167834ff5a5980d8f2a02c5cd2` |

Therefore `analysis/` is a copy/integrity view of Agent 4, not an independent
reference, expert label set, or accuracy benchmark.

## 5. EXP-005 gate audit

| Check | Verified value |
| --- | ---: |
| Full rows | 27 |
| Generalization-safe candidates | 24 |
| Labels supplied / valid labels | 0 / 0 |
| Generalization-safe valid labels | 0 |
| Same-pattern valid labels | 0 |
| Reviewer 1 labels | 0 |
| Reviewer 2 labels | 0 |
| Adjudicated labels | 0 |
| Gold-label rows | 0 |
| Holdout | sealed; not evaluated |

The verifier hashes but does not parse the private mapping. Its current SHA-256
is `d88b43789aa35d1728dab6a0fb5c7108b7877716cfc4f6e82cce5570c5f35a88`.
The strict gate remains closed: no quantitative accuracy, improvement, policy
superiority, or generalization evaluation is allowed at 0/24.

## 6. Trigger inventory

`IMPLEMENTED` means the field/label exists in the current artifact pipeline.
`DERIVABLE` means a deterministic comparison over existing artifacts produces it.
`MANUAL` would require a human mark. `PROPOSED ONLY` means the governed doctoral
contract names the signal but the frozen baseline does not observe it.

| Trigger | State | Layer / source | Current evidence count | Safe pilot use |
| --- | --- | --- | ---: | --- |
| Missing guideline | DERIVABLE | Agent 2 evaluator vs course reference | 59 | Candidate coverage review; reference-derived, not proof of error. |
| `Alternative` | IMPLEMENTED | Agent 3 uncovered-fragment label | 491 | Candidate ambiguity review; AI label only. |
| `Domain Mistake` | IMPLEMENTED | Agent 3 uncovered-fragment label | 79 | Candidate severity review; AI label only. |
| `Language Mistake` | IMPLEMENTED | Agent 3 uncovered-fragment label | 37 | Candidate syntax/language review; AI label only. |
| `Not-Satisfied` | IMPLEMENTED | Agent 3 compliance status | 496 | Candidate compliance review; no independent verdict. |
| `Partially-Satisfied` | IMPLEMENTED | Agent 3 compliance status | 743 | Candidate ambiguity review; no independent verdict. |
| Open question | IMPLEMENTED | Agent 2 `questions_to_language_advisor` | 12 | Candidate expert clarification point. |
| Low/medium confidence | IMPLEMENTED | Agent 4 confidence | 3 (all Medium; 0 Low) | Existing queue-compatible review signal. |
| Cross-agent disagreement | PROPOSED ONLY | doctoral signal contract | unavailable | Do not claim it is observed or automated. |
| Novelty | PROPOSED ONLY | doctoral signal contract | unavailable | `Alternative` is not automatically equivalent to novelty. |
| Memory disagreement/conflict | IMPLEMENTED | M4A/M4B-1 extension | 0 | Mechanism exists; this run provides no conflict case. |

## 7. Real pilot candidates

| Candidate | Evidence status | Exact source | What is established | Boundary |
| --- | --- | --- | --- | --- |
| C1 — domain-guideline coverage | FOUND | `VEGO-AI/eval_output/ucd_ch/agentB_guideline_mapping.json`, cluster `C1` | No base assignment; minimum mapping certainty 0.7. | Candidate escalation only; no independent outcome. |
| C2 — compliance disagreement | **NOT FOUND** at row level | `experiments/EXP-046-recorded-review-analysis/README.md` | Tracked evidence is aggregate; source workbooks with row identifiers remain outside Git. | Do not invent a case or call an aggregate an exact pilot item. |
| C3 — uncovered fragment | FOUND locally | Exact private per-case path and item index are emitted by the verifier. | A real frozen Agent 3 item labeled `Alternative`. | Student/case locator is intentionally not copied into public Git; no independent outcome. |
| C4 — Agent 4 uncertainty/update flag | FOUND | `VEGO-AI/human_review_output/cd_ch/human_review_queue.jsonl`, `HRQ-cd_ch-P2` | Medium confidence plus guideline-update trigger; 7 affected cases. | The original `requires_human_review` value is false; the extension queue supplies the review point. |

## 8. Deterministic replay feasibility

| Pilot | Replay without LLM/API | Current state | Technical conclusion |
| --- | --- | --- | --- |
| C1 missing-guideline addition | no | BLOCKED | A new guideline requires semantic mapping/scoring; no approved deterministic injection path exists. |
| C2 compliance correction | partial | DERIVABLE | Stored contribution arithmetic can be recalculated, but the exact human row and bounded correction adapter are absent. |
| C3 fragment relabel | partial | DERIVABLE | Contribution arithmetic can be recalculated, but no approved human-relabel replay adapter exists. |
| C4 pattern correction | yes | IMPLEMENTED | M1–M4B-1 supports feedback, memory, and non-destructive comparison. This tests mechanism behavior, not benefit. |

No replay may modify Agent 4 or the frozen baseline, call an LLM/API, create a
human label, open the holdout, or be reported as an accuracy/effectiveness result.

## 9. Claim-safe conclusion

The repository is sufficient to demonstrate where deterministic escalation
signals exist, how much review work each signal would nominate, and whether the
existing H-layer can capture and reuse a bounded human decision. It is not
sufficient to decide which trigger is correct or superior. That requires approved
human labeling, independent review/adjudication, and the still-closed EXP-005 gate.
