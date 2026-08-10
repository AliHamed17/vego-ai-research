# Chapter 5 — The Human–AI Co-Reasoning Artifact (M1–M4B-1)

> Draft. Describes the implemented extension that turns VEGO-AI from an automated pipeline into a staged
> human–AI co-reasoning system. Sources: `VEGO-AI/framework/{selective_intervention_policy,human_review_queue,
> human_feedback_manager,human_judgment_memory,memory_advisor,memory_informed_classifier}.py`, the matching
> `VEGO-AI/schemas/*.json` and `VEGO-AI/docs/*.md`, and `docs/agent-memory/shared-state-report.md`.

## 5.1 Design principle

The contribution of this thesis is not "add a human-in-the-loop step" but **transform human judgment into structured, reusable knowledge** for AI-assisted domain-model assessment. This distinction is fundamental: many systems incorporate human review, but few treat the resulting judgment as a durable asset that accumulates value over time. The design is guided by three core principles.

First, **durability over transience**. Every human judgment should become persistent, retrievable knowledge rather than a one-time correction that is consumed and discarded. This means the system must not only capture what the expert decided but also *why* they decided it, *which case* prompted the decision, and *under what conditions* the decision should be reused.

Second, **additivity and non-destruction**. Every layer of the artifact consumes the baseline's existing evidence and produces new artifacts alongside it. No layer modifies, overwrites, or suppresses an AI classification. The original Agent 4 output is preserved verbatim throughout the entire chain, so that the artifact's effect can be measured against an uncontaminated baseline.

Third, **future-proofing**. The human-judgment asset should retain value even as the underlying LLM improves. A general model update might reduce some classification errors, but it cannot encode institution-specific norms, pedagogical intent, domain conventions, or historical precedent — the kinds of knowledge that human experts contribute. The judgment memory is designed to be valuable precisely because it encodes what no general model contains.

> **Figure 5.1.** End-to-end architecture of the human–AI co-reasoning artifact. Each layer adds a file-level artifact while preserving the baseline. See `thesis/figures/fig-5-1-co-reasoning-artifact.mmd` for the full Mermaid source.
>
> ```mermaid
> flowchart TB
>     A4["Agent 4 Output (baseline, read-only)"]
>     M1["M1: human_review_queue.jsonl (11 items)"]
>     HE(["Human Expert"])
>     M2["M2: resolved queue (4 feedback)"]
>     M3["M3: judgment_memory.jsonl (3 entries)"]
>     M4A["M4A: memory_advice.json (8 items)"]
>     M4B["M4B-1: comparison.json (27 rows, 0 differ)"]
>     A4 --> M1 --> HE --> M2 --> M3 --> M4A --> M4B
>     A4 --> M4A; A4 --> M4B
> ```

## 5.2 M1 — Human Review Queue

M1 operationalizes the baseline's latent review signals — the `requires_human_review`, `confidence`, and `flag_for_guidelines_update` fields that Agent 4 produces but no component acts upon (§4.4).

### Design rationale

The key design decision in M1 is *selectivity*: not every pattern needs human review, and reviewing everything would be neither scalable nor useful. The Selective Intervention Policy (`selective_intervention_policy.py`) implements a rule-based filter that identifies the patterns where human judgment is most likely to matter, based on the AI's own uncertainty signals. This positions the system as on-the-loop (§2.5): the AI operates autonomously for confident, unambiguous cases, and the human is engaged by exception.

### Intervention criteria

A pattern is routed to the human review queue if any of the following conditions hold: Agent 4 has set `requires_human_review = true`; the classification is `Undetermined`; the confidence is low or medium (below a configurable threshold); or Agent 4 has flagged the pattern for guideline update (`flag_for_guidelines_update = true`). These criteria are conjunctive with the AI's own signals — the policy does not override the AI's classification but identifies cases where the AI itself is uncertain or recommends review.

### Queue structure

`human_review_queue.py` joins each flagged classification with its deviation-pattern context and emits one `human_review_queue.jsonl` item per pattern. Each queue item contains the pattern description, the AI's classification and justification, the triggering criteria, the affected student models, and the related guideline — all the context a human reviewer needs to make an informed judgment.

**M1.2** adds a deterministic, order-independent `review_signature` computed over stable fields (setting, pattern ID, classification, and justification hash), plus a `source_pattern_id` that links back to the Agent 4 output. The signature serves two purposes: it allows later feedback (M2) to join safely even if the queue is regenerated from a different run order, and it provides a tamper-detection mechanism — if the AI's output changes between queue generation and feedback attachment, the signature mismatch is detected and recorded.

