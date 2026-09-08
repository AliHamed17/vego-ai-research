# Technical Appendix: Study 2 Prospective Run `S2P-LIVE-20260908T192135Z`

Evidence class: **PROSPECTIVE EMPIRICAL EVIDENCE**. Mode: LIVE. Execution head `3a62d91a48205e3a78cebf9a352e95e6615b97b8`. Manifest `d05ece7e2d15aed1f2b4696f1c7939792f435790dfcd568e25b41d9691abae08`.

## 1. Frozen configuration

| Item | Value |
|---|---|
| Provider / model | openai / gpt-5.6-luna (chat.completions) |
| Request parameters | max_completion_tokens 16384; temperature PROVIDER_DEFAULT_NOT_SENT; seed NOT_SENT; roles ['system', 'user'] |
| Allowed host | api.openai.com |
| Caps | total 267; ON 228 (19/case); OFF 36 (3/case) |
| Budget | hard ceiling 6.00 USD; guard 5.90; per-request reserve 0.0220608; whole-study reservation 5.8241 |
| Case ids | 01, 02, 03, 05, 06, 07, 08, 12, 15, 18, 20, 21 |
| Started / completed (UTC) | 2026-09-08T19:21:36.106Z / 2026-09-08T19:54:15.824Z |

## 2. Gates

| Gate | Passed | Detail |
|---|---|---|
| corpus_hashes_verified_at_load | yes | domain description and every selected case match the frozen digests |
| credential_present_value_unread | yes | OPENAI_API_KEY present in process environment, value never read by the harness |
| eligible_inventory_verified | yes | 21 eligible cases, every digest re-verified |
| expected_head_supplied | yes | live execution requires --expected-head |
| frozen_model_and_host | yes | gpt-5.6-luna via ['api.openai.com'] |
| frozen_selection_document_matches | yes | case ids and digests agree |
| git_head_matches_expected | yes | HEAD 3a62d91a4820 |
| manifest_loaded_and_self_bound | yes | d05ece7e2d15aed1 |
| minimum_paired_cases | yes | 12 paired cases |
| off_isolation_before_start | yes | no orchestration, Q&A, detector or queue module loaded |
| on_unit_reservation_before_start | yes | 265 reservable requests remain, ON cap 228 |
| output_root_fresh | yes | output root must not exist yet |
| output_root_safe | yes | absolute, inside the private root, no symlink or reparse point |
| private_runtime_root_present | yes | fullframe_runtime under the private root |
| selection_reproduced_from_seed | yes | 01,02,03,05,06,07,08,12,15,18,20,21 |
| whole_study_reservation_within_guard | yes | 264 requests x 0.0220608 = 5.8241 USD |
| working_tree_clean | yes | tracked files must be unmodified |

## 3. Spend and requests

| Quantity | VEGO_AI_ON | VEGO_AI_OFF | Total |
|---|---|---|---|
| Requests (incl. retries) | 227 | 12 | 240 |
| Successful requests | 227 | 12 | |
| Transport errors / retried | 0 / 0 | 0 / 0 | |
| Provider errors | 0 | 0 | |
| Prompt tokens | 2646887 | 17061 | 2663948 |
| Completion tokens | 311238 | 41361 | 352599 |
| Cost USD | 0.902863 | 0.053045 | 0.955908 |
| Elapsed seconds | 1712.78 | 238.696 | |
| ON setting-level requests / cost | 2 / 0.007457 | | |
| ON case-attributed requests / cost | 225 / 0.895406 | | |
| Finish reasons | {'stop': 227} | {'stop': 12} | |
| Response models | {'gpt-5.6-luna': 227} | {'gpt-5.6-luna': 12} | |
| Guard refusals | | | 2 |
| Requests counted by guard / ledger rows | | | 240 / 239 |
| Unrecorded in-flight requests (charged at full reserve) | | | 1 |
| Spend upper bound USD | | | 0.977969 |

Accounting note: a request reserved by the guard but cancelled in flight when a cap stopped the condition returns no usage; it is counted as issued and charged at the full per-request reservation in the upper bound.

