# AirTravel later paid-run decision packet — not an authorization

Status: **NOT_AUTHORIZED**. Cost: **TO BE MEASURED**. No paid grant exists or is created here. This document cannot authorize the offline fake preflight either.

## Source-bound configuration observations

At base `c34d3954b5e080d090017d2ea655d454d75a6b92`, protected `VEGO-AI/framework/llm_client.py:39` imports `AsyncOpenAI`; its `MODEL` at line 43 is `gpt-4o`. Protected `orchestrator.py:591` constructs LLMClient and uses `cfg.get("model", "gpt-4o")`. These are code defaults, **not a user-confirmed model selection**, not a recommendation and not a claim about current provider availability or pricing. No provider lookup was performed.

| Decision field | Current observation or proposed bounded value |
|---|---|
| Provider adapter | Existing OpenAI AsyncOpenAI wrapper; not invoked |
| Configured default model | gpt-4o; user confirmation NOT_DOCUMENTED |
| Setting / corpus | cd_airtravel / text2uml_airtravel_253b26dc |
| N and logical-call range | 4; 16–326 for one complete pass, not two combined |
| Proposed logical-call hard cap | 326; requires independent enforcement approval before paid execution |
| Proposed transport-attempt hard cap | 326 total provider requests, including retries; not yet implemented/authorized |
| Proposed concurrency | 2 case tasks |
| Proposed timeout | 1800 seconds; paid-run enforcement must be separately verified |
| Cost | TO BE MEASURED; no monetary estimate or budget inferred |
| Private output | A new, exact, empty ignored child under external_data/airtravel-pr38; absolute path is bound only in the future private request |
| Credential status | NOT_CHECKED in this packet; future gate may record presence boolean only, never values |
| Paid authorization | NOT_AUTHORIZED; distinct owner-issued grant required |

The static bound counts orchestrator logical `client.call` invocations, not HTTP retry attempts. The protected wrapper permits parse retries (`MAX_PARSE_RETRIES=2`); SDK retries require separate accounting. Consequently 326 logical calls alone is **not** a spend ceiling. Any paid packet must cap transport attempts and obtain an explicit monetary/token budget; lack of either is a stop condition. This task changes no protected retry behavior.

## Required measured receipt fields after a separately authorized future run

Record requested and returned model IDs, provider, run/commit/configuration/input hashes, logical calls, transport attempts and retries, concurrency, elapsed time, input/output/cached/reasoning tokens where supplied, usage-unavailable flags, actual currency and charged/estimated cost with its price-source date, parse failures, finish status, exception class, output hashes, and explicit authorization hash. Never convert unavailable usage into zero or claim supervisor approval from successful execution.

Abort on absent/mismatched authorization; unconfirmed model; missing budget; source/runtime drift; nonempty or nonprivate output; quota, timeout, transport-attempt or cost-cap breach; unaccounted retries; unexpected endpoint; missing required instrumentation; or technical failure. No automatic retry of the experiment, no fallback model and no subsequent Detector analysis after failure.

GPL review concerns publication/redistribution of upstream-derived material. It does not prohibit private local fake preflight, but neither this distinction nor green CI grants permission to publish raw bytes or execute a paid run.

Human decisions still required: approve the offline packet first; issue an exact matching local fake grant; review its future evidence; then separately choose provider/model, monetary/token limits, retry policy and exact paid command. This sequence remains unperformed.