*Contribution to SQ1 (selective intervention):* VEGO-AI can now identify and persist where human judgment is requested, instead of leaving the signal unused. The current policy routes 11 of 27 patterns rather than routing every pattern. Whether this selection captures the cases that matter most or reduces reviewer effort without harmful misses remains an empirical question for EXP-021, EXP-022, and EXP-026.

## 5.3 M2 — Human Feedback Manager

M2 provides the mechanism for capturing expert decisions in a structured, machine-actionable format and attaching them to the specific review items they address.

### Design rationale

The design choice that distinguishes M2 from informal feedback (free-text comments, email exchanges, verbal discussions) is **schema validation**. Every feedback entry must conform to `human_feedback.schema.json`, which requires: a decision (`approve`, `reject`, `reclassify`, or `defer`), a rationale (required for all non-approve decisions), a reviewer identifier, and a timestamp. This ensures that feedback is comparable, auditable, and machine-processable — qualities that are necessary if the judgment is to be promoted to reusable memory (M3).

### Signature verification

Feedback joins by `review_id` and **verifies the `review_signature`** of the target review item. If the signature does not match — indicating that the AI's output has changed since the review item was generated — the mismatch is recorded as `signature_mismatch` and the feedback is not applied silently. This prevents a subtle but important failure mode: if Agent 4 is re-run with different parameters and produces a different classification for the same pattern, the expert's feedback (which was based on the original classification) should not be blindly attached to the new one.

### Non-destructive attachment

`human_feedback_manager.py` produces `human_review_queue_resolved.jsonl` — a new file that contains the original queue items enriched with the attached feedback. The original `human_review_queue.jsonl` is never overwritten. This preserves the audit trail: the original queue represents the AI's uncertainty, and the resolved queue represents the human's response to that uncertainty.

*Contribution to SQ2 (governed knowledge reuse):* Human feedback becomes structured, validated, and linked to the specific AI decision it addresses. Information flows bidirectionally: the AI's evidence and justification inform the human's review, and the human's structured decision feeds forward into the memory layer.

## 5.4 M3 — Human Judgment Memory

M3 is the central design contribution of the thesis: a provenance-tracked store of reusable human judgments that can be queried for future, similar cases.

### Design rationale

The distinction between M2 (feedback) and M3 (memory) is deliberate. Not all feedback should become reusable knowledge: a `defer` decision indicates that the expert needs more information, not that they have made a judgment; a one-time correction of a clear error may not generalize to other cases. M3 therefore requires explicit promotion: only feedback with `status == resolved`, `reusable == true`, a valid signature, and a human rationale is ingested into the memory store.

### Memory schema

Each memory item (`human_judgment.schema.json`) stores: a unique `memory_id`; a `memory_signature` for integrity verification; the source `review_id` and `feedback_id` (provenance chain); the human's `decision` and `rationale`; a `reuse_scope` indicating the intended generality (same-pattern, same-setting, cross-setting, or cross-domain); the `source_commit` at which the judgment was recorded; and a `conflict_status` field. The provenance chain is complete and auditable: from any memory item, one can trace back to the specific feedback entry, the specific review queue item, the specific Agent 4 classification, and the specific student models that triggered the review.

### Explainable, embedding-free retrieval

A key design choice is that retrieval uses **deterministic, explainable matching** rather than embedding-based similarity. When queried for a new Agent 4 pattern, the memory ranks stored judgments by overlap across three dimensions: domain match, diagram-type match, and guideline/keyword overlap. Each retrieved memory item carries human-readable `match_reasons` — for example, "same domain (Cheers), same diagram type (UCD), guideline overlap: 'Customer actor'" — so that the user of the advice can understand *why* a past judgment is considered relevant.

This design choice reflects a deliberate stance: the reuse mechanism should be as transparent and auditable as the original AI decision. Embedding-based retrieval would produce similarity scores without explaining what makes two patterns similar, creating an opaque layer in a system that is otherwise fully inspectable. The trade-off is that the matching is less flexible — it cannot capture deep semantic similarity between patterns described in very different terms — but for the current 27-pattern scale and the thesis's emphasis on transparency, deterministic matching is the appropriate choice.

### Conflict handling

