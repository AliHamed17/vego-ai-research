# Q&A Escalation Signal Preregistration — v1.0.2 Amendment: Text2UML/AirTravel Setting

## 0. Amendment header

**Version: v1.0.2. Amendment type: PRE-DATA SCOPE EXTENSION. Data exposure before this amendment: NONE.**

**Parent document:** `docs/research/phd-proposal/2026-09-04-qa-escalation-signal-preregistration.md`, version v1.0.1,
committed at `917f1089b4e8d19fdc39d5f80a59e3663ab664cd`. Per that document's own §16 ("This document is not
amended in place for such changes; a dated addendum or successor section records them."), this amendment is
a **separate successor document**. Not one line of the v1.0.1 file is modified by this amendment; its full
text, including its own §0 revision block, remains in force unchanged.

**`audit_base_sha` (the `main` commit this document was authored/last rebased against — a fixed historical
reference point, never this commit's own hash):** `cbc2fb5e3c05471cf37c0eef55a48857e2066403`. This field is
deliberately named to avoid the self-reference defect found in the historical-case-recovery-v3 audit's
"Current main" field (commit `cbc2fb5`, which records its own parent `fbd7541` rather than itself — a commit
cannot contain its own resulting hash, since editing the field changes the commit). No provider run, no
Detector-v1 result, and no VEGO-AI experimental output was inspected before or during the authoring of this
amendment.

**Rebase history (unpushed until this freeze):** originally authored against `2d38e378` (`ff0a61a`); rebased
against `36602e41a3a7ccec52a300d9244f3afe4702153f` (`91ccee4`); rebased again against `cbc2fb5e3c05471cf37c0eef55a48857e2066403`
(this commit), after independently re-verifying that no intervening commit touches any AirTravel path, this
document, or v1.0.1. No content in this amendment changed at either rebase beyond this header — the
intervening historical-case-recovery work is a wholly separate track (Cheers/ParkWise byte recovery),
adjudicated on its own terms elsewhere, and does not alter anything frozen below. Confirmed independently:
historical-inventory issues in that track, including the case-`68065` cross-directory content swap, do not
block or bear on this AirTravel feasibility setting in any way — the two tracks share no data, code path, or
identifier.

**Dataset-choice, approval, and execution-authorization record (frozen at this freeze):**

| Field | Value |
|---|---|
| Dataset choice | `USER_AUTHORIZED_PUBLIC_EXTERNAL_FEASIBILITY` — Ali authorized `cd_airtravel` as a public-external feasibility setting; this is documented user authorization for that dataset choice only |
| Supervisor approval | `NOT_DOCUMENTED` — no exact Iris/Arnon wording approving this setting, candidate selection, or any run has been supplied |
| Paid provider execution | `NOT_AUTHORIZED` — this record authorizes neither spend nor a provider call; that remains a separate, explicit decision |

**Scope of this amendment.** v1.0.1 governs four settings — `ucd_pw`, `cd_pw`, `ucd_ch`, `cd_ch` — all
reported `BLOCKED` on missing historical case-model inputs (v1.0.1 §8). This amendment adds exactly one new
setting, `cd_airtravel`, built on a public external dataset, without touching v1.0.1's policy for the four
historical settings, its Detector-v1 definition, or any threshold. It is not a correction of a v1.0.1 defect
(contrast with the v1.0.0→v1.0.1 revision) and is not a post-data change under v1.0.1 §16 — no data exposure
of any kind has occurred for either the historical settings or this new setting.

## 1. Relationship to the prior 178-case synthetic corpus

The wholesale 178-case synthetic Cheers/ParkWise replacement corpus prepared in an earlier session turn
(local branch `study1/synthetic-corpus`, commits `aa82290`/`535d353`, confirmed unpushed) is **explicitly
outside this amendment's scope**. It is quarantined: not approved, not referenced by this amendment's
`cd_airtravel` setting, and prohibited from any runtime input path this amendment defines. Its own
disposition — a slot-by-slot historical recovery audit, followed by a decision on whether any of its files
may be reclassified as legitimate gap-fill for a specifically confirmed-missing slot — remains open and is
not resolved by this document.

## 2. Correction to prior provenance-policy statements

Two statements made in this session's earlier provenance-policy adjudication (never committed to any
tracked file) are corrected here, in force from this point forward for all subsequent work in this project:

1. **"MISSING" was stated too absolutely.** An absence-of-recovery finding cannot prove that no copy exists
   anywhere; it can only report that a declared search scope was checked on a declared date and nothing was
   found there. Going forward, "MISSING" is replaced by **`SEARCHED_NOT_FOUND_WITHIN_DECLARED_SCOPE`**,
   always recorded together with the exact scope searched and the audit date. Synthesis for a slot becomes
   eligible only after (a) the expected slot itself is established (its setting, position, and what it was
   supposed to contain) and (b) the owner accepts the search as closed for that slot. No slot in this
   amendment relies on this term — `cd_airtravel` is a new setting, not a recovery attempt for a historical
   slot — but the corrected term governs any future Cheers/ParkWise recovery-audit work.
2. **"Public external is never empirical" was stated too broadly and is withdrawn.** A real, provider-backed
   VEGO-AI run on the AirTravel corpus, if one is ever authorized and executed, would be genuine empirical
   evidence about VEGO-AI's own behavior on that specific external corpus. It would remain, and could never
   become, evidence about real students, the historical Cheers/ParkWise corpus, alert correctness, or human
   benefit. §7 and §8 below state the corrected boundary precisely.

Two further provenance-policy corrections apply project-wide from this point:
`ORIGINAL_VERIFIED` provenance is not unconditionally admissible to historical-data analysis — it still
requires exact setting binding, integrity verification, lawful/ethical-use clearance, and evidence that the
artifact belongs to the actual evaluated input set, not merely a plausible match. `PUBLIC_EXTERNAL` is not
synonymous with human authorship; §4 below assigns the AirTravel candidates their own, separate
authorship/process classification rather than leaving that implication open.

## 3. Frozen dataset identity

| Field | Frozen value |
|---|---|
| `setting_id` | `cd_airtravel` |
| `corpus_id` | `text2uml_airtravel_253b26dc` |
| Upstream repository | `https://github.com/IlKaiser/text2uml` |
| Upstream scenario path | `dataset/AirTravel` |
| Pinned upstream commit | `253b26dc704d523209a5cba79686f8f7fab57d63` |
| Declared license | `GPL-3.0`. **Scope stated precisely, not inferred:** the project's own license-attribution receipt states redistribution/attribution review is required before *source publication*; it does not itself establish that GPL-3.0 review blocks a private, unpublished local execution. No document available to the author of this amendment asserts a broader restriction, and none is invented here — if a broader restriction exists, it must be documented before being enforced as such. |
| Acquisition/staging date | 2026-09-04 (per the preparation pack committed in `ed37d77`) |
| **Technical readiness** | **`TECHNICAL NO-GO`**, not conditional-GO — see the complete blocker list in §11. |

