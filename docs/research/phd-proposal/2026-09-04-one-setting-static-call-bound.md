# Study 1 static provider-call bound

This is a static formula only. It was produced without invoking a provider and
must be recalculated from the selected setting immediately before authorization.

Let `N` be the number of case models and `R = MAX_QA_ROUNDS = 10`.

| Component | Minimum calls | Worst-case calls | Assumption |
|---|---:|---:|---|
| Phase 1 language template | 1 | 1 | One template request |
| Phase 2 Agent 2 guidelines | 1 | `3R = 30` | One guideline request plus up to language and domain answer calls per round |
| Phase 3 per case | `3N` | `61N` | Map once; resolve and audit each use up to `R` rounds, each with two possible answer calls |
| Phase 4 identify/classify | 2 | `1 + 3R = 31` | One identify request and classify loop |
| Phase 4 feedback loop | 0 | 20 | Only if flagged patterns exist: up to `R` feedback requests plus one language answer per round |
| **Total** | **`6 + 3N`** | **`82 + 61N`** | Conservative control-flow bound |

`max_concurrent_cases` is the configured semaphore limit (currently 2 in the
offline fixture; the real setting must supply its value). The configured model
is inherited from the selected run configuration and is not assumed here.
Token counts, provider pricing, and monetary cost are **TO BE MEASURED**; no
API call or cost estimate was fabricated.
