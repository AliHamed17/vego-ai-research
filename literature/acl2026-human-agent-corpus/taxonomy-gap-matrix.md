# ACL 2026 Taxonomy Coverage and Candidate-Gap Matrix

Source: Zou et al., *LLM-Based Human-Agent Collaboration and Interaction Systems:
A Survey*, Findings of ACL 2026, DOI `10.18653/v1/2026.findings-acl.1811`, and the associated repository
at commit `7b3ba9deefe99172748582f6025d995ccc2a6f86`.

## Reconciled corpus

| Layer | Raw rows | Distinct works | Meaning |
| --- | ---: | ---: | --- |
| Latest Research Papers | 106 | 106 | Chronological repository list |
| Applications, Datasets & Benchmarks | 62 | 57 | Application/category occurrences |
| Taxonomy | 357 | 90 | Repeated work-by-taxonomy assignments |
| Union | 525 | 116 | Bounded corpus after connected-component deduplication |

Taxonomy rows: Human Feedback `89`; Interaction `89`; Orchestration `90`;
Communication `89`.

## What the source taxonomy explicitly encodes

| Branch | Encoded dimensions | Safe Chapter 2 use |
| --- | --- | --- |
| Human Feedback | type, subtype, granularity, phase | Describe what information/control humans provide and when |
| Interaction | interaction type and variant | Compare collaboration, supervision, delegation, cooperation, and coordination |
| Orchestration | strategy and synchronization | Describe one-by-one/simultaneous and synchronous/asynchronous control |
| Communication | structure and mode | Describe centralized/decentralized/hierarchical communication and conversation/observation |

## Dimensions not encoded by the taxonomy schema

The following are **schema-coverage observations**, not claims that no paper in
the corpus discusses the topic: case grounding; provenance; accountable expert
authority; validation and adjudication; conflict handling; scope, expiry, and
revocation; safe reuse of a judgment artifact; cross-context transfer of that
artifact; and measured expert burden. Full-text screening is required before
any absence or novelty claim.

## Evidence-safe Chapter 2 structure

1. **2.1 Review scope and evidence method.** Distinguish the bounded ACL corpus,
   the separate local candidate corpus, and deferred QL-01 through QL-05.
2. **2.2 Problem setting: guideline operationalization and observed
   variability.** Establish the domain problem before presenting a solution.
3. **2.3 Agentic systems and the human-agent collaboration design space.** Use
   the survey's four explicit taxonomy branches and their encoded dimensions.
4. **2.4 Selective intervention and bounded oversight.** Synthesize candidate
   evidence relevant to when a system asks; do not infer burden reduction from
   routing counts.
5. **2.5 Feedback, judgment representation, governance, and reuse.** Separate
   source-reported feedback mechanisms from the still-hypothetical governed
   judgment lifecycle.
6. **2.6 Evaluation, transfer, and context boundaries.** Separate general
   collaboration benchmarks from transfer of governed judgment artifacts.
7. **2.7 Synthesis and candidate gaps.** Every gap is source-backed or labelled
   `Pending full-text review`; provisional RQ wording is not used as a heading.

## Frozen boundaries

- RQ wording, exploration versus identification, and human versus expert remain unresolved.
- QL-01 through QL-05 remain protocol-ready and deferred after the proposal-stage bounded corpus pass.
- The pre-existing methodology draft is frozen; this tranche does not extend it.