When retrieval finds multiple relevant memory items that disagree (one expert approved a pattern, another rejected a similar one), the system surfaces the conflict rather than auto-resolving it. Each memory item carries a `conflict_status` that can be `none`, `detected`, or `resolved`, and conflicting items are presented together with their respective rationales. This preserves human authority over disagreements — the system does not silently choose between conflicting expert opinions but ensures that the consumer of the advice knows a disagreement exists.

*Contribution to SQ2 (governed knowledge reuse):* Expert judgment becomes durable, queryable, provenance-tracked knowledge. A judgment about "Customer as an actor" is not discarded after one case but stored with scope and provenance and surfaced when a similar pattern recurs — even in a different setting or domain.

## 5.5 M4A — Memory Advisory Layer

M4A retrieves relevant memory for each Agent 4 pattern and presents it as graded advisory evidence, without changing the AI's classification.

### Advisory retrieval

`memory_advisor.py` queries the judgment memory (M3) for each of the 27 Agent 4 patterns and emits `memory_advice.json`. Each advice item contains: the pattern being assessed, the retrieved memory items (with match reasons), a graded `advice_strength` (none, weak, moderate, strong, or conflicting), and the supporting evidence chain. The advice strength is computed from the number of relevant memories, the specificity of their match, and whether they agree or conflict.

### Hard boundary

The advisory layer's defining constraint is enforced in both code and schema: `advice_mode = "advisory_only"` (a `const` field in the schema, meaning it cannot be overridden at runtime) and `ai_classification_changed = false` (also schema-enforced). This is not merely a convention but an architectural guarantee: M4A can *inform* but cannot *change* the AI's output. The original Agent 4 classification is preserved verbatim alongside the advisory evidence.

This hard boundary is a design decision, not a temporary limitation. It reflects the principle that reusable human judgment should be surfaced as evidence for a human or a controlled experiment to act upon, not as an automatic override. The system presents "here is what past experts have said about similar cases" and leaves the decision about whether to act on that evidence to the consumer — whether that consumer is a human reviewer or the controlled comparison of M4B-1.

*Contribution to SQ2 (governed knowledge reuse):* Reusable human judgment is surfaced as advisory evidence while the original AI output is preserved verbatim. Information flows in both directions: the AI's classification provides the context for retrieval, and the human's past judgments provide advisory evidence for the current case.

## 5.6 M4B-1 — Deterministic Memory-Informed Comparison

M4B-1 is the final layer of the thesis artifact: a deterministic, non-destructive parallel comparison between the original Agent 4 classification and a memory-informed alternative.

### Design rationale

The purpose of M4B-1 is to produce a *measurable* comparison — not to change the system's behavior, but to create a controlled artifact that can be evaluated against expert labels. The comparison answers the question: "if the system had used the memory-informed classification instead of the original, would it have been more or less accurate?" But it answers this question as a parallel experiment, never as an actual change to the baseline.

### Policy table

`memory_informed_classifier.py` implements a transparent, deterministic policy table that maps each combination of `(advice_strength, agreement_with_original, conflict_status)` to an outcome. The policy is intentionally conservative:

| Advice strength | Agreement | Conflict | Outcome |
| --- | --- | --- | --- |
| none / weak | — | — | Keep original |
| moderate | agree | none | Keep original |
| moderate | disagree | none | Keep original; set `requires_human_review_after_memory` |
| strong | agree | none | Keep original |
| strong | disagree | none | Propose memory-supported alternative (in parallel artifact only) |
| any | — | conflicting | Keep original; set `requires_human_review_after_memory` |

Under the current deterministic policy (`memory-informed-classifier-v1`), most cases keep the original classification. Only a *strong disagreement* with no conflicts would propose a memory-supported alternative — and even then, the proposal appears only in the parallel comparison artifact, never in the baseline output. Moderate disagreements and conflicting advice are escalated for human review rather than resolved automatically.

### Output structure

Each comparison record (`memory_informed_comparison.schema.json`) carries: the original Agent 4 classification, the memory-informed classification (which may be identical), a boolean `memory_informed_differs_from_original`, a detailed `decision_trace` explaining which policy row was applied, the `policy_version` (`memory-informed-classifier-v1`), the `human_memory_used` (listing which memory items informed the decision), and an `evaluation_leakage_status` tag for the evaluation protocol.

