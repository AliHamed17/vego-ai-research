# Study 2 Prospective: Redaction and Privacy Policy

**Status:** FROZEN 2026-09-08. Enforced by `vego_study2.prospective.aggregate.assert_redacted`
and by `scripts/check_repository_privacy.py` in CI.

## 1. What never enters Git

- Corpus bytes (domain description, candidate models), in whole or in part.
- Prompts, system templates instantiated with corpus text, model answers,
  evidence strings, fragment text, question or answer text.
- Private artifacts: per-case condition outputs, the Q&A event stream, the
  call ledger, lifecycle records, pipeline state, the protected pipeline's
  own output files, and the blinded rater cards.
- Credential values in any form, including hashes or lengths.
- Absolute private paths. The private root is written only as the token
  `${VEGO_PRIVATE_EVIDENCE_ROOT}`.

## 2. What is published (redacted public aggregate)

Counts, enumerations, SHA-256 digests, identifiers (case ids, run id, model
id, commit), timestamps, numbers, and harness-authored sentences under the
keys `claim_boundary`, `detail`, `credential_source` and `algorithm`. Every
other string must match a short-label allowlist and must not read as prose.
The aggregate is additionally checked against the first forty characters of
every corpus line in memory before it is written.

## 3. Credential handling

The provider credential is read only by the provider SDK from
`OPENAI_API_KEY` in the local process environment. The harness tests presence
by key membership only. It never prints, inspects, logs, hashes, commits or
transmits the value. The receipt records the sentence describing this policy,
not any property of the value.

## 4. Network containment

During execution, name resolution is permitted only for `api.openai.com`.
During preflight, every destination is blocked. Blocked attempts are counted
in the receipt.

## 5. Output containment

The output root must be absolute, inside the private root, fresh, and free of
symlinks or reparse points on every existing ancestor. Receipts are written
with exclusive-create semantics.

## 6. Rater cards

Cards contain produced artifact content and are therefore private. They are
generated into the private root; the public record holds only their count and
digests. Cards carry no condition label, no case id and no run identifier
visible to the rater.

## 7. Validation

`study2_prospective_run.py validate` recomputes the public aggregate from the
private evidence and compares digests, verifies the receipt binding, and
reconciles the ledger with the receipt request count.
