# AirTravel offline fake-preflight authorization packet v4

Status: **PREFLIGHT_V4_PREPARED_AWAITING_INDEPENDENT_REVIEW_AND_FRESH_USER_GRANT**.

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

No protected orchestrator, external provider, model, Detector-v1, renderer, or
scientific analysis is run by preparation. The future grant must be issued
separately by the human owner after independent review. A grant is not a
cryptographic signature against a malicious filesystem owner.

## Machine authority

The controlling machine manifest is
docs/research/phd-proposal/airtravel-pr38-correction/airtravel-v4-packet-manifest.json.

Manifest SHA-256:
0416bcd332bcf7cbab8f34e737433b1b03ea864355407f40f32aeb6ed0faa6f6

It binds the packet version, base SHA
c34d3954b5e080d090017d2ea655d454d75a6b92, implementation ancestor
28a1d95f39058e5b9dd3e7601584e2393311d405, AirTravel identity, runtime
archive and five runtime hashes, fixed run root, layout, command template,
bounds, prohibitions, and required evidence. The validator must compare the
future grant and request directly to this manifest before any protected import.

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
receipt. It must end with AUTHORIZATION_REQUESTED_NOT_GRANTED; it never
executes.

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
output receipt hash when present. Deleting only output/ cannot permit replay.

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

PREFLIGHT_V4_PREPARED_AWAITING_INDEPENDENT_REVIEW_AND_FRESH_USER_GRANT