Two fields are schema-enforced constants: `mode = "experimental"` and `ai_behavior_changed_in_baseline = false`. These cannot be overridden at runtime and serve as machine-readable guarantees that M4B-1 does not change the actual system behavior.

### Schema enforcement and non-destruction

The non-destructive guarantee is enforced at three levels. At the code level, M4B-1 reads from the baseline outputs and writes only to `memory_informed_comparison.json` — it never opens the baseline files for writing. At the schema level, the `ai_behavior_changed_in_baseline = false` constant makes any violation a schema error. At the guard level, `scripts/check_evidence_consistency.py` verifies on every prompt that the baseline outputs remain unmodified and that `ai_classification_changed` remains zero.

*Contribution to SQ3 (evaluation and transfer):* Reusable human judgment can drive a measurable, non-destructive comparison without changing the original result. The comparison artifact is the input to the empirical evaluation (Chapter 6), which will measure whether the memory-informed classifications are more accurate than the originals when compared against independent expert labels.

### Running example: "Customer as actor" through M4B-1

Continuing the running example from §4.4, the "Customer as actor" pattern (ucd_ch P6) now illustrates the complete chain:

1. **M1** queues P6 because of `medium_confidence` (trigger: `medium_confidence`). Review ID: `HRQ-ucd_ch-P6`.
2. **M2** captures the expert's disagreement: decision `valid_alternative`, rationale "Modeling 'Customer' as an actor who places orders is a legitimate alternative interpretation, not a modeling error; the AI's Occasional classification is too strict."
3. **M3** promotes the feedback to memory entry `HJM-ucd_ch-P6` with `reuse_scope = {domain: cheers, diagram_type: UCD, applies_to_future_models: true}` and limitation "Only when the customer is clearly the order initiator in the model."
4. **M4A** retrieves this memory with `advice_strength = moderate`, `match_reasons = [same domain, same diagram type, keyword match: Customer]`, and `ai_classification_changed = false`.
5. **M4B-1** applies policy row `moderate_disagreement_keep_original_require_review`: the original Occasional classification is kept, but `requires_human_review_after_memory = true` flags the case for further expert attention. The `decision_trace` records `advice_strength=moderate, original_classification=Occasional Variability, human_memory_classification=Substantial Variability`.

The comparison record also tags this row as `evaluation_leakage_status = same_pattern_memory_used` — the memory was derived from this exact pattern, so this row is excluded from generalization-safe metrics (§6.5). See Figure 5.2 for a visual trace.

> **Figure 5.2.** Running example: the "Customer as actor" pattern traced through the complete artifact chain from Agent 4 through M4B-1. See `thesis/figures/fig-5-2-running-example.mmd`.

## 5.7 The end-to-end artifact chain

The five layers compose into a concrete, file-level realization of reusable human judgment:

```
Agent 4 output (baseline, read-only)
    ↓
human_review_queue.jsonl          (M1: which patterns need review)
    ↓
human_review_queue_resolved.jsonl (M2: structured expert feedback attached)
    ↓
human_judgment_memory.jsonl       (M3: reusable, provenance-tracked judgments)
    ↓
memory_advice.json                (M4A: advisory evidence per pattern)
    ↓
memory_informed_comparison.json   (M4B-1: parallel comparison artifact)
```

Each file in the chain is a complete, self-contained artifact that can be inspected independently. The chain is traceable: from any field in the comparison artifact, one can follow the provenance chain back through advice, memory, feedback, review queue, and original Agent 4 output. This traceability is not incidental but a design requirement — it supports both the evaluation methodology (Chapter 6) and the auditability that the design principles (§9.4) emphasize.

Two inspection surfaces support analysis of the artifact chain: an offline **results dashboard** (`analysis/build_results_dashboard.py`) that generates summary statistics and pattern-level breakdowns across all layers, and a **Tkinter visualizer** with model/result mismatch detection, read-only research panels for each milestone's output, and search/filter capabilities. Both inspection surfaces are read-only with respect to the baseline and human artifacts — they consume and display but never modify.

## 5.8 Implementation summary

The entire co-reasoning artifact is implemented in pure Python with no LLM or
API dependencies. The implementation comprises six framework modules (selective
intervention policy, human review queue, human feedback manager, human judgment
memory, memory advisor, and memory-informed classifier), six runtime schema
files, and comprehensive documentation. The accepted verification record
reports the VEGO-AI suite passing for schema compliance, signature integrity,
deterministic match behavior, policy-table behavior, and non-destruction; exact
counts remain attached to that dated record. Independent human relevance of retrieved advice is a later
EXP-022 question, not established by the unit tests.

