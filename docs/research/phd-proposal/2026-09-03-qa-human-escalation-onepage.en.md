# Preliminary Study: Finding When VEGO-AI Should Ask a Human

**Ali Hamed | for Prof. Iris Reinhartz-Berger and Prof. Arnon Sturm | 3 September 2026 | design, for your comments**

**QUESTION.** Can observable patterns in VEGO-AI's inter-agent Q&A communication automatically identify
situations where a human expert should be consulted? *(Addresses the WHEN part of provisional SQ1; wording
not yet approved.)*

**WHY THIS STUDY.** Stage one is only to find the cases that need a human — not whether the human helps.
The agents already talk to each other: when one asks another a question, that exchange is a record of the
system reaching the edge of what it can settle alone. Communication is the object; results are broken down
by agent and stage.

**DATA.** The frozen run over Cheers and ParkWise. **The Q&A record is half present**, and this decides the
plan: 12 real questions from the Domain Advisor to the Language Advisor survive in the canonical artifacts
(30 across all three runs), but there are **0 answers, 0 answer-confidence values and 0 Q&A rounds**. The
published corpus was produced by a harness that never ran the Q&A loop — its own code says
`no Q&A loop in evaluator`. The full pipeline does support Q&A. So every stored question is "unanswered"
for a harness reason, not an agent reason.

**THE STUDY IN ONE LINE.**

| Q&A events | → extract signals | → rule-based detector | → ALERT / NO ALERT | → blind A/B/C review | → confirmed / false / unclear |
| --- | --- | --- | --- | --- | --- |
| **12 exist** (questions only) | needs answers | not built | not run | not run | not run |

Only the first box has data today. Everything after it depends on obtaining a corpus that contains answers.

**Q&A SIGNALS.** Starting set, small on purpose. **S1** low answer confidence · **S2** medium answer
confidence · **S6** several rounds before resolution · **S7** no convergence. Each needs answers, so each
needs a corpus first. **S9** low Domain-Advisor mapping certainty is available today but is a *contextual*
signal, not a communication one, and is reported separately. **Dropped:** "unanswered question" — true of
100% of the current data by construction, so it carries no information.

**AUTOMATIC DETECTOR.** Rule-based, deterministic, auditable, no machine learning. Per episode: observable
features → frozen rule → **ALERT / NO ALERT**, and every alert says which feature fired. Version 1 is frozen
*before* anyone sees a human label.

**HUMAN VALIDATION.** Three independent reviewers (Ali, Iris, Arnon). For each episode: **human intervention
required / not required / unclear**, plus one line of reasoning. Blind first pass — reviewers do not see
what the detector said. Then agreement is measured, then disagreements are adjudicated.

**MEASURES.** Events reviewed · alerts raised · confirmed / false / unclear alerts · **alert yield**
(confirmed ÷ alerts) · **false-alert rate** · reviewer agreement before adjudication. If non-alert events
are also reviewed, we can add missed cases and coverage. If only alerts are reviewed, coverage cannot be
computed and will not be reported.

**EXPECTED OUTPUT.** A list of communication patterns that the three of us judge to be genuine points where
a human should be consulted, with the alert yield and false-alert rate for each. That is a candidate set of
automatic escalation conditions.

**WHAT WE NEED FIRST.** One decision. Either **(a)** ask the original authors for the `interaction_log.jsonl`
the run configuration says was written but which was not shipped — zero cost, and it may already contain
the missing material; or **(b)** re-run the pipeline on one setting to produce answered Q&A, which costs
model calls and reverses our "nothing is re-run" rule. We recommend (a) first.

**LIMITATIONS.** Small number of episodes. Answer confidence is the model's own self-report and no code
checks it. Reviewers are the three of us, not independent assessors. The study says nothing about whether
asking a human improves the result — that is a later stage. Independent expert labels remain 0 of 24.
