# AirTravel offline fake-preflight authorization packet v4

Status: **AUTHORIZATION_V4_REPAIRED_AWAITING_INDEPENDENT_REVIEW**.

This packet supersedes packet v3 for future execution. The v3 execution remains
**OFFLINE_FAKE_PREFLIGHT_EVIDENCE_REJECTED** and is preserved byte-for-byte as
private debugging evidence. Nothing in this packet re-authorizes, accepts, or
rewrites that run. Packet v3 is **SUPERSEDED_FOR_FUTURE_EXECUTION**.

## Scope and stop state

This is a versioned, machine-bound request for one future local fake-provider
technical preflight only:

- setting_id: cd_airtravel
- corpus_id: text2uml_airtravel_253b26dc
- N: 4
- provider/API calls: forbidden
- network access: forbidden
- Detector-v1 and renderer: forbidden
- paid execution: false
- maximum invocations: one
- status before a fresh owner grant: AUTHORIZATION_REQUESTED_NOT_GRANTED

Current verification state: source/runtime/config verification **PASS**;
exact protected fake-provider preflight **BLOCKED_PENDING_AUTHORIZATION**.

No protected orchestrator, external provider, model, Detector-v1, renderer, or
scientific analysis is run by preparation. The future grant must be issued
separately by the human owner after independent review. A grant is not a
cryptographic signature against a malicious filesystem owner.

## Machine authority

The controlling machine manifest is
docs/research/phd-proposal/airtravel-pr38-correction/airtravel-v4-packet-manifest.json.

Manifest SHA-256:
b10b6685f3c75023141ffe92a13c4c7a871c86de7367f744dbe984feee8441fe

It binds the packet version, base SHA
c34d3954b5e080d090017d2ea655d454d75a6b92, implementation ancestor
28a1d95f39058e5b9dd3e7601584e2393311d405, AirTravel identity, runtime
archive and five runtime hashes, fixed run root, layout, command template,
bounds, prohibitions, and required evidence. The validator must compare the
future grant and request directly to this manifest before any protected import.
The persisted request also binds the SHA-256 of this packet. The grant must
repeat that packet hash, the manifest hash, and the exact command fingerprint;
changing the packet bytes, command tokens, interpreter, or any bound path is a
fail-closed condition.

## Fixed private root and layout

Every future request, message, grant, command record, attempt marker, receipt,
and verification artifact is inside:

external_data/airtravel-pr38/v4-authorized-fake-run/

Required layout:

- control/private-execution-request.json
- control/authorization-grant.message.txt (created only with a fresh owner grant)
- control/authorization-grant.json (created only with a fresh owner grant)
- control/execution-command.json
- control/preparation-receipt.json
- control/attempt-start.json
- control/attempt-end.json
- output/baseline/
- output/instrumented/
- output/preflight-receipt.json
- verification/final-output-inventory.json
- verification/parity-verification.json
- verification/lifecycle-verification.json
- verification/post-verification-receipt.json

No sibling verification directory is permitted. No required child may escape the
root, normalize to another path, collide under case folding, or traverse
parent-segments. Symlinks and Windows reparse points are rejected. Only the root
above is an allowed write root; repository source, schemas, reports, and
protected files are prohibited write roots.

## Exact command template

The machine manifest records the exact relative command template. The executing
machine must resolve the Python interpreter and all arguments, record their
canonical token list and SHA-256 in control/execution-command.json, and bind
that fingerprint into the future grant. Any path, token, executable, output,
packet, or grant change invalidates the grant.

Preparation may create only the private request/template and preparation
receipt. Execution is a separate command that requires a fresh, hash-bound
owner grant. When granted, it consumes the grant once, executes the two local
fake passes, and emits the v2 receipt; it never reaches an external provider.

## Durable one-time consumption

Before protected imports or orchestrator execution, the future implementation
must validate the packet manifest, request, owner message and grant, then create
control/attempt-start.json with exclusive creation. It contains the grant,
message and command hashes, reviewed head, invocation ID, fresh nonce, UTC and
monotonic start times, process identity, and attempt_number=1. An existing
attempt-start, attempt-end, or output receipt fails closed. The marker is never
removed automatically, including after a failed run.

Completion or failure creates control/attempt-end.json exclusively, bound to
the same invocation, with status, exit classification, UTC completion time,
grant_consumption_status=CONSUMED, retry_count=0, replay_count=0, and the
output receipt hash when present. The grant carries the nonce and invocation ID;
the attempt-start marker must match both values exactly. Grants are valid only
when `granted_at <= evaluated_at < expires_at`, with an aware timestamp and a
window no longer than 24 hours. Deleting only output/ cannot permit replay.

## Persisted parity evidence

Both runs must persist privacy-safe records at:

- output/baseline/call-records.jsonl
- output/instrumented/call-records.jsonl

Each record contains only sequence, phase, case ID, label, source/target
agents, prompt/answer lengths and SHA-256 values, deterministic decision hash,
and fake-client identity. Raw prompts, answers, credentials and API keys are
forbidden. Independent review recomputes direct/instrumented counts, ordered
label/prompt/answer/decision parity, and phase/case coverage from these files.
The v4 receipt binds both call-record hashes; an in-memory assertion is not
evidence.

## Receipt v2 and safety counters

The execute receipt uses
schemas/airtravel-technical-receipt-v2.schema.json and must include mode,
invocation and attempt identity, start/end timestamps, grant validity,
consumption/retry/replay state, both call counts, all parity results, completed
cases/phases, event and route counts, before/after protected and tracked
manifest hashes, output inventory and containment, privacy status, call-record
hashes, and every safety counter.

Receipt validation derives `grant_valid_at_start` from the evaluated grant
window and records `grant_evaluated_at`. It also checks direct plus
instrumented call-count equality, the two persisted call-record hashes, the
event-log hash, the output-inventory hash, and the presence of every required
evidence file before accepting a receipt.

The following counters must be persisted and zero:

external_provider_call_count, paid_provider_call_count,
provider_constructor_attempt_count, provider_import_attempt_count,
network_socket_attempt_count, DNS_attempt_count,
credential_access_attempt_count, subprocess_attempt_count,
native_escape_attempt_count, detector_v1_run_count, renderer_run_count,
and provider_backed_production_route_pair_count.

This remains a Python-level trusted-code boundary, not an OS sandbox.

## Frozen runtime and claim boundary

The runtime archive hash is
e37baecd20a0c84eb1d9b87b3b78a23bc4b4eb8a9824ad3086dc30aa35fdd31f. The five
runtime file hashes and the reference-file exclusion are machine-bound in the
manifest. GPL review concerns publication/redistribution; it does not block a
private local fake preflight.

A future successful receipt can support only deterministic offline execution,
observer operation, persisted parity, lifecycle capture, fake route coverage and
containment readiness. It cannot support real-provider behavior, accuracy,
precision, recall, F1, intervention correctness, human benefit, generalization,
student behavior, or historical Cheers/ParkWise claims.

## Required checks before a fresh grant

Run the v4 prepare-only command and ordinary tests. Verify the exact current
head, clean tracked worktree, packet-manifest hash, runtime archive/files,
reference separation, protected/tracked preservation, and the rejected v3
bundle hash/inventory. No owner grant or fake execution is created by this
preparation package.

The stopping state is:

AUTHORIZATION_V4_REPAIRED_AWAITING_INDEPENDENT_REVIEW
