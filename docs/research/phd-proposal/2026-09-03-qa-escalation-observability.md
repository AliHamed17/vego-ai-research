# Q&A Escalation Detection Study — Technical Evidence Package

**Active milestone:** Q&A ESCALATION DETECTION STUDY<br>
**Status:** technical scaffold ready for supervisor review; human validation has not been run.

## Scope and boundary

The immediate study asks: **which observable communication conditions should raise a
candidate human-intervention alert?** It does not test whether intervention improves
an Agent-C score, whether a final verdict is correct, reviewer effort, or policy
superiority. The prior Agent-C score reconstruction and C2 bridge remain valid
later-stage technical evidence, but are not the current critical path. The C2
usable-row disagreement (Claude: 114; Codex: 111) is explicitly deferred and is
not used as Q&A ground truth.

## Verified communication matrix

| Source stage | Target | Question field | Answer field | Confidence | Evidence | Persisted history | Frozen observation |
|---|---|---|---|---|---|---|---:|
| Agent 2 phase 2/3/4 routing | Agent 1 | `questions_to_language_advisor` | `questions_answers` | `answer.confidence` | `answer.evidence` | `state.lang_qa_history` | 12 |
| Agent 2 phase 2/3/4 routing | Agent 2 | `questions_to_domain_advisor` | `questions_answers` | `answer.confidence` | `answer.evidence` | `state.dom_qa_history` | 0 |
| Agent 3 skills 3-2/3-3 | Agent 1 | `questions_to_language_advisor` | `questions_answers` | `answer.confidence` | `answer.evidence` | `state.lang_qa_history` | 0; supported by code, not observed |
| Agent 3 skills 3-2/3-3 | Agent 2 | `questions_to_domain_advisor` | `questions_answers` | `answer.confidence` | `answer.evidence` | `state.dom_qa_history` | 0; supported by code, not observed |
| Agent 4 skill 4-2 | Agent 1 | `questions_to_language_advisor` | `questions_answers` | `answer.confidence` | `answer.evidence` | `state.lang_qa_history` | 0; supported by code, not observed |
| Agent 4 skill 4-2 | Agent 2 | `questions_to_domain_advisor` | `questions_answers` | `answer.confidence` | `answer.evidence` | `state.dom_qa_history` | 0; supported by code, not observed |

The 12 observed rows are final Agent-2 guideline questions: 2 `ucd_ch`, 1
`ucd_pw`, 3 `cd_ch`, and 6 `cd_pw`. Frozen state histories contain zero answers.
The three run snapshots contain 30 question records, with no repeated normalized
question text; they are retained as a separate snapshot count and are not silently
merged with the 12 final rows.

## Confidence inventory

| Concept | Producer / field | Semantics | Frozen observation | Escalation use |
|---|---|---|---:|---|
| Q&A answer confidence | Agent 1/2 answer `confidence` | `High`, `Medium`, or `Low` confidence in an answer | 0 answers; unavailable | Primary planned feature; not observed yet |
| Agent-2 mapping certainty | Agent-2 `mapping_certainty` | Numeric 0–1 certainty of guideline/template mapping | 48 values ≤ 0.75 | Separate deterministic feature; not Q&A answer confidence |
| Agent-4 classification confidence | Agent-4 `confidence` | Confidence in variability classification | 24 High, 3 Medium, 0 Low | Context feature only; not answer confidence |
| Question-generation uncertainty | No persisted field | Would describe why a question was generated | Not available | Cannot be used without instrumentation |

## Frozen counts and features

The canonical final snapshot contains 12 persisted question records and no
persisted matching answer records. This is reported as `ANSWER_NOT_PERSISTED`,
not as a behavioral claim that the agent failed to answer. There are 12 language
questions, 0 domain questions, and no persisted answer records without
evidence, and 0 repeated normalized questions. Multiple-round episodes, cases with
multiple questions, MAX_QA_ROUNDS episodes, and unresolved episode counts are not
computable from the frozen evidence. The deterministic feature inventory is:

| Feature | Rule | Count | Availability |
|---|---|---:|---|
| F1 | answer confidence = Low | 0 | Not observed |
| F2 | answer confidence ∈ {Low, Medium} | 0 | Not observed |
| F3 | answered and answer evidence missing | 0 | Not observed |
| F4 | explicit lower-priority source | 0 | Field unavailable |
| F5 | answer not persisted | 12 | Data-availability status only; not a human-escalation signal |
| F6 | multiple rounds | 0 | Not reconstructable |
| F7 | repeated normalized question | 0 | Observed |
| F8 | follow-up clarification | 0 | Not reconstructable |
| F9 | unusually high case/claim count | 0 | Scope unavailable |
| F10 | MAX_QA_ROUNDS or unresolved | 0 | Not reconstructable |
| F11 | Agent-2 mapping certainty ≤ 0.75 | 48 | Observed separately |

## Detector and validation scaffold

`extract_qa_escalation_features.py` emits source-hashed events and applies a
transparent OR-rule. F5 is retained only as a visible data-availability status and
does not produce an escalation alert. The
alerts are candidate alerts only; no correctness is inferred. The detector stores
reason codes, confidence, evidence presence, and provenance for auditability.

The generator creates three independent blind sheets (Reviewer A/B/C) with context
and blank fields for `review_label`, `short_rationale`, `reviewer_id`,
`review_date`, and optional reviewer confidence. Detector decisions and trigger
reasons are hidden. A separate private audit mapping links blind rows to alerts.

The evaluation scaffold supports confirmed, false, and unclear alert counts and
yield/rate calculations after labels exist. It fails closed when only alerted rows
are labeled, so recall/coverage cannot be reported from alert-only review.

## Reproduction

```powershell
python scripts/extract_qa_escalation_features.py `
  --vego-root VEGO-AI `
  --output reports/generated/qa_escalation_observability.json `
  --review-output reports/generated/qa_escalation_review
```

All generated JSON/CSV review material is ignored/private. The extractor is
read-only, offline, deterministic, and does not modify baseline artifacts.
