# Case-Selection Receipt

Run `S2P-LIVE-20260908T192135Z`. Frame: complete eligible population, not a sample. Corpus `text2uml_airtravel_253b26dc` @ `253b26dc704d523209a5cba79686f8f7fab57d63`; archive SHA-256 `8cf82e2ab2d2ce3da9a7ec4165e760ae1e0d9af14468f5aa2a3883037d8da701`.

- Eligibility predicate: classification=GENERATED_CANDIDATE_MODEL and path starts result_one_ and bytes>0 and syntax_validation=WRAPPER_PRESENT and sha256 is 64 hex
- Eligible cases: 21
- Selection rule: `sorted(random.Random(seed).sample(sorted(eligible_case_ids), sample_size)); executed once before any provider output was observed; no substitution afterwards`
- Seed: 20260908; sample size: 12
- Selected: 01, 02, 03, 05, 06, 07, 08, 12, 15, 18, 20, 21
- Excluded (not drawn by the seeded sample under the frozen cost bound): 04, 09, 10, 11, 13, 14, 16, 17, 19
- Overlap with Study 1 by digest (full-frame id -> Study 1 id): {'03': '01', '06': '03', '07': '04'}
- Gate `selection_reproduced_from_seed`: True
- Gate `corpus_hashes_verified_at_load`: True

| Case | Source generator model | Bytes | SHA-256 | Selected |
|---|---|---|---|---|
| 01 | Qwen_Qwen2.5-3B-Instruct | 1686 | 2a7de3f3aad9ce230d0bda92f3660e8f403ef2c79447ff80262b5ab052865093 | yes |
| 02 | Qwen_Qwen3.5-4B | 1096 | 83f4f2c7d481a13b2fe3c805531213199e0245e7b86a41ab959eeac98e69a57f | yes |
| 03 | claude-sonnet-4-6 | 1248 | 240b034834e383b9844e9a3e9796f6be9b3d47fc95de6606ed022d278d751f91 | yes |
| 04 | codestral-2508 | 1272 | 08399ca9432c1399f3f9784d34741314e4d39e40307a6efb14fa92a1c138b1d6 | no |
| 05 | deepseek-ai_DeepSeek-R1-Distill-Qwen-7B | 10461 | 786fa79f56dea0e3af5d0c4df0c18838fe88f20615a155949b7c04faec3ffea5 | yes |
| 06 | deepseek-chat | 1324 | ee4d689d59c9ce3a5e8ff385747641954bd4821f2efeb18e581dcd1d5441d20a | yes |
| 07 | gemini-2.5-flash | 1231 | 1c3d15eac71fcaab138857dbbc7153833b3df55ab57925ac756a79dc28dc847a | yes |
| 08 | google_gemma-3-4b-it | 7042 | b72fc5eaa682ce27912086dd2dcb3ea192c7fbe14285457cdcea23b0b6222f0b | yes |
| 09 | gpt-3.5-turbo | 1255 | 81abd4b6b848b9e9102418d023d2af4656931fe162358f336f6132ab11a817c5 | no |
| 10 | gpt-4o-mini | 1240 | 49e3989e341eba1414f6366b50d12b946ab3ceb16884e8faf1c0f6945ea8d4e9 | no |
| 11 | gpt-5-mini | 1299 | 4590b62dc0ea047e9a7789739a6482b5221e0deaa0fd5dc8004643863911ba36 | no |
| 12 | gpt-5-nano | 1185 | 6fad455a7d4831a5baba0cb7f4336f24fa338f4cd0c14f02236305664aebdfab | yes |
| 13 | gpt-5.2 | 1288 | 559769d3653cd690966e7873a5647da7834532148fa4ec64ee34e3bc8e056d18 | no |
| 14 | meta-llama_Llama-3.2-3B-Instruct | 7161 | 7e65f088e45f47a1eb0c39c7b1e70eb05b77ec6a6836e9454f89babf81bba26e | no |
| 15 | microsoft_Phi-4-mini-instruct | 7466 | 06ea010da3a8e4f21e38a4cb5c3b279cc036d3f0a1af5e15f8363efad5e4a36f | yes |
| 16 | microsoft_phi-4 | 1327 | 9d1a6cb2d9113e0425d0a69d8dd483cb403b0db89c2052cd621fd4728373248a | no |
| 17 | mistral-large-2411 | 1255 | 70ccdd6576d3c15d3215b946b23cf1ed0c40d463a05a7a4fbe0956f27dfba266 | no |
| 18 | mistral-small-2506 | 1208 | 77cdd113ce541a0bfffed798cbbfe3000d92d23fca88e41a344806373d551b1e | yes |
| 19 | mistralai_Mistral-7B-Instruct-v0.3 | 7182 | 3d8bb9c8564e086f0ba9e948b101def6c1fb50eefb1f2d20d71e591a491b1819 | no |
| 20 | o3-mini | 1207 | a844ee45eb8a4fd15a798ad0c67d7c654479dafdd53a80f270d14b2e0129232a | yes |
| 21 | tiiuae_Falcon-H1-7B-Instruct | 1177 | 7e3fccfff40f578aa80ab5aec866e5842bae6009cc4c8fd6c580f90a5f623d35 | yes |
