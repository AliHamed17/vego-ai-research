# AirTravel authorization packet v3

Status: **AUTHORIZATION_REQUESTED_NOT_GRANTED**. Packet v2 is SUPERSEDED_NOT_AUTHORIZABLE.
PR: [38](https://github.com/AliHamed17/vego-ai-research/pull/38); do not merge or execute.
Green base: `c34d3954b5e080d090017d2ea655d454d75a6b92`. Correction parent: `3727acfe2130863ab6b737824a1718e7b3648b92`. Implementation commit: `28a1d95f39058e5b9dd3e7601584e2393311d405`.
The later owner-issued grant must bind the **full final corrected PR head**, independently compared to `git rev-parse HEAD`, this packet hash, harness hash, archive, command fingerprint, output directory and all protected hashes. A PR body or an assertion flag is not a grant. This immutable request plus a separate matching grant are both required; the request alone always fails. No grant is issued by this task.

## Future command and scope

Working directory: the exact checkout identified in the private `external_data/airtravel-pr38/private-execution-request.json` (generated on the executing machine). Verify its HEAD is the subsequently reviewed green PR head before issuing the grant. Public records intentionally omit personal absolute paths.

```powershell
python scripts/prepare_airtravel_protected_fake_preflight.py --execute --authorization-packet docs/research/phd-proposal/2026-09-05-airtravel-protected-fake-preflight-authorization-packet-v3.md --authorization-grant external_data/airtravel-pr38/authorization-grant.json --runtime-root external_data/airtravel-pr38/runtime_input --runtime-archive external_data/airtravel-pr38/cd_airtravel-runtime-v1.0.2.zip --output-dir external_data/airtravel-pr38/authorized-fake-run --receipt external_data/airtravel-pr38/authorized-fake-run/preflight-receipt.json
```

DO NOT RUN this command now. The private request records its fully resolved executable/arguments and SHA-256 fingerprint. The grant file does not exist. The sole tracked example is `TEST_FIXTURE_ONLY` and is rejected.

The owner must separately supply `authorization-grant.message.txt` beside the grant, containing the exact human authorization message. Its SHA-256 is mandatory and compared independently. No message or grant is created here. This local owner-controlled receipt protocol is not cryptographic proof of authorship against a malicious user with filesystem write access. Grant type must be OFFLINE_FAKE_PREFLIGHT_ONLY; grantor Ali Hamed; current issue/expiry, final HEAD, implementation commit, packet/harness/call-bound/protected-manifest/archive/five runtime hashes, exact command/output, timeout 1800, cap 326, network prohibition and paid_execution_authorized=false must all match. A missing or changed binding fails before protected imports.

Allowed reads: clean tracked checkout files (including the protected table), exact five runtime files below, the runtime configuration/archive, packet and grant during validation. Provider credentials, browser profiles, key stores, subprocesses and dynamic native/provider imports are forbidden during orchestration. Allowed writes: **only** `external_data/airtravel-pr38/authorized-fake-run/`, initially absent/empty, symlink-free and Git-ignored. Fixed children: `baseline/`, `instrumented/`, `preflight-receipt.json`. Full private resolved paths are fingerprint-bound in the grant.

Each pipeline child writes pipeline_state.json, pipeline.log, language_template.json, reference_guidelines.json, compliance_vectors.json, uncovered_fragments.json, deviation_patterns.json, variability_classifications.json, lang_qa_history.json, dom_qa_history.json and human_review_queue.jsonl. Instrumented alone adds qa_events.jsonl. Maximum 40 files and 16777216 persisted bytes; conservative cumulative write quota is also enforced. Unexpected files, outside writes, nonempty destinations or tracked/protected drift fail closed. The receipt cannot escape the granted directory.

## Two-pass checks and timeout

Direct `RecordingFake(two_rounds)` baseline versus the same deterministic fake through `Proxy` and the external registry observer. Expected 46 logical calls per pass, 92 combined; enforced minimum/maximum **16–326 per pass**, never 326 combined. Absolute combined maximum 652. The bound verifies the current protected orchestrator hash before using its inventory. Costs and tokens: **TO BE MEASURED** (not HTTP retry bounds).

Require ordered labels, prompt hashes, answer hashes, per-pass counts, complete PipelineState and every scientific output hash to match. Only logs (wall-clock timestamps) are excluded from scientific byte parity; observer events/receipts are the permitted additions. All four case IDs 01–04 and all four phases must complete.

Timeout: 1800 seconds around the complete two-pass coroutine, with cancellation, no retry, LLMClient/registry restoration, environment restoration and handler closure before a TECHNICAL_FAILED receipt. Fixture tests use a short timeout; CLI cannot override it. Trusted deterministic Python control flow yields at each fake call. This is a Python audit/IO safety boundary, not a kernel sandbox or a defense against hostile native extensions. Event-loop local IPC is created before external-network denial; protected execution permits no network attempt. Any attempted socket/DNS/provider path is counted and fails even if caught below.

Lifecycle: actual source/skill/case/round labels and registry-assigned IDs bind exact pre-hash questions to answers. One loop invocation retains its episode across rounds and targets. A questionless next round closes CONVERGED; answered final round closes TERMINATED_MAX_ROUNDS; exception/missing answer/correlation failure closes INCOMPLETE_TECHNICAL. Never label every open episode converged. Unresolved/cross-run/cross-episode/duplicate/post-terminal evidence is rejected. No helper-only routes are counted as provider observations.

Counters: protected_orchestrator_fake_episode_count counts episodes; protected_orchestrator_fake_route_pair_count and protected_orchestrator_fake_route_pairs count/list distinct ordered source_agent→target_agent pairs. Before execution counts are NOT_EXECUTED and the list is empty. direct_fake_call_count and instrumented_fake_call_count are separate; compatibility baseline/route aliases retain the same semantics. provider_backed_production_route_pair_count, external_provider_call_count and detector_v1_experimental_run_count remain zero. Detector-v1 is not invoked by preflight.

Parity includes ordered labels, source-bound branch inventory and per-phase/per-case counts, complete return-value decision hashes, full unmodified state, scientific file hashes and final completed-phase result. No scientific field is normalized away. Run identity derives from grant hash, command hash and commit; a different grant/command has a different identity, and the same output cannot be overwritten. Before/after inventories accompany the receipt.

## Privacy, failure, rollback and expiry

Only the Q&A event log stores hashes, lengths and machine fields. Pipeline artifacts can contain complete fake/public-external scientific state. Every output remains private and ignored; nothing is automatically committed. Extracted public receipts require a separate privacy scan. Future paid-run raw prompts/answers remain private.

On failure: stop without retry, report technical failure, never treat empty events as valid zero-Q&A. Keep partial evidence private. Rollback: restore the reviewed checkout via an ordinary reviewed revert if needed; after verifying its exact resolved path, remove only this run's ignored output directory. Do not reset main, clean the repository, or delete unrelated work. No protected file modification is requested.

Expiry: any bound commit/hash/path/command change, main drift, or expiry timestamp invalidates the grant. Ali alone may issue the later matching machine grant after explicit approval of this exact packet and green corrected head. GPL review concerns publication/redistribution, not private local preflight. This request authorizes neither a provider, paid run, Detector-v1 experimental analysis, raw-data publication nor synthetic corpus generation.

## Runtime bytes

Archive SHA-256: `e37baecd20a0c84eb1d9b87b3b78a23bc4b4eb8a9824ad3086dc30aa35fdd31f`. Setting `cd_airtravel`, corpus `text2uml_airtravel_253b26dc`, N=4. Reference files are outside runtime inputs.

| Runtime path | Bytes | SHA-256 |
|---|---:|---|
| `domain_description/description.md` | 1477 | `96bc8a6fbf2c2fdd93592fdbf6fac7c2b9db403494fe2d5a45e0a2bcbf0167e2` |
| `candidate_models/01_result_one_claude-sonnet-4-6.txt` | 1248 | `240b034834e383b9844e9a3e9796f6be9b3d47fc95de6606ed022d278d751f91` |
| `candidate_models/02_result_one_codestral-2508.txt` | 1272 | `08399ca9432c1399f3f9784d34741314e4d39e40307a6efb14fa92a1c138b1d6` |
| `candidate_models/03_result_one_deepseek-chat.txt` | 1324 | `ee4d689d59c9ce3a5e8ff385747641954bd4821f2efeb18e581dcd1d5441d20a` |
| `candidate_models/04_result_one_gemini-2.5-flash.txt` | 1231 | `1c3d15eac71fcaab138857dbbc7153833b3df55ab57925ac756a79dc28dc847a` |

## Corrected executable content

| Path | SHA-256 |
|---|---|
| `scripts/prepare_airtravel_protected_fake_preflight.py` | `ec4c0aa4b948e4c5ee33244470da9d6a7b436ce85cc57c940fb4389a4024c997` |
| `scripts/airtravel_preflight_contract.py` | `f6bedbd904907656b0af929c0aa133481f6ad6f289ed4c8e9b913bb1a3dc6db8` |
| `scripts/airtravel_execution_safety.py` | `8c4cb6814311aee4d5b8a328aa117881daf3186bdcc6b86782f1b02a752bd203` |
| `scripts/airtravel_local_observer.py` | `e60db39e7ad52ac789372db592d91d2c9a3a81d8193c09346e39a09107e25228` |
| `scripts/airtravel_preflight_execution.py` | `879d7d99c33dddaf319527a85273d40a6402e9480bdeb65742c367623f5a2da9` |
| `scripts/render_airtravel_results.py` | `4174e114c1aa67f06f911d0377c0d18d0cdcce085965403ea9b846356d25da88` |
| `schemas/airtravel-technical-receipt-v1.schema.json` | `4a6ab510230e8288c5cd111c2796a8f24849c88db7808cbeaf30b74fe6a5060d` |
| `scripts/study1_call_bound.py` | `82d059aab17da87b9bd0c4d121b2daa7717c8b5167c68df2cddba4f72b96936c` |
| `schemas/airtravel-fake-grant-v1.schema.json` | `0f426c3f1d8c7791127481ba7714eb0e009fc4a2dcecfdfe7b7c5ca9ecdc396a` |
| `schemas/qa-communication-event-v1.schema.json` | `7df773a6a141a656b32012abd35c34aab25002f2a873c84e61c9ade06af670b2` |
| `scripts/extract_qa_escalation_features.py` | `8723f8f7cb75df51d5c82bda2b604bfaa2b72c230ce580090f7ba06cf3457974` |

## Protected inventory

| Full repository-relative path | Before = after SHA-256 | Access |
|---|---|---|
| `VEGO-AI/eval/README_EVALUATOR.md` | `b24280599b799a121d4758f9d9eb81b1451cb9b178ce1c60fb0ebdfe9ac20832` | READ_ONLY / unchanged |
| `VEGO-AI/eval/agentA_language_evaluator.py` | `de412e3ab42dc783c3fdd94dc6e42969c84d565b687277e2c359c2a0299a28cf` | READ_ONLY / unchanged |
| `VEGO-AI/eval/agentB_domain_evaluator.py` | `26b299587fc54cd2a19bc0841aba6f9e322c253e3e0523ebc4f06c8f697feb8e` | READ_ONLY / unchanged |
| `VEGO-AI/eval/agentC_case_scorer.py` | `27011d8569736601bc2f60a5510354024b7ff27a7aba350119c824a4adbaf2e8` | READ_ONLY / unchanged |
| `VEGO-AI/eval/agentD_variability_evaluator.py` | `53b2cc4aae3a3cb4a903872359bbf60c060e7c62d03a15b3834b8f7db7503c14` | READ_ONLY / unchanged |
| `VEGO-AI/eval/eval_config.json` | `87f35c96b5b67f4785ac0abd4d24cf100d5b499ba562f0683e5b644c90bc3f5e` | READ_ONLY / unchanged |
| `VEGO-AI/eval/evaluator.py` | `ac5c5062e0275546154b9d526ab431a4a90cb68480c60f7d2060c14dd8a80b23` | READ_ONLY / unchanged |
| `VEGO-AI/framework/README.md` | `d3035fa08cdc32bfc14d26c3b567ac901fc2fef87b4bdb15b74af0c483a0a825` | READ_ONLY / unchanged |
| `VEGO-AI/framework/agent1_language_advisor.py` | `13e152fe4ec3b417a8c515bbe1bdb28ff952766579ce1ed6463a7ad9fa5b724e` | READ_ONLY / unchanged |
| `VEGO-AI/framework/agent2_domain_advisor.py` | `fdf330b99295e871ad3cc3e5e934bb04a15f996a5060ea35d43fa13243d16d79` | READ_ONLY / unchanged |
| `VEGO-AI/framework/agent3_model_inspector.py` | `4d0042777040f76abc1ca616a6e1dddcda591ddec54478fa2491b5020a817fa4` | READ_ONLY / unchanged |
| `VEGO-AI/framework/agent4_variability_explorer.py` | `6b043c5643f9211d93ac402a9bf98685727e2cd92cab3377d1462dc3417df2ff` | READ_ONLY / unchanged |
| `VEGO-AI/framework/hlayer_architecture.py` | `b978176b03f389c5017cc6bfdb3237a1c0b2c5ea9d76793f927963bf6d04bfd5` | READ_ONLY / unchanged |
| `VEGO-AI/framework/human_feedback_manager.py` | `238e99d7bd652a0fde2884d8fd544c829dfbc8c66dddf404cd4b1eaef13e50e2` | READ_ONLY / unchanged |
| `VEGO-AI/framework/human_judgment_memory.py` | `87cc7113452f366a254f946a92877bc069e1c75bfc2185bf267dfdc0f74dd976` | READ_ONLY / unchanged |
| `VEGO-AI/framework/human_review_queue.py` | `499963663722cbb3892916df4a6e8d53ee5fdfab4876db3b2ef709100897944e` | READ_ONLY / unchanged |
| `VEGO-AI/framework/llm_client.py` | `1a36b4ee860619db97a6ff84ecf64b4845a292ef67cf432c17a86eacd56f55da` | READ_ONLY / unchanged |
| `VEGO-AI/framework/memory_advisor.py` | `143cefd87c3cbe51029b90f3f849384a4ee50df5d1d6e7f3394b2cb109c2e271` | READ_ONLY / unchanged |
| `VEGO-AI/framework/memory_informed_classifier.py` | `41518916a5b7fcb243564a9b3d2fed83cfba584211a10ca2198ad16cb4414171` | READ_ONLY / unchanged |
| `VEGO-AI/framework/orchestrator.py` | `fca4b885ee07381db0f02e558b1aebf25bdc7c27da1c471fd3103d7e0e2d5b88` | READ_ONLY / unchanged |
| `VEGO-AI/framework/qa_communication.py` | `9f2cda1dc52fe919be22ac2ea42d61dce3ed22d3fae7ae27077b3db821594236` | READ_ONLY / unchanged |
| `VEGO-AI/framework/qa_instrumented_runner.py` | `d187f8e8113a86caf24e55720e227f9a5f9b3466126969166bcefb83625a215f` | READ_ONLY / unchanged |
| `VEGO-AI/framework/qa_registry.py` | `ab189d3fd954ea03ba891f5746b36eff8889baeff73d7594f820e68f8762ad5f` | READ_ONLY / unchanged |
| `VEGO-AI/framework/requirements.txt` | `04f5965d2b72485f6c4fcc1c3a8e1fc1c3f5dae6641fb53e73fc04533b82c3cd` | READ_ONLY / unchanged |
| `VEGO-AI/framework/run_config.json` | `c185879270a318a2b7c3920f4a9c49c6be6ae807afe33eddb4d4577fd9603794` | READ_ONLY / unchanged |
| `VEGO-AI/framework/selective_intervention_policy.py` | `b43e18225e5ff03de29b9e69f1436de93ace23ddc3a2c0c1a4a72fd1fe518aff` | READ_ONLY / unchanged |
| `VEGO-AI/framework/state.py` | `d8492a623804065b86905d6183979c322d6f83376bf91026e718c615eea1730d` | READ_ONLY / unchanged |
| `VEGO-AI/inputs/README.md` | `78bf44ccc63fea7693f492416d7ee0f6fdebfa3771a04be2fe0935ff7e6e2e89` | READ_ONLY / unchanged |
| `VEGO-AI/inputs/ch/domain_description.txt` | `fda75e2cc9dbbfb9c74df5d567edb40a00aba3bcb4819079321acc8c9fb7538b` | READ_ONLY / unchanged |
| `VEGO-AI/inputs/ch/domain_description_cd.txt` | `172f461fa0fa9c9b3b64e81adbee91a708dcd59316eb88ec8a2b498d6f3ffca9` | READ_ONLY / unchanged |
| `VEGO-AI/inputs/ch/domain_description_ucd.txt` | `5e5da0ae931ca2f3db509fc8476b314f604fc2c639b212957576f5db8285eace` | READ_ONLY / unchanged |
| `VEGO-AI/inputs/human_feedback.example.jsonl` | `9d2fd7cfd17e892e8bf161f15c19eeb51db6d9c3d2897dc5b1ac2dbde629d6f0` | READ_ONLY / unchanged |
| `VEGO-AI/inputs/language_base_cd.txt` | `8247f4e4e19aed2198937969babaf7309efa1a6c66b665c556f9ad20e10003da` | READ_ONLY / unchanged |
| `VEGO-AI/inputs/language_base_ucd.txt` | `53d79578c30ad8e898d2773858036775c7bcfefd8c5d7e63744f062bd99528d8` | READ_ONLY / unchanged |
| `VEGO-AI/inputs/pw/domain_base_cd.txt` | `251dfd4d7526942b858679a5e54d16160eb2ea206bb2ed8a6ca3aeebb62cfe4f` | READ_ONLY / unchanged |
| `VEGO-AI/inputs/pw/domain_base_ucd.txt` | `4720627b6e5e8ec172d4b2922af972c17e761c8786dade2ec278ce4c964d3165` | READ_ONLY / unchanged |
| `VEGO-AI/inputs/pw/domain_description.txt` | `f4c43ff8c928294f9bde20e539c072ecae6dd564d038aeb0c9dd658fd543340b` | READ_ONLY / unchanged |
| `VEGO-AI/inputs/scoring_schema.txt` | `b0911d3921eeabdee7f93802cbf56a6d2b32a20e8e3a470ee7fc6709686ab506` | READ_ONLY / unchanged |
| `VEGO-AI/schemas/README.md` | `b3f629801ef4fbb6148ed9554ff003d8f7e07e709000229aa2ad61906ae715b9` | READ_ONLY / unchanged |
| `VEGO-AI/schemas/human_feedback.schema.json` | `170561aa00aff11fa264084383488618d6acc87f4e8fb69141def6985e26f2d7` | READ_ONLY / unchanged |
| `VEGO-AI/schemas/human_judgment.schema.json` | `2d28a9a5c2100cfe30b6e2e14f1780cf84518f7f8dacd344ac8d465911b4c1ad` | READ_ONLY / unchanged |
| `VEGO-AI/schemas/human_review_item.schema.json` | `1f3d0f74c624abfbfa8e8eda0600ceb1403e4e68426f9bb779e07e00265f4603` | READ_ONLY / unchanged |
| `VEGO-AI/schemas/memory_advice.schema.json` | `59240d67aac0cdc6236d0fe85cc757d123e4b446d127fa0c970004f3ef5c5024` | READ_ONLY / unchanged |
| `VEGO-AI/schemas/memory_informed_comparison.schema.json` | `d14af2b67940ec4f40957ddafad30dad2134355cd6f0ec94a6fe0b82f9069ade` | READ_ONLY / unchanged |
| `VEGO-AI/schemas/results_dashboard_snapshot.schema.json` | `04e128eb9abca49a60edb809f2600c40c39e162c14166c31b4a0c30e9cfffcf5` | READ_ONLY / unchanged |
| `VEGO-AI/tests/README.md` | `36f180bdee118cf4157c0faa0458464d16770c41a392dfa22129fb6b659ff49f` | READ_ONLY / unchanged |
| `VEGO-AI/tests/test_accuracy_improvement_analysis.py` | `6dcdb87f71d231cc2580171b830eeb66d93e2735a5351912464be2a8ce700a7b` | READ_ONLY / unchanged |
| `VEGO-AI/tests/test_human_feedback_manager.py` | `39538c746498791307a433153105dc950332e8b577a5b4b1acea73699c276832` | READ_ONLY / unchanged |
| `VEGO-AI/tests/test_human_judgment_memory.py` | `5f28d27c567984ef0d196ec5b2d58d3dc2158a4db4539cd4cdfefee3c990f7ee` | READ_ONLY / unchanged |
| `VEGO-AI/tests/test_human_review_queue.py` | `58f1a8ae340a03f99d1a1948fad7cadcfb01c53f4b5ede06c27014695b5a6329` | READ_ONLY / unchanged |
| `VEGO-AI/tests/test_llm_client_security.py` | `9349a6c61ba77e6c736fcc3757f3a27d07b42429cbbe8bd503ddc0ab19ea97d2` | READ_ONLY / unchanged |
| `VEGO-AI/tests/test_memory_advisor.py` | `6dbb6609cf10f45ebbf344e8b5448fe0eb3019c71c0aea5d7845d05053782745` | READ_ONLY / unchanged |
| `VEGO-AI/tests/test_memory_informed_classifier.py` | `0067b3cc4b4f6d866b15e5b730da83f17c6f13069239c0aa41e749004e0e52e9` | READ_ONLY / unchanged |
| `VEGO-AI/tests/test_qa_communication.py` | `ebd8b6dd133a617063f104056e6bce61310306ba0ba0a74e83abd4b8335b3c2d` | READ_ONLY / unchanged |
| `VEGO-AI/tests/test_qa_instrumented_runner.py` | `4e6c88fec0802a7caae67bf77a37d07384014330b9646478bc795f6ebbfe7c7f` | READ_ONLY / unchanged |
| `VEGO-AI/tests/test_results_dashboard.py` | `35f7109f36a934b7c780e422a1284a36fac368ab0eb1301f82c66deb31663e18` | READ_ONLY / unchanged |
| `VEGO-AI/tests/test_visualizer_helpers.py` | `d0ca91f1b175d1af843f7ea4e77b907530e029454ad3df75d619893289eb34c0` | READ_ONLY / unchanged |
| `scripts/hlayer_offline/__init__.py` | `25dc6d2880f9a3aa28ba291bb6286f0db592a4a2d870c4deac98079a82e580bf` | READ_ONLY / unchanged |
| `scripts/hlayer_offline/common.py` | `04be8da46aa7675739626b86f5782e113cdcf8b7fb51765bc182f6497007b835` | READ_ONLY / unchanged |
| `scripts/hlayer_offline/contracts.py` | `4f2b711246682f09a6348b0217f1c4e4b5dca53450382e92e1d80fc345b99529` | READ_ONLY / unchanged |
| `scripts/hlayer_offline/exp013.py` | `392f00b8ca9dfd538f628a825b2f234974f1d832fc25d79252bb2fa881faa267` | READ_ONLY / unchanged |
| `scripts/hlayer_offline/exp014.py` | `b0453e107cb814606881472d95af1cba28767900b1d44d4a55165c2af4ff1c7e` | READ_ONLY / unchanged |
| `scripts/hlayer_offline/exp015.py` | `a223f3a7beaa50c54fe1f846f03465ed77868038eecb2c1ad1d717785f8438fa` | READ_ONLY / unchanged |
| `scripts/hlayer_offline/exp016.py` | `aa1070596c0f86630cde884934f722a8e6ba1ed0f140caf3eef3ae69577709b0` | READ_ONLY / unchanged |
| `scripts/hlayer_offline/exp017.py` | `88092e489653a6286fecf820859f557f6826ae484aa04cb35fe79282980efbed` | READ_ONLY / unchanged |
| `scripts/hlayer_offline/exp018.py` | `571fcb5ca26b1c52d92554b77bd03405445fbbb79a769c61b86ab6d2060c30f9` | READ_ONLY / unchanged |
| `scripts/hlayer_offline/legacy_replay_adapter.py` | `8861b64a154e6c727f54770b5f6cafdf3b8bb6c9ff986c8a9ee36693af9428e3` | READ_ONLY / unchanged |
| `scripts/hlayer_offline/state_machine.py` | `54d15af6e457b85fe81ce2eae4c2948329c3db3fd5ab2c6991ec0a9ae4c5866e` | READ_ONLY / unchanged |
| `scripts/hlayer_offline/suite.py` | `ffbe787a8a1e53aee7bb64657d8863c7e3a9c4f025b5e0fd1e7372ab5cfe3c1f` | READ_ONLY / unchanged |
| `scripts/hlayer_offline/validator.py` | `c6d166504b6847b6d3d6bb80654e4905cad112eff7091f4a4a463bd22e903876` | READ_ONLY / unchanged |
| `src/vego_hlayer/__init__.py` | `7a10cd95ea118da0848e0b61a3ddd164ad49462c7f5328828d84b60780b16d3f` | READ_ONLY / unchanged |
| `src/vego_hlayer/adapters.py` | `6d97a5aaa288d30781dca80d320cea8cb47f8d95f53b655f45496748a31657df` | READ_ONLY / unchanged |
| `src/vego_hlayer/contracts.py` | `97881676db22c28cb9a8a3e45a57f1555e213f1f8849c8f9196b768f3cc6075b` | READ_ONLY / unchanged |
| `src/vego_hlayer/io_safety.py` | `c7ee7eab05c0c79b8e4196de51f345bcef72a81da4de667fddfefb304089b1cb` | READ_ONLY / unchanged |
| `src/vego_hlayer/runtime.py` | `bd285dafcda15ef34ebcbcfd465461bcb19ca28c9c59182e0749112e4c7880ec` | READ_ONLY / unchanged |
| `src/vego_hlayer/state_machine.py` | `df539df9ba50fefbdc75fe4e050c8039cbe2bf7da4049330589b0df76a55e42e` | READ_ONLY / unchanged |
| `tests/hlayer_offline/conftest.py` | `335518034ad1217ff7cb9281f77472aac23171c48e16a0045d3d56c4a43d19b0` | READ_ONLY / unchanged |
| `tests/hlayer_offline/test_contracts_and_state.py` | `752933b13f57458129a86f3a5952c7ddd375f83168f8dfd2684e20bd7f3c8c32` | READ_ONLY / unchanged |
| `tests/hlayer_offline/test_experiments.py` | `896008a18d25d97b15208656bf6b5f4a1adfa439c700e4bf68f9a2d9a4fb0ec5` | READ_ONLY / unchanged |
| `tests/hlayer_offline/test_io_safety.py` | `d8943de65697b6ecbe7af0aed8dc3446bd9a0c4eeb68882c8e4b6d3e638394c1` | READ_ONLY / unchanged |
| `tests/hlayer_offline/test_suite.py` | `62f382eb90a84e2de2cb457d5c9d1a6b00ef1da430d1cc8dcbeb85dd72c044ab` | READ_ONLY / unchanged |
| `tests/hlayer_offline/test_unified_runtime.py` | `6bb93211b1af17d0627b7ba2714207924b0bcfedecb0dca052f8c1dc0caade6a` | READ_ONLY / unchanged |
| `tests/hlayer_offline/test_validator.py` | `af72c50c18a3c75e2b70993c423fff097003d1905a31f2406e48e509fc6dee7b` | READ_ONLY / unchanged |

<!-- AIRTRAVEL_PACKET_V3
{
  "N": 4,
  "amendment_manifest_sha256": "bd2b7f03585582ff7591d21795fbd3ed4701244d66d26221683520238c2dead2",
  "base_sha": "c34d3954b5e080d090017d2ea655d454d75a6b92",
  "code_hashes": {
    "schemas/airtravel-fake-grant-v1.schema.json": "0f426c3f1d8c7791127481ba7714eb0e009fc4a2dcecfdfe7b7c5ca9ecdc396a",
    "schemas/airtravel-technical-receipt-v1.schema.json": "4a6ab510230e8288c5cd111c2796a8f24849c88db7808cbeaf30b74fe6a5060d",
    "schemas/qa-communication-event-v1.schema.json": "7df773a6a141a656b32012abd35c34aab25002f2a873c84e61c9ade06af670b2",
    "scripts/airtravel_execution_safety.py": "8c4cb6814311aee4d5b8a328aa117881daf3186bdcc6b86782f1b02a752bd203",
    "scripts/airtravel_local_observer.py": "e60db39e7ad52ac789372db592d91d2c9a3a81d8193c09346e39a09107e25228",
    "scripts/airtravel_preflight_contract.py": "f6bedbd904907656b0af929c0aa133481f6ad6f289ed4c8e9b913bb1a3dc6db8",
    "scripts/airtravel_preflight_execution.py": "879d7d99c33dddaf319527a85273d40a6402e9480bdeb65742c367623f5a2da9",
    "scripts/extract_qa_escalation_features.py": "8723f8f7cb75df51d5c82bda2b604bfaa2b72c230ce580090f7ba06cf3457974",
    "scripts/prepare_airtravel_protected_fake_preflight.py": "ec4c0aa4b948e4c5ee33244470da9d6a7b436ce85cc57c940fb4389a4024c997",
    "scripts/render_airtravel_results.py": "4174e114c1aa67f06f911d0377c0d18d0cdcce085965403ea9b846356d25da88",
    "scripts/study1_call_bound.py": "82d059aab17da87b9bd0c4d121b2daa7717c8b5167c68df2cddba4f72b96936c"
  },
  "corpus_id": "text2uml_airtravel_253b26dc",
  "correction_parent_sha": "3727acfe2130863ab6b737824a1718e7b3648b92",
  "implementation_commit": "28a1d95f39058e5b9dd3e7601584e2393311d405",
  "pr": 38,
  "protected_hashes": {
    "VEGO-AI/eval/README_EVALUATOR.md": "b24280599b799a121d4758f9d9eb81b1451cb9b178ce1c60fb0ebdfe9ac20832",
    "VEGO-AI/eval/agentA_language_evaluator.py": "de412e3ab42dc783c3fdd94dc6e42969c84d565b687277e2c359c2a0299a28cf",
    "VEGO-AI/eval/agentB_domain_evaluator.py": "26b299587fc54cd2a19bc0841aba6f9e322c253e3e0523ebc4f06c8f697feb8e",
    "VEGO-AI/eval/agentC_case_scorer.py": "27011d8569736601bc2f60a5510354024b7ff27a7aba350119c824a4adbaf2e8",
    "VEGO-AI/eval/agentD_variability_evaluator.py": "53b2cc4aae3a3cb4a903872359bbf60c060e7c62d03a15b3834b8f7db7503c14",
    "VEGO-AI/eval/eval_config.json": "87f35c96b5b67f4785ac0abd4d24cf100d5b499ba562f0683e5b644c90bc3f5e",
    "VEGO-AI/eval/evaluator.py": "ac5c5062e0275546154b9d526ab431a4a90cb68480c60f7d2060c14dd8a80b23",
    "VEGO-AI/framework/README.md": "d3035fa08cdc32bfc14d26c3b567ac901fc2fef87b4bdb15b74af0c483a0a825",
    "VEGO-AI/framework/agent1_language_advisor.py": "13e152fe4ec3b417a8c515bbe1bdb28ff952766579ce1ed6463a7ad9fa5b724e",
    "VEGO-AI/framework/agent2_domain_advisor.py": "fdf330b99295e871ad3cc3e5e934bb04a15f996a5060ea35d43fa13243d16d79",
    "VEGO-AI/framework/agent3_model_inspector.py": "4d0042777040f76abc1ca616a6e1dddcda591ddec54478fa2491b5020a817fa4",
    "VEGO-AI/framework/agent4_variability_explorer.py": "6b043c5643f9211d93ac402a9bf98685727e2cd92cab3377d1462dc3417df2ff",
    "VEGO-AI/framework/hlayer_architecture.py": "b978176b03f389c5017cc6bfdb3237a1c0b2c5ea9d76793f927963bf6d04bfd5",
    "VEGO-AI/framework/human_feedback_manager.py": "238e99d7bd652a0fde2884d8fd544c829dfbc8c66dddf404cd4b1eaef13e50e2",
    "VEGO-AI/framework/human_judgment_memory.py": "87cc7113452f366a254f946a92877bc069e1c75bfc2185bf267dfdc0f74dd976",
    "VEGO-AI/framework/human_review_queue.py": "499963663722cbb3892916df4a6e8d53ee5fdfab4876db3b2ef709100897944e",
    "VEGO-AI/framework/llm_client.py": "1a36b4ee860619db97a6ff84ecf64b4845a292ef67cf432c17a86eacd56f55da",
    "VEGO-AI/framework/memory_advisor.py": "143cefd87c3cbe51029b90f3f849384a4ee50df5d1d6e7f3394b2cb109c2e271",
    "VEGO-AI/framework/memory_informed_classifier.py": "41518916a5b7fcb243564a9b3d2fed83cfba584211a10ca2198ad16cb4414171",
    "VEGO-AI/framework/orchestrator.py": "fca4b885ee07381db0f02e558b1aebf25bdc7c27da1c471fd3103d7e0e2d5b88",
    "VEGO-AI/framework/qa_communication.py": "9f2cda1dc52fe919be22ac2ea42d61dce3ed22d3fae7ae27077b3db821594236",
    "VEGO-AI/framework/qa_instrumented_runner.py": "d187f8e8113a86caf24e55720e227f9a5f9b3466126969166bcefb83625a215f",
    "VEGO-AI/framework/qa_registry.py": "ab189d3fd954ea03ba891f5746b36eff8889baeff73d7594f820e68f8762ad5f",
    "VEGO-AI/framework/requirements.txt": "04f5965d2b72485f6c4fcc1c3a8e1fc1c3f5dae6641fb53e73fc04533b82c3cd",
    "VEGO-AI/framework/run_config.json": "c185879270a318a2b7c3920f4a9c49c6be6ae807afe33eddb4d4577fd9603794",
    "VEGO-AI/framework/selective_intervention_policy.py": "b43e18225e5ff03de29b9e69f1436de93ace23ddc3a2c0c1a4a72fd1fe518aff",
    "VEGO-AI/framework/state.py": "d8492a623804065b86905d6183979c322d6f83376bf91026e718c615eea1730d",
    "VEGO-AI/inputs/README.md": "78bf44ccc63fea7693f492416d7ee0f6fdebfa3771a04be2fe0935ff7e6e2e89",
    "VEGO-AI/inputs/ch/domain_description.txt": "fda75e2cc9dbbfb9c74df5d567edb40a00aba3bcb4819079321acc8c9fb7538b",
    "VEGO-AI/inputs/ch/domain_description_cd.txt": "172f461fa0fa9c9b3b64e81adbee91a708dcd59316eb88ec8a2b498d6f3ffca9",
    "VEGO-AI/inputs/ch/domain_description_ucd.txt": "5e5da0ae931ca2f3db509fc8476b314f604fc2c639b212957576f5db8285eace",
    "VEGO-AI/inputs/human_feedback.example.jsonl": "9d2fd7cfd17e892e8bf161f15c19eeb51db6d9c3d2897dc5b1ac2dbde629d6f0",
    "VEGO-AI/inputs/language_base_cd.txt": "8247f4e4e19aed2198937969babaf7309efa1a6c66b665c556f9ad20e10003da",
    "VEGO-AI/inputs/language_base_ucd.txt": "53d79578c30ad8e898d2773858036775c7bcfefd8c5d7e63744f062bd99528d8",
    "VEGO-AI/inputs/pw/domain_base_cd.txt": "251dfd4d7526942b858679a5e54d16160eb2ea206bb2ed8a6ca3aeebb62cfe4f",
    "VEGO-AI/inputs/pw/domain_base_ucd.txt": "4720627b6e5e8ec172d4b2922af972c17e761c8786dade2ec278ce4c964d3165",
    "VEGO-AI/inputs/pw/domain_description.txt": "f4c43ff8c928294f9bde20e539c072ecae6dd564d038aeb0c9dd658fd543340b",
    "VEGO-AI/inputs/scoring_schema.txt": "b0911d3921eeabdee7f93802cbf56a6d2b32a20e8e3a470ee7fc6709686ab506",
    "VEGO-AI/schemas/README.md": "b3f629801ef4fbb6148ed9554ff003d8f7e07e709000229aa2ad61906ae715b9",
    "VEGO-AI/schemas/human_feedback.schema.json": "170561aa00aff11fa264084383488618d6acc87f4e8fb69141def6985e26f2d7",
    "VEGO-AI/schemas/human_judgment.schema.json": "2d28a9a5c2100cfe30b6e2e14f1780cf84518f7f8dacd344ac8d465911b4c1ad",
    "VEGO-AI/schemas/human_review_item.schema.json": "1f3d0f74c624abfbfa8e8eda0600ceb1403e4e68426f9bb779e07e00265f4603",
    "VEGO-AI/schemas/memory_advice.schema.json": "59240d67aac0cdc6236d0fe85cc757d123e4b446d127fa0c970004f3ef5c5024",
    "VEGO-AI/schemas/memory_informed_comparison.schema.json": "d14af2b67940ec4f40957ddafad30dad2134355cd6f0ec94a6fe0b82f9069ade",
    "VEGO-AI/schemas/results_dashboard_snapshot.schema.json": "04e128eb9abca49a60edb809f2600c40c39e162c14166c31b4a0c30e9cfffcf5",
    "VEGO-AI/tests/README.md": "36f180bdee118cf4157c0faa0458464d16770c41a392dfa22129fb6b659ff49f",
    "VEGO-AI/tests/test_accuracy_improvement_analysis.py": "6dcdb87f71d231cc2580171b830eeb66d93e2735a5351912464be2a8ce700a7b",
    "VEGO-AI/tests/test_human_feedback_manager.py": "39538c746498791307a433153105dc950332e8b577a5b4b1acea73699c276832",
    "VEGO-AI/tests/test_human_judgment_memory.py": "5f28d27c567984ef0d196ec5b2d58d3dc2158a4db4539cd4cdfefee3c990f7ee",
    "VEGO-AI/tests/test_human_review_queue.py": "58f1a8ae340a03f99d1a1948fad7cadcfb01c53f4b5ede06c27014695b5a6329",
    "VEGO-AI/tests/test_llm_client_security.py": "9349a6c61ba77e6c736fcc3757f3a27d07b42429cbbe8bd503ddc0ab19ea97d2",
    "VEGO-AI/tests/test_memory_advisor.py": "6dbb6609cf10f45ebbf344e8b5448fe0eb3019c71c0aea5d7845d05053782745",
    "VEGO-AI/tests/test_memory_informed_classifier.py": "0067b3cc4b4f6d866b15e5b730da83f17c6f13069239c0aa41e749004e0e52e9",
    "VEGO-AI/tests/test_qa_communication.py": "ebd8b6dd133a617063f104056e6bce61310306ba0ba0a74e83abd4b8335b3c2d",
    "VEGO-AI/tests/test_qa_instrumented_runner.py": "4e6c88fec0802a7caae67bf77a37d07384014330b9646478bc795f6ebbfe7c7f",
    "VEGO-AI/tests/test_results_dashboard.py": "35f7109f36a934b7c780e422a1284a36fac368ab0eb1301f82c66deb31663e18",
    "VEGO-AI/tests/test_visualizer_helpers.py": "d0ca91f1b175d1af843f7ea4e77b907530e029454ad3df75d619893289eb34c0",
    "scripts/hlayer_offline/__init__.py": "25dc6d2880f9a3aa28ba291bb6286f0db592a4a2d870c4deac98079a82e580bf",
    "scripts/hlayer_offline/common.py": "04be8da46aa7675739626b86f5782e113cdcf8b7fb51765bc182f6497007b835",
    "scripts/hlayer_offline/contracts.py": "4f2b711246682f09a6348b0217f1c4e4b5dca53450382e92e1d80fc345b99529",
    "scripts/hlayer_offline/exp013.py": "392f00b8ca9dfd538f628a825b2f234974f1d832fc25d79252bb2fa881faa267",
    "scripts/hlayer_offline/exp014.py": "b0453e107cb814606881472d95af1cba28767900b1d44d4a55165c2af4ff1c7e",
    "scripts/hlayer_offline/exp015.py": "a223f3a7beaa50c54fe1f846f03465ed77868038eecb2c1ad1d717785f8438fa",
    "scripts/hlayer_offline/exp016.py": "aa1070596c0f86630cde884934f722a8e6ba1ed0f140caf3eef3ae69577709b0",
    "scripts/hlayer_offline/exp017.py": "88092e489653a6286fecf820859f557f6826ae484aa04cb35fe79282980efbed",
    "scripts/hlayer_offline/exp018.py": "571fcb5ca26b1c52d92554b77bd03405445fbbb79a769c61b86ab6d2060c30f9",
    "scripts/hlayer_offline/legacy_replay_adapter.py": "8861b64a154e6c727f54770b5f6cafdf3b8bb6c9ff986c8a9ee36693af9428e3",
    "scripts/hlayer_offline/state_machine.py": "54d15af6e457b85fe81ce2eae4c2948329c3db3fd5ab2c6991ec0a9ae4c5866e",
    "scripts/hlayer_offline/suite.py": "ffbe787a8a1e53aee7bb64657d8863c7e3a9c4f025b5e0fd1e7372ab5cfe3c1f",
    "scripts/hlayer_offline/validator.py": "c6d166504b6847b6d3d6bb80654e4905cad112eff7091f4a4a463bd22e903876",
    "src/vego_hlayer/__init__.py": "7a10cd95ea118da0848e0b61a3ddd164ad49462c7f5328828d84b60780b16d3f",
    "src/vego_hlayer/adapters.py": "6d97a5aaa288d30781dca80d320cea8cb47f8d95f53b655f45496748a31657df",
    "src/vego_hlayer/contracts.py": "97881676db22c28cb9a8a3e45a57f1555e213f1f8849c8f9196b768f3cc6075b",
    "src/vego_hlayer/io_safety.py": "c7ee7eab05c0c79b8e4196de51f345bcef72a81da4de667fddfefb304089b1cb",
    "src/vego_hlayer/runtime.py": "bd285dafcda15ef34ebcbcfd465461bcb19ca28c9c59182e0749112e4c7880ec",
    "src/vego_hlayer/state_machine.py": "df539df9ba50fefbdc75fe4e050c8039cbe2bf7da4049330589b0df76a55e42e",
    "tests/hlayer_offline/conftest.py": "335518034ad1217ff7cb9281f77472aac23171c48e16a0045d3d56c4a43d19b0",
    "tests/hlayer_offline/test_contracts_and_state.py": "752933b13f57458129a86f3a5952c7ddd375f83168f8dfd2684e20bd7f3c8c32",
    "tests/hlayer_offline/test_experiments.py": "896008a18d25d97b15208656bf6b5f4a1adfa439c700e4bf68f9a2d9a4fb0ec5",
    "tests/hlayer_offline/test_io_safety.py": "d8943de65697b6ecbe7af0aed8dc3446bd9a0c4eeb68882c8e4b6d3e638394c1",
    "tests/hlayer_offline/test_suite.py": "62f382eb90a84e2de2cb457d5c9d1a6b00ef1da430d1cc8dcbeb85dd72c044ab",
    "tests/hlayer_offline/test_unified_runtime.py": "6bb93211b1af17d0627b7ba2714207924b0bcfedecb0dca052f8c1dc0caade6a",
    "tests/hlayer_offline/test_validator.py": "af72c50c18a3c75e2b70993c423fff097003d1905a31f2406e48e509fc6dee7b"
  },
  "runtime_archive_sha256": "e37baecd20a0c84eb1d9b87b3b78a23bc4b4eb8a9824ad3086dc30aa35fdd31f",
  "runtime_files": {
    "candidate_models/01_result_one_claude-sonnet-4-6.txt": {
      "bytes": 1248,
      "sha256": "240b034834e383b9844e9a3e9796f6be9b3d47fc95de6606ed022d278d751f91"
    },
    "candidate_models/02_result_one_codestral-2508.txt": {
      "bytes": 1272,
      "sha256": "08399ca9432c1399f3f9784d34741314e4d39e40307a6efb14fa92a1c138b1d6"
    },
    "candidate_models/03_result_one_deepseek-chat.txt": {
      "bytes": 1324,
      "sha256": "ee4d689d59c9ce3a5e8ff385747641954bd4821f2efeb18e581dcd1d5441d20a"
    },
    "candidate_models/04_result_one_gemini-2.5-flash.txt": {
      "bytes": 1231,
      "sha256": "1c3d15eac71fcaab138857dbbc7153833b3df55ab57925ac756a79dc28dc847a"
    },
    "domain_description/description.md": {
      "bytes": 1477,
      "sha256": "96bc8a6fbf2c2fdd93592fdbf6fac7c2b9db403494fe2d5a45e0a2bcbf0167e2"
    }
  },
  "setting_id": "cd_airtravel",
  "status": "AUTHORIZATION_REQUESTED_NOT_GRANTED"
}
-->
