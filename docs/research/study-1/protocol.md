# Study 1 protocol: candidate human escalation

## Purpose and question

Study 1 asks: **when does VEGO-AI propose human escalation?** It is a deterministic, descriptive candidate-escalation exercise, not an outcome evaluation. A proposal remains subject to human review; it is not an automatic correction, a reviewer assignment, or an authoritative decision.

The unit is one **review item**: one sanitized candidate-escalation event. Counts, queues, budgets, and overlaps therefore describe review-item handling only. They do not measure source-level accuracy, people, effort, or model performance.

## Frozen C0 adaptation

The C0 adapter uses a user-selected frozen-output root and the four fixed settings `ucd_ch`, `ucd_pw`, `cd_ch`, and `cd_pw`. It produces only sanitized candidate-event records, whose public fields contain opaque source and locator hashes. A manifest is hashed before adaptation and rechecked before artifact writing; any selected-input mutation aborts the run.

The seed is `20260902`. Replays must use the same canonical event IDs for every arm and budget. Candidate events carry the complete policy-signal inventory with explicit evidence states; unavailable signals remain unavailable and are not fabricated.

## Arms and escalation budgets

Each replay compares six deterministic arms over the same review-item sequence:

| Arm | Operational role in this descriptive exercise |
| --- | --- |
| `never_ask` | Reference arm that proposes no escalation. |
| `always_ask` | Reference arm that proposes every available review item until budget handling applies. |
| `random_at_budget` | Seeded deterministic random reference arm. |
| `uncertainty_only` | Reference arm using the uncertainty signal only. |
| `fixed_threshold` | Reference arm using its fixed threshold rule. |
| `proposed_joint_policy` | Candidate joint-policy arm; it does not grant reviewer authority. |

Run each arm at 5%, 10%, and 20% of the available review-item units. Budgets are recorded as configured units and actual ledger consumption. All arm outputs are candidate-escalation descriptions only.

## StateDiagram and controlled-notes gates

StateDiagram is **inventory-only**. The present interface may produce a local aggregate inventory receipt only; it performs no evaluator configuration, network work, empirical evaluation, or C0 comparison. Its status remains blocked pending data-processing authorization.

Controlled notes are permitted only through the development-only provenance gate. They must remain local, fail closed on malformed or unauthorized provenance, and yield only a redacted private receipt. They are not a public result source and must not be used to establish outcome claims.

## Future empirical benchmark gate

Any future empirical benchmark is out of scope for this protocol until it has independent reviewers and an adjudication process. Before any outcome analysis, the study must establish approved data handling, independent reviewer roles, adjudication rules, outcome definitions, and a frozen analysis plan. That gate is required before interpreting candidate-escalation output as empirical evidence.

## Research context, not VEGO-AI results

- [Mozannar & Sontag (2020)](https://proceedings.mlr.press/v119/mozannar20b.html) provides a learning-to-defer framing in which a predictor can defer to a downstream expert.
- [Bouali et al. (2025)](https://www.scitepress.org/Link.aspx?doi=10.5220%2F0013481900003932) is included as related conceptual-modeling context; it is not evidence about this implementation.
- [Silva et al. (2026)](https://link.springer.com/book/10.1007/978-3-032-08623-5) appears in the ER 2025 proceedings section on LLM-enabled modeling; it is context, not a VEGO-AI comparison.
- [NIST AI RMF](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf) provides governance, mapping, measurement, and management vocabulary for AI-risk work.

These references motivate protocol vocabulary only. They do not validate VEGO-AI, select a policy, or supply study outcomes.