## 4. Communication and Detector-v1 (ON only)

Episodes 16 (scientifically complete 14); classifications {'STRONG_ALERT': 13, 'EXCLUDED': 2, 'WEAK_ALERT': 1}; signals {'S1_LOW_ANSWER_CONFIDENCE': 13, 'S2_MEDIUM_ANSWER_CONFIDENCE': 11, 'S6_MULTIPLE_QA_ROUNDS': 14, 'S7_TERMINATED_MAX_ROUNDS': 5}; termination {'CONVERGED': 9, 'INCOMPLETE_TECHNICAL': 2, 'TERMINATED_MAX_ROUNDS': 5}; episodes per case {'01': 2, '02': 1, '03': 1, '05': 2, '06': 1, '07': 1, '08': 2, '12': 2, '15': 2, '18': 1, '20': 1}; cases with no episode ['21'].

Routes: [{"question_count": 64, "source_agent": "agent3", "target_agent": "agent1"}, {"question_count": 191, "source_agent": "agent3", "target_agent": "agent2"}]

## 5. Integrity bindings

| Artifact | SHA-256 |
|---|---|
| Frozen manifest | d05ece7e2d15aed1f2b4696f1c7939792f435790dfcd568e25b41d9691abae08 |
| Detector-v1 source | 38c8fe3cb5b912e7ed597e83e119ab18c3149adeb9174e5a6910b36d7ed97bd1 |
| protected runtime agent1_language_advisor.py | 13e152fe4ec3b417a8c515bbe1bdb28ff952766579ce1ed6463a7ad9fa5b724e |
| protected runtime agent2_domain_advisor.py | fdf330b99295e871ad3cc3e5e934bb04a15f996a5060ea35d43fa13243d16d79 |
| protected runtime agent3_model_inspector.py | 4d0042777040f76abc1ca616a6e1dddcda591ddec54478fa2491b5020a817fa4 |
| protected runtime agent4_variability_explorer.py | 6b043c5643f9211d93ac402a9bf98685727e2cd92cab3377d1462dc3417df2ff |
| protected runtime llm_client.py | 1a36b4ee860619db97a6ff84ecf64b4845a292ef67cf432c17a86eacd56f55da |
| protected runtime orchestrator.py | fca4b885ee07381db0f02e558b1aebf25bdc7c27da1c471fd3103d7e0e2d5b88 |
| protected runtime qa_communication.py | 9f2cda1dc52fe919be22ac2ea42d61dce3ed22d3fae7ae27077b3db821594236 |
| protected runtime qa_registry.py | ab189d3fd954ea03ba891f5746b36eff8889baeff73d7594f820e68f8762ad5f |
| protected runtime state.py | d8492a623804065b86905d6183979c322d6f83376bf91026e718c615eea1730d |
| OFF prompt template | 8d4e1d8fe03e5fe87db48d2cb679921102a7cb8f098e2c1e7ff6cd5e1e7d27b8 |

## 6. Validation of published values

- receipt_binding_valid: True
- published_sha256: df71bcaa0f3773f89c96f557f2e36f6baf7e8580876794e590593f14e91f880e
- recomputed_sha256: df71bcaa0f3773f89c96f557f2e36f6baf7e8580876794e590593f14e91f880e
- match: True
- ledger_requests: 239
- receipt_requests: 240
- ledger_matches_receipt: False
- ledger_cost_usd: 0.955908
- receipt_cost_usd: 0.955908

## 7. Human-review cards (private)

- {"blinding": "no case id, episode id, condition, detector label or timestamp on any card; order shuffled with a fixed seed", "cards": 14, "cards_sha256": "bfaad81770c09d29a6ce208c702356f2f43d2771f319f5b85acbd564c8fcc53a", "exchanges": 235, "key_sha256": "68ed3b4946602bbe08d9d2af6cc8d26fce6fc47e0d9fabefbf67f16a6c58aff4", "location": "${VEGO_PRIVATE_EVIDENCE_ROOT}/study2-prospective/S2P-LIVE-20260908T192135Z/human-review/", "raters_scored": 0, "status": "NOT_MEASURED"}
