# Protected authorization packet — Text2UML/AirTravel v1.0.2

**Authorization state: NOT AUTHORIZED.** This packet requests a human decision;
it is not an authorization record and does not permit a provider call.

## Scope requested

After the v1.0.2 amendment is supplied and verified, authorize one bounded,
provider-backed AirTravel feasibility run using the exact frozen `setting_id`
and `corpus_id`, the amendment-selected runtime files, and the pre-registered
offline instrumentation. No student material, reference model, private URL,
or human ground-truth claim is in scope. Expiry requested: **24 hours after
issuance**, or earlier on any manifest/configuration drift. API cost remains
**TO BE MEASURED**.

## Hash-bound evidence

- Base SHA before this receipt: `ed37d77ccad6022185cd73e539d63abd11ca290b`.
- Proposed head SHA: `a7d06a93529174d400fb0611c47ef8ee1d0eeb0b`; a human must
  verify it before authorizing.
- Upstream Text2UML commit: `253b26dc704d523209a5cba79686f8f7fab57d63`.
- Input manifest: `source-manifest.json` SHA-256
  `f13f4172f05422971c3d049d9be672b5befb9f49a1ab5f4589dda3587aa2910c`.
- Configuration: `vego-ai-config-airtravel.json` SHA-256
  `09e6400e6cf36c19614ceafbd3233ad2f58c4353d66845affd379a258c4a3d5f`.

Observed runtime bytes (not yet v1.0.2-authoritative):

| Relative file | Bytes | SHA-256 |
|---|---:|---|
| `runtime_input/domain_description/description.md` | 1,477 | `96bc8a6fbf2c2fdd93592fdbf6fac7c2b9db403494fe2d5a45e0a2bcbf0167e2` |
| `runtime_input/candidate_models/01_result_one_claude-sonnet-4-6.txt` | 1,248 | `240b034834e383b9844e9a3e9796f6be9b3d47fc95de6606ed022d278d751f91` |
| `runtime_input/candidate_models/02_result_one_codestral-2508.txt` | 1,272 | `08399ca9432c1399f3f9784d34741314e4d39e40307a6efb14fa92a1c138b1d6` |
| `runtime_input/candidate_models/03_result_one_deepseek-chat.txt` | 1,324 | `ee4d689d59c9ce3a5e8ff385747641954bd4821f2efeb18e581dcd1d5441d20a` |
| `runtime_input/candidate_models/04_result_one_gemini-2.5-flash.txt` | 1,231 | `1c3d15eac71fcaab138857dbbc7153833b3df55ab57925ac756a79dc28dc847a` |
| `source_metadata/LICENSE` | 35,149 | `3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986` |

## Scientific justification and risk

The pack is a public Text2UML/AirTravel UML-class-diagram feasibility setting,
not a student corpus, human-intervention ground truth, or accuracy benchmark.
The run can test only instrumentation and descriptive candidate-escalation
observability. Risks include amendment/hash drift, accidental reference
exposure, provider cost, and overclaiming from a four-case external pilot.
The default-deny provider flag, reference-only directory, stable IDs, and
fail-closed verifier mitigate these risks; human review remains mandatory.

## Missing authorization inputs

Claude v1.0.2 commit and byte-level amendment manifest are not present. The
owner must attach them, verify the proposed head SHA, confirm the exact N and
call bound, and sign/record authorization with an expiry before any provider
operation.
