# ACL 2026 Human-Agent Corpus — Bounded Evidence Package

This package is generated from the README at the immutable commit recorded in
`source-manifest.json`. It is a bounded repository-corpus extraction, not a
systematic database review and not an execution of QL-01 through QL-05.

## Files and grain

- `occurrences.csv`: one row per in-scope README occurrence; 525 rows.
- `works.csv`: one row per deduplicated work; 116 rows.
- `screening.csv`: one machine metadata-screen row per work. Human inclusion,
  author conclusions, and researcher synthesis remain pending.
- `local-candidate-corpus-audit.json`: reconciles the separate 144-record local
  candidate corpus and the six-row native Google workbook snapshot. Its 139
  normalized-title groups retain the weakest source verification label in each
  duplicate group: 127 verified-labelled, 11 partial, and 1 unverified.
- `taxonomy-gap-matrix.md`: maps what the source taxonomy explicitly encodes,
  what it does not encode, and the evidence-safe Chapter 2 structure.
- `chapter2-source-anchors.md`: page/section anchors into the primary ACL
  survey, with claim-safe wording for Chapter 2.
- `conservative-key-sources.csv`: twelve title/taxonomy-level candidates for
  human screening; no paper-level finding is attributed.
- `native-workbook-snapshot-2026-08-15.json`: read-only schema and row-count
  snapshot derived from a hash-bound connector capture of all six used ranges,
  including 11 Controlled_Lists data rows.
- `evidence-inputs/`: immutable, hash-bound sanitized inputs for the native
  workbook read and the unverified Foundations-query observation.
- `native-*-append-staging.csv`: exact-schema append candidates. These files
  have not been written to the native workbook. Their canonical SQ/Plan fields
  remain blank because the RQs and Plan A/B are unresolved.
- `native-append-preflight.json`: lossless/order/key-replay proof for offline
  staging. Live append remains blocked because native table metadata was not
  exposed by the connector.
- `foundations-query-test-2026-08-15.json`: one hash-bound, unverified operator
  observation of the Foundations query; no durable DOM/screenshot exists and
  it is not QL-01–QL-05 execution.

## Deduplication

Occurrences are joined when they share a normalized title or a strong
identifier (arXiv, ACL Anthology, OpenReview, DOI, or PubMed). This connects
publisher/preprint aliases and title variants while retaining every occurrence
and line reference. Same-title groups with conflicting strong identifiers fail
closed unless the exact publisher/preprint alias set is explicitly reviewed.
The final `Work_ID` is a deterministic hash of the connected component's
identifiers and normalized titles.

## Claim boundary

`Machine_Screen_Status=Complete` means only that all 116 titles and repository
taxonomy records received a deterministic preliminary mapping. It is never
equivalent to human title/abstract screening, full-text inclusion, independent
identity verification, or review completeness.