`setting_id` and `corpus_id` are distinct fields by design (per this project's identity model): `setting_id`
names the language/domain configuration axis; `corpus_id` names the data-generating process. Neither may be
renamed to, nor pooled under, any of the four historical `setting_id` values.

## 4. Exact runtime manifest and authorship/process classification

All values below were cross-checked across five independently authored sources on `main` at
`2d38e378`: `source-manifest.json`, `airtravel-inventory.json`, `staging-hash-check.json`,
`2026-09-04-airtravel-v102-pre-run-technical-gate.md`, and
`2026-09-04-airtravel-v102-protected-authorization-packet.md`. All five agree exactly with each other and
with the values supplied for this amendment. **This is cross-document consistency, not source-byte
verification, and it must not be described as the latter.** The actual downloaded external bytes (expected
under `external_data/text2uml/253b26dc.../...`) are not present anywhere in this checkout — confirmed absent
by direct filesystem search. **Actual verification of these bytes against the live Text2UML upstream commit
remains an open Codex dependency**, not something this amendment or its cross-document check discharges. No
disagreement was found among the five documents checked, which is the only claim made here.

**Domain description (runtime-visible):**

| Path | Bytes | SHA-256 |
|---|---:|---|
| `domain_description/description.md` | 1,477 | `96bc8a6fbf2c2fdd93592fdbf6fac7c2b9db403494fe2d5a45e0a2bcbf0167e2` |

**Selected candidates, N=4 (runtime-visible):**

| Path | Bytes | SHA-256 |
|---|---:|---|
| `candidate_models/01_result_one_claude-sonnet-4-6.txt` | 1,248 | `240b034834e383b9844e9a3e9796f6be9b3d47fc95de6606ed022d278d751f91` |
| `candidate_models/02_result_one_codestral-2508.txt` | 1,272 | `08399ca9432c1399f3f9784d34741314e4d39e40307a6efb14fa92a1c138b1d6` |
| `candidate_models/03_result_one_deepseek-chat.txt` | 1,324 | `ee4d689d59c9ce3a5e8ff385747641954bd4821f2efeb18e581dcd1d5441d20a` |
| `candidate_models/04_result_one_gemini-2.5-flash.txt` | 1,231 | `1c3d15eac71fcaab138857dbbc7153833b3df55ab57925ac756a79dc28dc847a` |

**Exact source-to-runtime mapping.** `source_path` is the file's path inside the Text2UML repository's
`dataset/AirTravel` directory at the pinned commit, as recorded by `source-manifest.json`; `runtime_path` is
its relocated path under this setting's runtime input tree. The rename/relocation is filesystem identity
only, required by the protected loader's directory-and-numbering convention — **it does not, and must not,
change any file's bytes.** This mapping is a documentation cross-reference, not itself proof that the
`source_path` bytes match the live upstream repository (see the verification-tier limitation above).

| `source_path` (in `dataset/AirTravel`) | `runtime_path` | Bytes | SHA-256 | `transformation` | `byte_transformation` |
|---|---|---:|---|---|---|
| `description.md` | `domain_description/description.md` | 1,477 | `96bc8a6fbf2c2fdd93592fdbf6fac7c2b9db403494fe2d5a45e0a2bcbf0167e2` | `BYTE_IDENTICAL_RELOCATION` | `NONE` |
| `result_one_claude-sonnet-4-6.txt` | `candidate_models/01_result_one_claude-sonnet-4-6.txt` | 1,248 | `240b034834e383b9844e9a3e9796f6be9b3d47fc95de6606ed022d278d751f91` | `BYTE_IDENTICAL_RELOCATION_AND_CASE_ID_PREFIX` | `NONE` |
| `result_one_codestral-2508.txt` | `candidate_models/02_result_one_codestral-2508.txt` | 1,272 | `08399ca9432c1399f3f9784d34741314e4d39e40307a6efb14fa92a1c138b1d6` | `BYTE_IDENTICAL_RELOCATION_AND_CASE_ID_PREFIX` | `NONE` |
| `result_one_deepseek-chat.txt` | `candidate_models/03_result_one_deepseek-chat.txt` | 1,324 | `ee4d689d59c9ce3a5e8ff385747641954bd4821f2efeb18e581dcd1d5441d20a` | `BYTE_IDENTICAL_RELOCATION_AND_CASE_ID_PREFIX` | `NONE` |
| `result_one_gemini-2.5-flash.txt` | `candidate_models/04_result_one_gemini-2.5-flash.txt` | 1,231 | `1c3d15eac71fcaab138857dbbc7153833b3df55ab57925ac756a79dc28dc847a` | `BYTE_IDENTICAL_RELOCATION_AND_CASE_ID_PREFIX` | `NONE` |

Note the label correction from an earlier turn: the description file receives no filename prefix (only
directory relocation), so its `transformation` is `BYTE_IDENTICAL_RELOCATION`, not the candidates' compound
label. `byte_transformation: NONE` is stated explicitly for all five rows: no row's file bytes are altered
by this relocation, regardless of which `transformation` label applies to its path/filename.

`source_path` values for the four candidates are taken directly from `source-manifest.json`'s recorded
`path` field for each (classification `GENERATED_CANDIDATE_MODEL`, `source: "Text2UML pinned upstream
commit"`); the `description.md` mapping is taken from the same manifest's `DOMAIN_DESCRIPTION_CANDIDATE`
entry. The hashes in this table are unchanged from, and identical to, those already frozen above — the
mapping documents *where* each byte-identical file came from, it does not introduce a second, independent
hash computation.

Selection basis (frozen, matches `candidate-subset-proposal.md`): filename/documented output provenance
only — one-shot, non-empty, non-stripped, mutually distinct-hash outputs. Selection did not use, and may
never retroactively be justified by, candidate quality, similarity to any reference, expected Q&A volume,
expected alert rate, desired outcome, or any VEGO-AI/Detector-v1 output — none of which existed at the time
of selection.

**Authorship/process classification (correcting §2's `PUBLIC_EXTERNAL`-only framing):** each of the four
candidates is classified jointly as **`PUBLIC_EXTERNAL` + `EXTERNAL_LLM_GENERATED`**. They are outputs of
named external LLM systems (per their filenames) applied to the AirTravel scenario text, sourced from a
public repository. They are **not** human-authored, **not** student submissions, and **not** independent
statistical observations — cross-candidate independence is **not assumed**, since all four responded to the
identical scenario prompt under an unknown and possibly shared upstream generation protocol. They may serve
only as case models for instrumentation-feasibility purposes (§7); they may never be treated as human,
student, or correctness-ground-truth evidence.

**Sample characterization:** N=4 is an **exact pre-data purposive feasibility sample**, frozen for its
structural diversity across distinct model families, not for statistical representativeness. It licenses no
population-level inference of any kind.

## 5. Excluded references

The following are excluded from every runtime input path and are never supplied to VEGO-AI:

| Path | Bytes | SHA-256 | Classification |
|---|---:|---|---|
| `reference_only/plantuml.txt` | 1,300 | `01448d859c916a4229a2becec2e3675614ab6f00495d9049ace30b7c82bb7b98` | `REFERENCE_MODEL` |
| `reference_only/plantuml_adjusted.txt` | 1,328 | `17c4179653fcfea5b2bfd306cb1382d1b93bc5dc946419f85e8fc5e4b480f3ff` | `DERIVED_DUPLICATE` (of `plantuml.txt`; retained for provenance, never treated as a second independent reference) |
| `reference_only/extramaterial/AirTravel.cd4a` | 1,452 | `51a73df36663ab70e251e365266cc51d9a3f2c41ddf2dcf2a3cc106246ce61df` | `REFERENCE_MODEL` |

References are entirely provider-invisible and excluded from Detector-v1 in full: they are never passed to
the orchestrator, never used to grade a candidate, and never used to label a Detector-v1 alert true or
false. Any future study comparing candidates against these references requires its own, separately
preregistered amendment; it is not authorized by this document.

## 6. Denominators — no combined scientific denominator

Historical/recovered data (v1.0.1's four settings, whatever provenance tier they eventually clear),
`SYNTHETIC_GAP_FILL` data, and this amendment's `PUBLIC_EXTERNAL`/`EXTERNAL_LLM_GENERATED` AirTravel data
have **completely separate scientific denominators**, always. No table, figure, or count in any report
arising from this amendment may define a scientific denominator that sums across these three; the only
permitted cross-source number is an explicitly labeled **"operational throughput"** count (e.g., "N
candidate files executed across all currently prepared settings this run"), which carries no scientific
interpretation and appears only alongside, never in place of, the separated denominators. Within
`cd_airtravel` itself, the standard v1.0.1 §9 denominators apply unchanged: complete episodes
(`CONVERGED` + `TERMINATED_MAX_ROUNDS`), `INCOMPLETE_TECHNICAL` episodes (reported separately), and
partial-technical-success episodes (reported separately, named field missing).

## 7. Detector-v1 — unchanged

No threshold, tier, or signal admission from v1.0.1 §5/§6 is altered by this amendment:

```
STRONG_ALERT = S1_LOW_CONFIDENCE OR S3_MISSING_EVIDENCE OR S7_NON_CONVERGENCE
WEAK_ALERT   = NOT STRONG_ALERT AND (S2_MEDIUM_CONFIDENCE OR S6_MULTI_ROUND)
NO_ALERT     = neither tier fired
INCOMPLETE_TECHNICAL episodes are excluded from all three, reported as separate technical missingness.
```

C1 (`mapping_certainty < 0.7`), S5 (repeated clarification), S8 (follow-up), and S9 (question density)
remain non-triggering / contextual-only / exploratory, exactly as fixed in v1.0.1 §5–§7. Applying this
detector to `cd_airtravel` requires the same live-instrumentation prerequisites already listed as blocking
in v1.0.1 §15 (episode termination genuinely derived from orchestrator control flow, `round_index` parsed
from the call label, `case_id` included in episode identity) — this amendment freezes the dataset; it does
not assert those prerequisites are met.

## 8. Allowed and forbidden claims

**Allowed:** empirical observation of VEGO-AI's own Q&A communication, episode structure, and Detector-v1
classification, specifically and only on this exact `cd_airtravel` / `text2uml_airtravel_253b26dc` corpus,
once a run is authorized and executed. This is genuine empirical evidence about VEGO-AI's behavior on this
external corpus (§2 correction), reported with its exact N and denominator per §6.

**Forbidden:** any claim about real students; any claim about the historical Cheers/ParkWise corpus or its
representativeness; any claim that this corpus reproduces or estimates the historical population; alert
correctness (true/false alerts); accuracy, precision, recall, or F1; generalization to real educational
data; human benefit or intervention effectiveness; treating any candidate as an independent human or
statistical observation; any claim before a provider run is actually authorized and executed.

## 9. Zero-Q&A handling

A `cd_airtravel` run producing zero Q&A episodes is a **valid, reportable scientific result** under v1.0.1
§9's `VALID ZERO-Q&A RUN` criterion — not a failure, not an instrumentation defect, and not a reason to
retry. It must be reported as such and the process must stop there. **It does not trigger an
outcome-dependent fallback**: no fallback setting, corpus, or expanded run may be selected in response to a
zero-Q&A result, or to any other observed AirTravel result — consistent with v1.0.1 §10.D and with this
amendment's own §4 sample characterization, which forecloses any outcome-dependent justification for
expansion.

## 10. Supervisor-approval status

**NOT DOCUMENTED.** No evidence available to the author of this amendment records that Iris or Arnon has
approved the AirTravel setting, its candidate selection, or a provider run against it, specifically. This
amendment does not state or imply such approval; it is a pre-data scientific freeze only, produced by the
methodological lead, and remains subject to the same supervisor review as any other artifact in this
project.

## 11. What this amendment does not authorize, and the `technical_blockers_at_freeze_time` list

This amendment freezes dataset identity, provenance, denominators, and claim boundaries. It does **not**:
run VEGO-AI, Detector-v1, a provider, an API, or an external model; inspect any VEGO-AI or Detector-v1
result; resolve the GPL-3.0 review scope noted in §3; resolve CI or protected-path authorization; or
authorize a provider-backed run, which remains a separate, explicit human decision.

**AirTravel execution status is `TECHNICAL_NO_GO`, not conditional-GO, for the following complete
`technical_blockers_at_freeze_time` list** (narrowing this to only license/CI, as an earlier session turn
did, understated the actual blocker list; this list is named "at freeze time" because item 1 is expected to
change independently of this document's content, per its own note):

1. `amendment_not_merged_into_main` — this v1.0.2 amendment is open as PR #36 (branch
   `study1/airtravel-v1.0.2-amendment`) but not yet merged into `main`, so Codex's tooling on `main` cannot
   yet read it as the authoritative amendment. It is no longer accurate to call it "unpushed" once pushed;
   "not merged" is the precise current state and is tracked separately from the other five items below,
   which are not resolved merely by merging this PR.
2. Exact runtime bytes have not yet passed the fail-closed verifier (`scripts/verify_text2uml_airtravel_runtime.py`) against this amendment's manifest — this remains a Codex dependency per §4's verification-tier limitation, not something cross-document consistency discharges.
3. Production-observed Q&A routes remain at zero.
4. Model/provider selection remains unspecified.
5. CI is red (source/security/documents job and merge gate failing on a stale release manifest, per
   `2026-09-04-airtravel-v102-pre-run-technical-gate.md`).
6. Paid-run authorization has not been given.

Each of these is independent; resolving GPL-review scope and CI alone does not clear items 1–4 and 6, and
merging this PR alone does not clear items 2–6.

## 12. Change control

This amendment is exempt from v1.0.1 §16's post-data change-control procedure because no data exposure has
occurred for any setting, historical or new (§0). Any future change to this amendment's frozen dataset
identity (§3–§5), once any `cd_airtravel` run has occurred, is a post-data change and requires a versioned,
dated successor document under the same procedure v1.0.1 §16 establishes.
