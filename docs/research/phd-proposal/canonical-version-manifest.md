# Canonical Proposal Version Manifest

Last updated: 2026-08-19

Status: **working source-of-truth register.** The entries below identify which artifact lineage is
currently used for reconciliation. They do not convert a working draft into a supervisor-approved
or submission-ready artifact. SHA-256 release hashes remain `TBD` until a frozen delivery package
is generated; repository blob or commit identifiers must not be substituted for a release-file
hash without saying so.

## Current canonical working set

| Artifact | Canonical working source | Evidence/content cutoff | Controlling artifact policy | Approval state | Release SHA-256 |
| --- | --- | --- | --- | --- | --- |
| Literature review | `VEGO_AI_Literature_Review_v10_Iris_Aligned_Controlled_2026-08-18.pdf` | 2026-08-18 | Problem-world review; contribution tables must be synchronized to `artifact-layer-contract.md` before the next render | Working scholarly draft; formal QL searches, Ali review, and supervisor approval pending | `TBD at release freeze` |
| RQ literature workbook | `VEGO-AI_Literature_Workbook_RQ_Only_Organized_v8_Audit_Aligned.xlsx` | 2026-08-19 | RQ-only controlled workbook; artifact/baseline/evaluation rows must use the layered model; provenance against the larger multi-sheet lineage remains explicit | Working evidence map; human inclusion review and supervisor approval pending | `TBD at release freeze` |
| Chapter 4 methodology | `docs/research/phd-proposal/chapter-4-research-methodology.md` | 2026-08-19 | Layered artifact model v1; two-stage evaluation per study; integrated U-RQ test | Internal working draft; four supervisor decisions and resourcing remain open | `TBD at release freeze` |
| Layered artifact contract | `docs/research/phd-proposal/artifact-layer-contract.md` | 2026-08-19 | Defines primary artifact, supporting implementation bundle, and evaluation package | Recommended reconciliation control; supervisor confirmation pending | `TBD at release freeze` |
| Three-study contract | `docs/research/phd-proposal/three-study-contract.md` | 2026-08-19 after reconciliation | Same layered artifact model and evidence gates as Chapter 4 | Working research contract; RQ wording and study boundaries pending approval | `TBD at release freeze` |
| Chapter 4 decisions packet | `docs/research/phd-proposal/2026-08-19-chapter4-decisions-packet.md` | 2026-08-19 | Four explicit Confirm/Correct/Defer decisions with dated decision records | Awaiting Iris/Arnon response | `TBD at release freeze` |
| Chapter 5 preliminary results | `docs/research/phd-proposal/chapter-5-preliminary-results.md` | 2026-08-19 | Mechanism, observability, and reference-implementation conformance only | Working draft; wording confirmation pending | `TBD at release freeze` |
| Study resourcing control | `docs/operations/study-resourcing-request-template.md` | 2026-08-19 | Separate Study 2 implementer and Study 3 rater requests; ethics/data determination before recruitment | Draft outreach material; no participant commitment recorded | `TBD at release freeze` |
| VEGO-AI foundation manuscript | supplied `Variability_MAS4MODELS2026_Mar28_IRB2...pdf` manuscript | manuscript supplied for 2026 MODELS cycle | Architecture/results source only; paper described as accepted/program-listed, not as a final proceedings copy | Template/anonymized manuscript; final DOI and pagination not asserted | `TBD at release freeze` |

## Known cross-artifact facts that must remain visible

- The foundation manuscript reports **26 variability patterns**: 8 substantial and 18 occasional.
- The supplied implementation snapshot contains **27 pattern files**: 9 substantial and 18
  occasional. The one-pattern difference is unresolved and neither count is described as an
  independently reproduced result.
- EXP-005 remains **0/24** generalization-safe expert labels.
- Medical entry gates remain **0/6**.
- Formal literature searches QL-01–QL-05 remain **0/5** unless a later receipt explicitly changes
  that state.
- Instrument evidence, implementation evidence, and outcome/effect evidence remain distinct.

## Version authority rules

1. A newer filename does not automatically supersede an older artifact. Supersession requires an
   explicit manifest entry, rationale, and affected-file list.
2. A workbook sheet labeled `vN` is not authoritative merely because `N` is higher. The current
   entry sheet must identify the authoritative tabs and mark legacy tabs as superseded.
3. A PDF, DOCX, workbook, and Markdown source describing the same research state must use the same
   RQ wording, artifact layers, hard-gate counts, evidence cutoff, and approval status.
4. Composite readiness scores may not replace the raw hard-gate counts. Any diagnostic score must
   state its dimensions and must not be labeled submission readiness.
5. Release SHA-256 values are generated only after the final files are rendered and assembled.
   The release manifest must hash every delivered file and list no absent companion deliverable.
6. Any supervisor decision must update this manifest, the decision/change log, Chapter 4, the
   three-study contract, and the workbook before the next supervisor-facing package is labeled
   current.

## Next release preflight

Before generating the next package:

- [ ] Reconcile the literature-review contribution tables to the layered artifact model.
- [ ] Reconcile the RQ workbook artifact, comparator, and evaluation rows.
- [ ] Resolve or explicitly retain the 26-versus-27 pattern discrepancy.
- [ ] Correct PDF version metadata, page numbering, tail marker, and candidacy wording.
- [ ] Verify that every companion deliverable named by the package is present.
- [ ] Generate SHA-256 hashes after rendering, not before.
- [ ] Record Ali review and supervisor decision state without inferring approval.
