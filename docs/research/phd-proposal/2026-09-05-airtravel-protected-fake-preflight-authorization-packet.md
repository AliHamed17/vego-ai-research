# Protected authorization packet — AirTravel fake-provider preflight

**Status: REQUEST ONLY — DO NOT EXECUTE YET**
**Authorization target (protected code):** `11cbe0413884624469867afa7aba66a0050a6442`
**Expiry:** 2026-09-06 23:59 Asia/Jerusalem, or immediately on any hash/config drift.

This packet requests one local, deterministic, network-disabled fake-provider
preflight for `cd_airtravel`, `N=4`. It authorizes no real provider, external
model, API call, Detector-v1 run, spend, synthetic generation, or data release.
Explicit human acceptance is required before execution.

## Proposed change and protected-file boundary

No protected runtime file is proposed for modification. The execution target
is the frozen protected code at the authorization SHA above, with a local fake
client injected only at the existing client boundary.

| File | State | SHA-256 at target | Why needed |
| --- | --- | --- | --- |
| `VEGO-AI/framework/orchestrator.py` | unchanged/read-only | `fca4b885ee07381db0f02e558b1aebf25bdc7c27da1c471fd3103d7e0e2d5b88` | Execute the real control flow without editing it |
| `VEGO-AI/framework/qa_registry.py` | unchanged/read-only | `ab189d3fd954ea03ba891f5746b36eff8889baeff73d7594f820e68f8762ad5f` | Preserve question/answer registry semantics |
| `VEGO-AI/framework/state.py` | unchanged/read-only | `d8492a623804065b86905d6183979c322d6f83376bf91026e718c615eea1730d` | Preserve scientific state serialization |
| `VEGO-AI/framework/qa_instrumented_runner.py` | existing additive harness | `d187f8e8113a86caf24e55720e227f9a5f9b3466126969166bcefb83625a215f` | Inject deterministic fake client and observe metadata |

Before/after hashes for the three protected files are identical by design.
The materializer, verifier, call-bound module, tests, receipts, and this packet
are non-protected support files; none changes the protected runtime.

## Network and provider boundary

The fake client is an in-process deterministic implementation. The execution
command must run with network disabled (Windows firewall/offline profile or an
isolated runner), and must assert provider-call count `0`. Any attempted socket,
HTTP, SDK, credential, or provider import is a hard failure. No credential or
private URL is required.

## Exact commands (after acceptance only)

```powershell
$env:PYTHONPATH = (Get-Location).Path
python scripts/materialize_airtravel_runtime_v3_2_1.py `
  --upstream-archive external_data/airtravel-v3.2.1/text2uml-253b26dc704d523209a5cba79686f8f7fab57d63.zip `
  --output-root external_data/airtravel-v3.2.1/runtime_input
python -m pytest -q scripts/tests/test_audit_historical_case_recovery_v3_2.py scripts/tests/test_study1_call_bound.py
python -c "import sys; sys.path.insert(0, 'VEGO-AI/framework'); from qa_instrumented_runner import run_parity_fixture; print(run_parity_fixture())"
```

The final command is a local fixture/parity harness only. It must be extended
with the exact frozen `cd_airtravel` configuration and `N=4` only after the
protected owner accepts this packet. Stop on any hash drift before running.

## Expected fake observations and assertions

- Baseline fake-client counter: `N=0 → 4`, `N=1 → 7`, `N=4 → 16` calls.
- Static worst-case bound: `82 + 61N`; for `N=4`, 326 calls at
  `MAX_QA_ROUNDS=10`.
- Natural protected route: the route emitted by the actual orchestrator path.
- Helper-only routes: the six declared Agent 2/3/4 × Agent 1/2 combinations;
  these must be labelled helper fixtures, never production-observed routes.
- Prompt hashes and labels are identical between instrumented and
  non-instrumented runs.
- Serialized scientific state is identical between those runs.
- Observer events persist with stable episode IDs, correct source/target,
  case/stage/skill/round metadata, and no cross-case or cross-round mixing.
- Lifecycle assertions cover `CONVERGED`, `TERMINATED_MAX_ROUNDS`, and
  `INCOMPLETE_TECHNICAL`; incomplete episodes are excluded from scientific
  denominators.
- Provider calls, external calls, and production-observed routes remain `0`.

## Rollback and authorization

The run creates only an ignored local fixture/evidence directory. On failure,
stop, preserve the failure receipt, and remove only that run directory; restore
the pre-run checkout with `git clean` only after the owner confirms the exact
ignored paths. No protected file is edited, so code rollback is a no-op.

**Requested scope:** one offline fake-provider preflight of frozen `cd_airtravel`
(`N=4`) for structural parity and lifecycle evidence. **Not authorized:** every
real provider/model call, paid run, external network access, Detector-v1
analysis, synthetic corpus creation, or protected-file modification.

**Owner decision:** `PENDING — Ali must explicitly accept or reject this packet.`
