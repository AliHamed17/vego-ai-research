# PR 38 exclusive correction plan

Base main: c34d3954b5e080d090017d2ea655d454d75a6b92.
Correction parent: 3727acfe2130863ab6b737824a1718e7b3648b92.
Ali confirms Claude has stopped. No parallel writers are permitted.

1. Preserve inspected WIP locally, never push it. Start an isolated correction branch at PR38.
2. Add refusing grant/source/output tests; replace the packet-existence gate with schema/hash/commit/command-bound grants. No actual grant is issued.
3. Test external observer correlation, loop closure, route pairs, two-run parity, per-run bounds, timeout cleanup, write quotas and network refusal using fixtures only.
4. Make rendering depend on hash-bound successful technical receipts, canonical Detector output and deterministic descriptive fields. Test all eight outputs and rejected unsupported claims.
5. Materialize the private five-file pack with the existing deterministic command; run prepare-only. Do not execute the exact preflight.
6. Supersede packet v2, generate packet v3 with final content hashes and future grant-bound head. Record private exact paths separately; publish no raw data.
7. Run focused, scripts, VEGO-AI and root suites; lint, compile, privacy, security, evidence, schema and record checks. Regenerate hardening manifests three times after other edits finish.
8. Fetch and verify unmoved main/PR head before normal correction commits and push HEAD to the existing PR38 branch. Wait for all six fresh CI jobs. Never merge.

Commit boundary: one consolidated correction commit covering authorization/source safety, observer/parity/output and renderer corrections, final packet/evidence and the mechanically generated release manifest.
CI follow-up: a normal fast-forward compatibility fix is permitted in this same PR after reproducing the Python 3.10 pathlib quota failure; it includes code/tests and refreshed bindings, not a receipt-only commit.
Stop on main/head drift, protected modifications, provider access, unavailable source archive or missing human authority. Final exact execution remains unperformed.

WIP comparison: retain PR38 frozen runtime/check structure and call-site table. Reuse only independently tested question/answer correlation and lifecycle logic from the local checkpoint; do not copy its execution guard, grant format, renderer, provider guard, evidence receipts or unrelated documents wholesale. Those interfaces do not satisfy this correction's exact grant/output/receipt requirements.
