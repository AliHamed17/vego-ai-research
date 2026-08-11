# Supplied Drive Folders — Metadata-Only Inventory, 11 August 2026

Status: **metadata-only observation record.** File and folder names, counts, and sizes only. **No patient, event, or encounter row was opened, read, copied, processed, or sent to any model.** This is the "metadata-only reconciliation that does not expose medical rows" that the [medical readiness scorecard](./medical-readiness-scorecard.md) explicitly permits while all six entry gates remain blocked.

Three Drive folders were supplied on 2026-08-11. They are reachable on this machine through Google Drive for Desktop under `G:\.shortcut-targets-by-id\<folder-id>\`.

---

## Folder 1 — `VEGO-AI PhD` (delivery target)

`1omVq81a5zygRrNi3VYqoOUp_ZNKrchty`

The shared PhD folder nominated as the delivery target. Contents at inventory time were the supervisor package, the private preparation subfolder, the gaps report, the MediVARIA overview, and a governance subfolder. This folder is now maintained as the professional Word/PDF/Excel document set.

## Folder 2 — `VEGO-AI` (system, data, and the published paper)

`1WSW4aC4AIipaUmYq9Oyod2vzWf6PNKsL` · **723 files**

This is the real VEGO-AI implementation and evaluation material — software and modeling only, no medical content, therefore **no data-boundary restriction applies**.

| Item | Contents |
| --- | --- |
| `Variability_VEGO-AI_MODELS2026_final.pdf` | The published MODELS '26 paper. Read and recorded in the [foundation paper record](./vego-ai-foundation-paper-record.md) |
| `System/` | The framework itself: `framework`, `models`, `inputs`, `eval`, `eval_output`, `analysis`, `README.md` |
| `Dataset_Cheers/` | 138 files across `ClassDiagram`, `UseCaseDiagram`, `StateDiagram` — the student model corpus |
| `output/` | Experiment outputs, organised as `Ch-CD` and `Ch-UCD` |
| `Visualizer/` | `VEGO-AI.exe`, `visualize_compliance.py`, `compliance_vectors`, `guidelines`, `models`, config and requirements |
| `Tasks.gdoc` | Native Google Doc |

**Note on `StateDiagram`:** the corpus contains state-diagram material, while the published evaluation covers class and use-case diagrams only — the paper names behavioural languages such as state diagrams as *future work*. Any use of that subset is therefore beyond the published evaluation and must not be described as covered by it.

## Folder 3 — `iris-arnon-7.8.26` (clinical datasets — GATED)

`1zhrx3h8u8eaHY-4w0Q_cGwh9f_TrcRnH` · **78 files**

> **This folder contains patient-level clinical data and is subject to the full medical boundary. It was inventoried by name and size only.**

It was described on supply as containing "VEGO-AI experiments data and experiments paper used." **It does not.** The VEGO-AI experiments and the paper are in Folder 2. This folder holds two clinical datasets:

| Subfolder | Observed contents (names and sizes only) |
| --- | --- |
| `EHRSHOT/` | OMOP-CDM formatted clinical data: `condition_occurrence.csv` (~325 MB), `condition_era.csv` (~36 MB), `care_site.csv`, `cdm_source.csv`, plus OMOP vocabulary files `concept.csv` (~1.23 GB), `concept_relationship.csv` (~3.98 GB), `concept_ancestor.csv` (~1.87 GB), `concept_synonym.csv` (~239 MB), `concept_class.csv`; two `concept_knowledge_graph*.html` files; `csv_fields_summary.xlsx` |
| `mimic-iii-1.4/` | `dataset`, `analysis`, `index.xlsx` |

### Why this is significant

**EHRSHOT is a dataset that appears in no governance document in this project.** Every medical control written to date names MIMIC and Clalit. EHRSHOT is a Stanford-published EHR benchmark derived from real patient records and distributed under a research data use agreement; `condition_occurrence` and `condition_era` are patient/event-level tables by definition.

This means the standing controls need extending, not merely applying:

- The six entry gates (`G1`–`G6`) were written against MIMIC and Clalit. A named data source is part of Gate 1 (use-case) and Gate 3 (authorization); EHRSHOT is currently named in neither.
- `Q-05` ("Is MIMIC selected, and what license, access, privacy, and ethics rules apply?") has no EHRSHOT equivalent.
- The external-fact register carries no entry for EHRSHOT's provenance, licence, or authorization basis.
- Whether individual, project-specific authorization exists for EHRSHOT — for each researcher, for this stated project — is **unknown and unverified**.

### What remains prohibited regardless of this folder's presence

Medical readiness stands at **0 of 6 entry gates**. Folder visibility and download capability are explicitly *not* authorization — that principle is already recorded in the [Drive boundary verification record](./drive-boundary-verification-2026-08-03.md). Until all six gates pass, the following remain prohibited: inspecting any patient, event, or encounter row; clinical-note access; medical computation; executing any local or remote model over medical data; a bounded pilot; export; and any medical evidence claim.

Nothing in this folder has been copied into the repository, into the working Drive, or into any model context, and nothing from it may be.

### Recommended next actions (all human-owned)

1. Record EHRSHOT in the external-fact register with its provenance, licence terms, and the authorization basis under which it was obtained and shared.
2. Extend `Q-05` (or open a sibling question) to cover EHRSHOT explicitly, since Gate 1 and Gate 3 both require a *named* data source.
3. Confirm in writing whether the licence for each dataset permits the intended research use by each named researcher, and whether the current sharing arrangement is consistent with those terms.
4. Decide, with the supervisors, whether EHRSHOT changes the Plan A dataset assumption — the plan currently discusses MIMIC and Clalit only.

---

*Inventory performed 2026-08-11 by directory listing only. No file in Folder 3 was opened. Sizes and names are reported as observed; no content-level integrity claim is made, and matching metadata is not proof of unchanged content.*
