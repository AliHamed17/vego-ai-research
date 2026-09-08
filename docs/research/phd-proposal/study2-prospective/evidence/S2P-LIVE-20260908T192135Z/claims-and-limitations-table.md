# Claims and Limitations Table

Run `S2P-LIVE-20260908T192135Z`.

| Claim | Observation | Evidence class | Status |
|---|---|---|---|
| Artifact completion | ON 9/12, OFF 12/12 | PROSPECTIVE EMPIRICAL EVIDENCE | PERMITTED (descriptive) |
| Structural validity | ON 9 consistent of 9; OFF 7 of 12 | PROSPECTIVE EMPIRICAL EVIDENCE | PERMITTED (descriptive) |
| Requests and cost | ON 227 req / 0.9029 USD; OFF 12 req / 0.0530 USD | PROSPECTIVE EMPIRICAL EVIDENCE | PERMITTED (descriptive; not superiority) |
| Elapsed time | ON 1712.78 s; OFF 238.696 s | PROSPECTIVE EMPIRICAL EVIDENCE | PERMITTED (descriptive; one day) |
| Technical failures | ON 3, OFF 0 | PROSPECTIVE EMPIRICAL EVIDENCE | PERMITTED |
| Communication evidence | ON 16 episodes; OFF none by design | PROSPECTIVE EMPIRICAL EVIDENCE / NOT_AVAILABLE (OFF) | PERMITTED as availability, not as deficit |
| Detector-v1 labels | STRONG_ALERT 13, EXCLUDED 2, WEAK_ALERT 1 | PROSPECTIVE EMPIRICAL EVIDENCE | PERMITTED as candidate labels only |
| Detector-v1 under OFF | NOT_APPLICABLE | NOT_APPLICABLE | FORBIDDEN to report as zero alerts |
| Alert correctness / precision / recall / F1 | no human labels | NOT_MEASURED | FORBIDDEN |
| Human benefit / workload | no raters yet | NOT_MEASURED | FORBIDDEN |
| Quality superiority of either condition | no ground truth, no rated quality | NOT_MEASURED | FORBIDDEN |
| Mapping-row counts as a cross-condition quality measure | ON 9 rows over 9 artifacts against Domain-Advisor guidelines; OFF 202 rows over 12 artifacts against self-derived guidelines | PROSPECTIVE EMPIRICAL EVIDENCE | FORBIDDEN as quality; PERMITTED as structural description with the construction caveat |
| Generalisation beyond corpus/model/day | single corpus, model, day | NOT_AVAILABLE | FORBIDDEN |
| Preflight fixture behaviour | harness exercised with fake provider | ENGINEERING-ONLY FIXTURE | PERMITTED as engineering evidence only |

Limitations attached to every row: one public LLM-generated corpus; 12 seeded paired cases of 21; one model at the provider default temperature on one day; ON per-case cost and time are attributions under concurrency; structural metrics are not quality judgements; Detector-v1 labels are candidates, not confirmed problems.