The decision to avoid LLM calls and embeddings in the extension is deliberate. It ensures that the artifact is fully deterministic and reproducible: given the same baseline outputs and the same human feedback, the same comparison artifact is produced every time, regardless of API availability, LLM version, or network conditions. This reproducibility is essential for the evaluation methodology (Chapter 6), which requires that differences between conditions can be attributed to the human-judgment layer rather than to LLM stochasticity.

## 5.9 Component-to-evidence traceability

Each component has an invariant, a foreseeable failure mode, and a corresponding
evaluation:

| Component | Invariant | Main failure mode | Evidence or planned test |
| --- | --- | --- | --- |
| M1 Review queue | Every item traces to one baseline pattern and trigger | Important baseline error not queued; unnecessary queue item | Current schema/count evidence; EXP-021/022 precision and recall |
| M2 Feedback manager | Signature and required rationale fields validate | Feedback attaches to the wrong or stale item | Signature tests; reviewer protocol |
| M3 Judgment memory | Only explicitly reusable, provenance-complete records enter memory | Over-broad scope or unresolved conflict | Current provenance checks; EXP-022 scope/conflict audit |
| M4A Advisory layer | Advice cannot change the AI classification | Irrelevant or same-pattern advice appears persuasive | `ai_classification_changed=false`; EXP-022 blind relevance/leakage audit |
| M4B-1 Comparison | Baseline remains visible and unchanged | Candidate harm is hidden by aggregate accuracy | Current 0/27 change record; EXP-024/025 paired matrix and net correction |
| Evaluation gate | Missing evidence remains null, not zero or inferred | Synthetic, blank, or leaked labels enter a claim | EXP-005/012 gates; `GoldLabelRecord-v2`; `EvaluationRunManifest-v2` |

This traceability links architecture to evaluation without assuming that an
implemented mechanism has an empirically beneficial effect.

## 5.10 Unified contracts and fail-closed parity

Iteration 15 preserves the implementation described above as the `legacy`
runtime mode and adds a parallel `unified` mode under `src/vego_hlayer`. The
unified package defines versioned records for observation, triage, review,
feedback, verification, memory, advice, correction proposals, comparisons, and
run manifests. Deterministic adapters translate between these records and the
existing M1–M4B-1 file formats, so public filenames, review identifiers,
signatures, status fields, and evaluation interfaces remain compatible.

Three explicit modes prevent an implicit migration:

| Mode | Purpose | Publication rule |
| --- | --- | --- |
| `legacy` | Execute the existing implementation | Default and reference path |
| `unified` | Execute the canonical contract-driven path | Explicit selection only |
| `parity` | Execute both paths from the same immutable input in isolated temporary directories | Publish legacy only if every normalized field matches; otherwise publish legacy and record the difference |

Parity normalization is limited to run identifiers and timestamps. It compares
review IDs, signatures, statuses, memory matches, advice, classifications,
escalation flags, safety fields, and row counts. The controlled Iteration 15
check covered 14 artifacts, 11 review items, three historical mechanism-memory
records, and 27 comparison rows, with zero classification changes. This is
compatibility evidence, not evidence that either path is more accurate.

The canonical trust state also prevents historical reinterpretation. Existing
M3 records are `legacy_mechanism_memory`; they are not retroactively described
as S5-verified. Only independently verified or human-adjudicated records may
enter trusted memory with `verified` or `adjudicated` status. Timeout, missing
evidence, conflict, rejection, or an invalid output path preserves the baseline
and produces no trusted-memory write.

## 5.11 Boundaries

Across all layers: no Agent 1–4 prompt or logic change; no LLM or API calls in the extension; no embeddings; no visualizer write-back; baseline `eval_output/` is read-only. **M4B-2** (optional LLM/Agent 4 `resolve_with_answers` reclassification) is designed-only and **blocked** — it would require LLM calls, introduce stochasticity, and change Agent 4's behavior, all of which are explicitly excluded from this thesis.

These boundaries are what make the artifact a clean design-science object: it is fully attributable (every output traces to human input or deterministic computation), reproducible (no stochastic dependencies), and safe to evaluate against the preserved baseline (Chapter 6). They are not limitations of ambition but deliberate methodological choices that protect the validity of the evaluation.
