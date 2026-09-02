# Baseline Characterization (C0) and Artifact Operating Profile

> **Descriptive only — no accuracy or effect claim.** This document profiles the frozen VEGO-AI Agent 4
> baseline (C0) and the operating counts of the M1–M4B-1 artifact. It states *what exists and at what scale*,
> not whether anything improved. Every figure is sourced from the frozen baseline, `experiments/registry.md`,
> and the generated reports under `reports/generated/` (EXP-001 summary, evaluation comparison). Implements
> Step 1 of `results-deepdive-and-phd-roadmap.md` (P1 baseline characterization).
>
> Baseline tag: `official-vego-ai-baseline` (`2eeccb1`) · Policy: `memory-informed-classifier-v1` ·
> Run: `VEGO-AI/runs/20260614-122150/human` · Guard: 18/18 evidence invariants PASS · Tests: 94 passing.

---

## 1. Scope of the baseline (C0)

| Dimension | Value |
| --- | --- |
| Student model cases | 179 |
| Recurring variability patterns | 27 |
| Domains | 2 (Cheers, ParkWise) |
| Diagram types | 2 (use-case, class) |
| Settings | 4 (`ucd_ch`, `ucd_pw`, `cd_ch`, `cd_pw`) |
| Agent 4 classes used | Substantial (9), Occasional (18), Undetermined (0) |

### 1.1 Patterns per setting (from EXP-001 `setting` distribution)

| Setting | Domain · diagram | Patterns |
| --- | --- | ---: |
| `cd_ch` | Cheers · class | 4 |
| `cd_pw` | ParkWise · class | 7 |
| `ucd_ch` | Cheers · use-case | 8 |
| `ucd_pw` | ParkWise · use-case | 8 |
| **Total** | | **27** |

### 1.2 Critical provenance note — the baseline is *not* a benchmark

The author-reviewed files `VEGO-AI/analysis/agentD_variability_classes_*.json` are **byte-identical** to the
Agent 4 output for all 27 patterns (0 field differences; `evaluation_summary.json → benchmark_status`).
They record *agreement*, not independent ground truth, and are **never** used as evaluation labels. The only
admissible ground truth is independently collected expert labels (not yet supplied).

---

## 2. Artifact operating profile (M1–M4B-1) — descriptive counts

| Layer | Count | Detail |
| --- | ---: | --- |
| M1 review queue | 11 / 27 | Targeting rate 40.7%. Trigger reasons recorded in the four `human_review_queue.jsonl` files: `guideline_update_proposed` on 9 items and `medium_confidence` on 3 items (one `cd_ch` item carries both); `agent_requested_human_review` and `low_confidence` fired 0 times (corrected 2026-09-02 against the queue files; the earlier wording listed `requires_human_review` as most common). |
| M2 feedback | 4 | 100% schema-valid, 0 signature mismatches; `approve` + `reclassify` decisions, complete rationales. |
| M3 memory | 3 | 3 of 4 feedback entries promoted to reusable memory; full provenance chains; `ucd_ch` setting. |
| M4A advice | 8 advised | Advice-strength distribution below. `ai_classification_changed = false` on all. |
| M4B-1 comparison | 27 rows | 0 differ from original; 2 `requires_human_review_after_memory`; 0 conflicting. |

### 2.1 M4A advice-strength distribution (27 rows)

| Strength | Count |
| --- | ---: |
| none | 19 |
| weak | 4 |
| moderate | 2 |
| strong | 2 |

"Advised" patterns = weak + moderate + strong = **8**.

### 2.2 M4B-1 policy outcome distribution (v1, 27 rows)

| Rule applied | Count | Outcome |
| --- | ---: | --- |
| `no_memory_keep_original` | 19 | keep original |
| `weak_keep_original` | 4 | keep original |
| `strong_agreement_keep_original` | 2 | keep original |
| `moderate_disagreement_keep_original_require_review` | 2 | keep original **+ escalate** |
| **Changed classifications** | **0** | — |

The only "live" policy actions are the **2 escalations** (`requires_human_review_after_memory`). No row is
relabeled — this is a property of the conservative v1 policy as much as of the data (it relabels only on
strong, conflict-free, leakage-safe disagreement, which did not occur).

### 2.3 Leakage status distribution (27 rows)

| `evaluation_leakage_status` | Count | Use for accuracy metrics |
| --- | ---: | --- |
| `none` | 19 | generalization-safe candidate |
| `cross_setting_memory_used` | 5 | generalization-safe candidate |
| `same_pattern_memory_used` | 3 | **excluded** — mechanism only |

**Generalization-safe candidates = 24** (19 `none` + 5 `cross_setting`). The 5 `cross_setting` rows are
notable: reusable memory from a *different* setting was already applied to them, so once labeled they are
directly relevant to the generalization question. The 3 `same_pattern` rows are mechanism evidence only.

---

## 3. Label accounting (the binding constraint)

| Item | Value |
| --- | ---: |
| Expert-labeled rows (from memory provenance) | 3 |
| — all same-pattern leakage? | yes |
| Generalization-safe **independent** labels supplied | **0** |
| Generalization-safe candidates awaiting labels | 24 |

The 3 memory-provenance "labels" support **mechanism validation only** (EXP-001). They are same-pattern and
are excluded from every generalization-safe metric; **no agreement or accuracy rate derived from them may be
read as evidence of effect.**

---

## 4. What this characterization does and does not say

**Does say (supported):** the baseline operates at a defined, modest scale (179 cases, 27 patterns, 4
settings); the artifact exercises the full chain at that scale; the policy is conservative (0 changed, 2
escalations); 24 rows are generalization-safe candidates and 0 are labeled; the baseline is preserved and
reproducible.

**Does not say (not evaluable):** that any classification is correct or incorrect; that the artifact improves
or would improve accuracy; that memory generalizes. Those require independent expert labels and are gated
(0 → not evaluable; 1–19 → pilot only; ≥20 → quantitative).
