# Budget and Spend Receipt

Run `S2P-LIVE-20260908T192135Z`, mode LIVE.

| Item | Reserved / frozen | Actual |
|---|---|---|
| Hard ceiling (USD) | 6.00 | within: True |
| Guard ceiling (USD) | 5.90 | spent 0.955908 |
| Per-request reserve (USD) | 0.0220608 | |
| Whole-study reservation (USD) | 5.8241 | 0.955908 (16.4% of reservation) |
| Total request cap | 267 | 240 |
| VEGO_AI_ON request cap | 228 | 228 |
| VEGO_AI_OFF request cap | 36 | 12 |
| Prompt tokens | | 2663948 |
| Completion tokens | | 352599 |
| Transport errors (ON / OFF) | | 0 / 0 |
| Retried requests (ON / OFF) | | 0 / 0 |
| Guard refusals | | 2 [{'code': 'CONDITION_REQUEST_CAP', 'condition': 'VEGO_AI_ON', 'detail': 'VEGO_AI_ON request cap 228 reached'}, {'code': 'CONDITION_REQUEST_CAP', 'condition': 'VEGO_AI_ON', 'detail': 'VEGO_AI_ON request cap 228 reached'}] |
| Unrecorded in-flight requests / spend upper bound (USD) | | 1 / 0.977969 |
| Pricing (USD per 1M tokens) | in 0.2 / out 1.2 | |

Chosen protocol: A_HIGHEST_COVERAGE — A_HIGHEST_COVERAGE: the primary question is a paired per-case comparison, so distinct paired units are worth more than repeats of a default-temperature stochastic system; B has the same reservation with half the distinct cases; C leaves two thirds of the affordable sample unused

Rules applied: never start a paired unit unless its full ON+OFF reservation fits; all twelve units are reserved before the first request; one transport retry per request, only for a documented transport/provider failure before valid output; a valid but undesirable result is never retried; every retry, failed call and parse re-attempt counts against the caps and the ceiling; a failed or incomplete case remains in the evidence and is reported; never stop early because results are favourable or unfavourable.
