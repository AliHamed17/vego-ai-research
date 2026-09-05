# AirTravel v4 correction record

Status: `AUTHORIZATION_V4_REPAIRED_AWAITING_INDEPENDENT_REVIEW`

The previous local fake-provider run is retained as
`OFFLINE_FAKE_PREFLIGHT_EVIDENCE_REJECTED`. Its private bundle is immutable
debugging evidence; this record does not amend, delete, move, or re-authorize
it. The rejection concerned incomplete independent evidence binding: the
declared output path was not enforced end-to-end, post-verification was outside
the declared output root, execution identity and grant consumption were not
durably recorded, and call-level parity records were not persisted.

Packet v3 is superseded for future execution only. No scientific result exists
from the rejected run, and no retrospective authorization is implied.

The current AirTravel evidence state is source/runtime/config verification
`PASS`; the exact protected fake-provider preflight is
`BLOCKED_PENDING_AUTHORIZATION`.

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

## Repair v4.1

The independent review found fail-open command, packet-hash, execution-layout,
attempt-identity, grant-expiry, and receipt cross-field checks. The repaired
contract now requires the exact resolved command, binds the packet digest in
the request and grant, rejects undeclared execution siblings, matches the
durable attempt marker, enforces an aware validity window of at most 24 hours,
and derives receipt grant validity and call-count consistency. The current
packet SHA-256 is
`8c7b26956a547aa8299b1905037fd5f69da86f153d9d79a4c25429428497e18c`; the
machine-manifest SHA-256 is
`6287e592dda3298b6e0006c22807fde03d868430f4755e88aca6600b6e36b6cb`.

## Remaining human decision

Independent review must confirm the frozen head, manifest, runtime inputs,
protected-file preservation, and command fingerprint. Only then may Ali issue a
fresh, one-time owner grant bound to those hashes. The requested grant is for
one local fake-provider technical preflight only; it does not authorize a real
provider, paid execution, synthetic data, Detector-v1 analysis, publication, or
historical Cheers/ParkWise claims.
