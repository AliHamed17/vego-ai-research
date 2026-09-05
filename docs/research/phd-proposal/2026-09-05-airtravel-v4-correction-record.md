# AirTravel v4 correction record

Status: `PREFLIGHT_V4_PREPARED_AWAITING_INDEPENDENT_REVIEW_AND_FRESH_USER_GRANT`

The previous local fake-provider run is retained as
`OFFLINE_FAKE_PREFLIGHT_EVIDENCE_REJECTED`. Its private bundle is immutable
debugging evidence; this record does not amend, delete, move, or re-authorize
it. The rejection concerned incomplete independent evidence binding: the
declared output path was not enforced end-to-end, post-verification was outside
the declared output root, execution identity and grant consumption were not
durably recorded, and call-level parity records were not persisted.

Packet v3 is superseded for future execution only. No scientific result exists
from the rejected run, and no retrospective authorization is implied.

## v4 correction

Packet v4 and its machine manifest bind one fixed private root, exact setting
and corpus identifiers, the runtime/archive hashes, protected-manifest and
harness/schema hashes, command template, timeout and call bounds, required
evidence, prohibited roots, and zero-provider/zero-network restrictions. The
request and any future owner grant must match the manifest before protected
imports. Preparation writes only the private request, command fingerprint, and
preparation receipt. A future execution must create exclusive attempt-start
and attempt-end markers and persist privacy-safe baseline/instrumented call
records for independent parity reconstruction.

GPL review concerns publication or redistribution of upstream-derived bytes;
it does not block a private local fake preflight. No provider, model,
Detector-v1, renderer, or experiment is run by this preparation.

## Remaining human decision

Independent review must confirm the frozen head, manifest, runtime inputs,
protected-file preservation, and command fingerprint. Only then may Ali issue a
fresh, one-time owner grant bound to those hashes. The requested grant is for
one local fake-provider technical preflight only; it does not authorize a real
provider, paid execution, synthetic data, Detector-v1 analysis, publication, or
historical Cheers/ParkWise claims.
