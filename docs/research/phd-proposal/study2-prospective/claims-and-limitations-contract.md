# Study 2 Prospective: Claims and Limitations Contract

**Status:** FROZEN 2026-09-08. Every published result carries exactly one
evidence class: PROSPECTIVE EMPIRICAL EVIDENCE, ARCHIVAL-RETROSPECTIVE
DESCRIPTIVE EVIDENCE, ENGINEERING-ONLY FIXTURE, NOT_MEASURED, or NOT_AVAILABLE.

## 1. Permitted claims (after execution, descriptive only)

| Claim | Evidence class | Condition(s) | Denominator |
|---|---|---|---|
| Per-case artifact completion and structural validity under each condition | PROSPECTIVE EMPIRICAL EVIDENCE | ON, OFF | 12 planned paired cases |
| Provider requests, tokens and priced cost per condition, ON split into setting-level and case-attributed | PROSPECTIVE EMPIRICAL EVIDENCE | ON, OFF | all recorded requests including retries |
| Elapsed time per condition; OFF per case exact; ON per case approximate | PROSPECTIVE EMPIRICAL EVIDENCE | ON, OFF | per condition, per case |
| Technical failures and retries per condition | PROSPECTIVE EMPIRICAL EVIDENCE | ON, OFF | 12 planned paired cases |
| Recorded inter-agent episodes, questions, answers, routes, termination reasons | PROSPECTIVE EMPIRICAL EVIDENCE | ON | recorded episodes |
| Detector-v1 candidate labels per scientifically complete episode | PROSPECTIVE EMPIRICAL EVIDENCE | ON | scientifically complete episodes |
| OFF has no communication evidence by design | NOT_AVAILABLE | OFF | structural, not measured |
| Detector-v1 under OFF | NOT_APPLICABLE | OFF | undefined, never zero |
| Blinded human assessment outcomes | NOT_MEASURED | ON | cards scored by two raters (none yet) |
| Preflight behaviour of the harness under the fake provider | ENGINEERING-ONLY FIXTURE | both | fixture cases |

## 2. Forbidden conclusions

1. Detector-v1 alerts are correct. No human labels exist.
2. VEGO-AI is universally better, or better on quality. No ground truth; no
   rated quality yet.
3. One condition is superior because of cost alone.
4. OFF produced zero alerts. Detector-v1 is NOT_APPLICABLE under OFF.
5. Fixture or preflight output is empirical evidence.
6. A model judgement is a human judgement.
7. Results generalise beyond this corpus, model, day and configuration.
8. Any statement about human benefit, workload reduction, accuracy, recall,
   precision, F1 or causality.

## 3. Limitations that accompany every result

- One public LLM-generated corpus; not student data; not representative.
- Twelve paired cases drawn by seed from a frame of twenty-one.
- One provider model on one day at the provider default temperature; a second
  run may differ.
- ON per-case cost and time are attributions under concurrency, not isolated
  measurements; setting-level ON cost is shared across cases.
- Structural metrics describe artifacts; they do not judge correctness.
- Detector-v1 labels are candidates for inspection, not confirmed problems.
- Three selected inputs are byte-identical to Study 1 inputs; no Study 1
  output is reused and no pooling with Study 1 is performed.

## 4. Numbers that may appear in prose

Only numbers that appear in the public aggregate or in the frozen manifest,
each with its denominator and evidence class. Every chart carries title,
source, condition, denominator, evidence class, metric definition and a
one-line limitation.
