# AirTravel API Execution Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Build an isolated, provenance-bound, USD-6-capped AirTravel execution lane that cannot make an external provider call until a fresh, one-time authorization validates.

**Architecture:** The new lane is independent of the protected legacy orchestrator. It verifies the public Text2UML source/archive/runtime mapping, creates a private immutable input manifest, uses a deterministic fake-provider preflight, and permits an OpenAI transport only through an explicit execute mode after validation. Historical VEGO ZIP material and QuRE remain excluded from every provider-visible path.

**Tech Stack:** Python 3.10+, Decimal, jsonschema, pytest, existing QACommunicationRecorder, OpenAI SDK behind an execute-only adapter, GitHub Actions Python matrix.

**Spec:** docs/superpowers/specs/2026-09-12-airtravel-api-execution-design.md

## Global Constraints

- Base: origin/main at 158714064a2ecc40f5eda8561240978ebfe1b371, in the existing isolated worktree.
- Public input only: Text2UML/AirTravel commit 253b26dc704d523209a5cba79686f8f7fab57d63, archive SHA-256 8cf82e2ab2d2ce3da9a7ec4165e760ae1e0d9af14468f5aa2a3883037d8da701, and the v1.0.2 five-file mapping.
- Never transmit VEGO ZIP, student models, expert sheets, GUI/user logs, reference files, or QuRE to a provider.
- Do not modify VEGO-AI/framework, Detector-v1 definitions, amendment bytes, or corpus bytes.
- Keep all raw inputs, prompts, answers, events, grants, receipts, and pipeline outputs only under the ignored external_data/airtravel-api-runs/<run_id>/ root.
- prepare and preflight must make zero network/provider calls. execute is blocked without a new one-time grant.
- Use Decimal for every price/reservation/spend calculation and enforce maximum total USD 6.00.
- Receipt errors are controlled codes only; they never contain a provider exception message or raw response.
- Place every new test in scripts/tests/, which CI executes on Python 3.10–3.13.

---

## File Map

| Path | Role |
| --- | --- |
| scripts/verify_text2uml_airtravel_runtime.py | Archive, 143-entry source, mapping, runtime, reference separation verification. |
| scripts/study1_call_bound.py | Declared call-site derivation. |
| scripts/airtravel_execution_contract.py | Canonical hashes, config, manifest, grant, containment, receipt, budget types. |
| scripts/airtravel_execution_provider.py | Fake provider and execute-only OpenAI adapter. |
| scripts/airtravel_execution_pipeline.py | Isolated Agent 1–4 flow and Q&A lifecycle. |
| scripts/study1_external_execution_gate.py | Mode-specific gate. |
| scripts/study1_airtravel_external_runner.py | prepare / preflight / execute CLI. |
| schemas/airtravel-api-execution-*.schema.json | Config, grant, and receipt contracts. |
| scripts/tests/test_airtravel_execution_*.py | Contract, provider, pipeline, and preflight tests. |
| docs/research/phd-proposal/2026-09-12-airtravel-api-*.md | Sanitized protocol, grant template, and review packet. |

## Task 1: Verify source and runtime bytes fail closed

**Files:**
- Modify: scripts/verify_text2uml_airtravel_runtime.py
- Modify: scripts/tests/test_verify_text2uml_airtravel_runtime.py

**Interfaces:**
- Consumes: ZIP, extracted source root, source manifest, amendment manifest, runtime root.
- Produces: structured source_archive, source_entries, source_to_runtime, runtime_pack, and reference_separation results.

- [ ] **Step 1: Write failing tests**

~~~
def test_verified_source_and_five_file_runtime_pass(tmp_path: Path) -> None:
    inputs = make_verified_inputs(tmp_path)
    result = verify_pack(**inputs)
    assert result["status"] == "PASS"
    assert result["source_entries"]["matched"] == 143
    assert result["runtime_pack"]["observed_count"] == 5

def test_archive_or_mapping_drift_blocks(tmp_path: Path) -> None:
    inputs = make_verified_inputs(tmp_path)
    inputs["archive"].write_bytes(b"changed")
    assert verify_pack(**inputs)["status"] == "BLOCKED"

    inputs = make_verified_inputs(tmp_path)
    amendment = read_json(inputs["amendment_manifest"])
    amendment["runtime_files"].append(dict(amendment["runtime_files"][0]))
    write_json(inputs["amendment_manifest"], amendment)
    assert verify_pack(**inputs)["source_to_runtime"]["byte_identical"] is False
~~~

Add cases for a wrong archive digest, missing/extra/mismatched source entry, duplicate ZIP member, duplicate source/runtime mapping, missing mapping, runtime extra/missing file, reference leakage, symlink/reparse path, and empty manifest.

- [ ] **Step 2: Verify failing state**

Run:

~~~
uv run python -m pytest -q -p no:cacheprovider scripts/tests/test_verify_text2uml_airtravel_runtime.py
~~~

Expected: failures because the current verifier has no archive/source/mapping interface.

- [ ] **Step 3: Implement four verifier layers**

~~~
def verify_source_archive(archive: Path, expected_sha256: str, expected_commit: str) -> dict[str, Any]:
    """Return archive digest, commit binding, member inventory, and PASS/BLOCKED status."""

def verify_source_entries(source_root: Path, source_manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Compare every expected AirTravel source entry by path, byte length, and SHA-256."""

def verify_source_to_runtime_mapping(source_root: Path, runtime_root: Path, amendment: Mapping[str, Any]) -> dict[str, Any]:
    """Require exactly five unique byte-identical source-to-runtime mappings."""

def verify_runtime_pack(runtime_root: Path, amendment: Mapping[str, Any]) -> dict[str, Any]:
    """Require the exact five runtime files, allowed configuration, and no reference leakage."""
~~~

Require exactly five unique source paths and runtime paths: one domain description and four candidate models. Require byte length, SHA-256, and declared byte_transformation of NONE to match. Any extra, duplicate, missing, link/reparse point, or reference byte changes the overall status to BLOCKED.

- [ ] **Step 4: Pass tests and commit**

~~~
uv run python -m pytest -q -p no:cacheprovider scripts/tests/test_verify_text2uml_airtravel_runtime.py
uv run ruff check scripts/verify_text2uml_airtravel_runtime.py scripts/tests/test_verify_text2uml_airtravel_runtime.py
git add scripts/verify_text2uml_airtravel_runtime.py scripts/tests/test_verify_text2uml_airtravel_runtime.py
git commit -m "feat: verify AirTravel source and runtime bytes"
~~~

## Task 2: Add execution contracts, schemas, grants, and containment

**Files:**
- Create: schemas/airtravel-api-execution-config-v1.schema.json
- Create: schemas/airtravel-api-execution-grant-v1.schema.json
- Create: schemas/airtravel-api-execution-receipt-v1.schema.json
- Create: scripts/airtravel_execution_contract.py
- Create: scripts/tests/test_airtravel_execution_contract.py

**Interfaces:**
- Consumes: verified public input, canonical config JSON, private grant JSON, Git SHA, and run_id.
- Produces: immutable config/manifest/grant objects, a private empty output root, and a receipt skeleton.

- [ ] **Step 1: Write failing contract tests**

~~~
def test_grant_binds_config_manifest_and_commit(tmp_path: Path) -> None:
    config = make_config(model="test-model", max_usd="6.00")
    manifest = build_test_manifest(config)
    grant = make_grant(config=config, manifest=manifest, commit="a" * 40)
    validate_execution_grant(grant, config=config, manifest=manifest, current_commit="a" * 40)

    altered = replace(config, concurrency=2)
    with pytest.raises(GrantValidationError, match="configuration hash"):
        validate_execution_grant(grant, config=altered, manifest=manifest, current_commit="a" * 40)

def test_private_root_rejects_escape_and_reuse(tmp_path: Path) -> None:
    root = tmp_path / "external_data" / "airtravel-api-runs"
    assert_private_empty_run_root(root, "run-001")
    (root / "run-001" / "receipt.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ContainmentError):
        assert_private_empty_run_root(root, "run-001")
    for run_id in ("../x", "C:/outside", "run/child", "run-001 "):
        with pytest.raises(ContainmentError):
            assert_safe_run_id(run_id)
~~~

Also test missing, expired, replayed, wrong-mode, wrong-host, wrong-model, wrong-command, wrong-cap, symlink/reparse, sibling, case-fold collision, and schema-invalid grants.

- [ ] **Step 2: Verify the tests fail**

~~~
uv run python -m pytest -q -p no:cacheprovider scripts/tests/test_airtravel_execution_contract.py
~~~

Expected: imports fail before the module and schemas exist.

- [ ] **Step 3: Implement canonical contract functions**

~~~
@dataclass(frozen=True)
class ExecutionConfig:
    """Frozen public configuration: model, timeout, retries, concurrency, caps, and provider host."""

@dataclass(frozen=True)
class VerifiedInputManifest:
    """Self-binding record for exact archive, five runtime files, source mapping, configuration, and code."""

@dataclass(frozen=True)
class ExecutionGrant:
    """One-time private authorization binding a config, manifest, commit, command, and output root."""

def canonical_json_sha256(value: Mapping[str, Any]) -> str:
    """Serialize JSON canonically and return its SHA-256 digest."""

def build_input_manifest(*, verification: Mapping[str, Any], config: ExecutionConfig, code_sha: str) -> VerifiedInputManifest:
    """Build the prospective input binding before provider construction."""

def assert_safe_run_id(value: str) -> str:
    """Reject unsafe, empty, case-colliding, traversal, absolute, or separator-containing identifiers."""

def assert_private_empty_run_root(root: Path, run_id: str) -> Path:
    """Return the single approved empty private output directory or raise ContainmentError."""

def command_fingerprint(command: Sequence[str]) -> str:
    """Return SHA-256 over the complete normalized command vector."""

def validate_execution_grant(grant: ExecutionGrant, *, config: ExecutionConfig, manifest: VerifiedInputManifest, current_commit: str, command: Sequence[str]) -> None:
    """Fail closed unless every one-time grant binding exactly matches the requested execute mode."""
~~~

Use Decimal values encoded as canonical decimal strings. The grant schema requires nonce, invocation ID, exact execute mode, issued/expiry UTC timestamps, code/input/config hashes, model/host, price schedule hash, timeout/retry/concurrency/call/output caps, command fingerprint, relative private root, and consumed=false. Mark the grant consumed with a private exclusive attempt marker before provider construction; deletion of output cannot undo the attempt.

- [ ] **Step 4: Implement a controlled receipt vocabulary**

Require technical_error_code to be one of NONE, GRANT_INVALID, BUDGET_EXCEEDED, CALL_CAP_EXCEEDED, TIMEOUT, MALFORMED_RESPONSE, EGRESS_BLOCKED, or INTERNAL_FAILURE. The receipt includes safe hashes and counters but excludes private prompt/answer/exception content.

- [ ] **Step 5: Pass tests and commit**

~~~
uv run python -m pytest -q -p no:cacheprovider scripts/tests/test_airtravel_execution_contract.py
uv run ruff check scripts/airtravel_execution_contract.py scripts/tests/test_airtravel_execution_contract.py
git add schemas/airtravel-api-execution-*.schema.json scripts/airtravel_execution_contract.py scripts/tests/test_airtravel_execution_contract.py
git commit -m "feat: add AirTravel execution contracts"
~~~

## Task 3: Derive bounds and enforce budgeted provider access

**Files:**
- Modify: scripts/study1_call_bound.py
- Modify: scripts/tests/test_study1_call_bound.py
- Create: scripts/airtravel_execution_provider.py
- Create: scripts/tests/test_airtravel_execution_provider.py

**Interfaces:**
- Consumes: immutable config, validated grant, physical request label, and a privacy-safe prompt descriptor.
- Produces: fake/provider response records and precise call/token/cost ledger entries.

- [ ] **Step 1: Write failing bound and adapter tests**

~~~
@pytest.mark.parametrize(("n", "minimum", "maximum"), [(0, 4, 82), (1, 7, 143), (4, 16, 326)])
def test_call_site_plan_derives_bounds(n: int, minimum: int, maximum: int) -> None:
    bound = derive_call_bounds(n)
    assert bound["minimum_calls"] == minimum
    assert bound["worst_case_calls"] == maximum

async def test_every_physical_attempt_reserves_budget() -> None:
    provider = DeterministicFakeProvider(["timeout", "ok"])
    ledger = BudgetLedger(max_usd=Decimal("6.00"), reserve_per_attempt=Decimal("0.25"), max_calls=2)
    with pytest.raises(TechnicalProviderFailure, match="TIMEOUT"):
        await guarded_call(provider, ledger, label="first")
    await guarded_call(provider, ledger, label="second")
    assert ledger.physical_call_count == 2
~~~

Test reservation failure before the first request, cap breach, timeout, explicit retry, malformed output, alternate host, proxy, redirect, IP literal, socket bypass attempt, and OpenAI SDK automatic retries set to zero.

- [ ] **Step 2: Verify failures**

~~~
uv run python -m pytest -q -p no:cacheprovider scripts/tests/test_study1_call_bound.py scripts/tests/test_airtravel_execution_provider.py
~~~

- [ ] **Step 3: Make the call derivation inspectable**

Add a frozen CallSite dataclass and CALL_SITES sequence. Derive minimum 4 + 3N from phase 1 = 1, phase 2 = 1, phase 3 = 3N, phase 4 = 2. Derive worst case 82 + 61N from declared branch multiplicities. Preserve N=4 to 16/326 tests and return BLOCKED if the static source check cannot find its protected call-site labels.

- [ ] **Step 4: Implement an execute-only provider module**

~~~
class ProviderProtocol(Protocol):
    async def call(self, prompt: Mapping[str, str], *, label: str) -> Mapping[str, Any]:
        """Return the constrained provider response for one already-reserved physical call."""

class DeterministicFakeProvider:
    """Local deterministic test double; imports neither OpenAI nor networking modules."""
class OpenAIProvider:
    @classmethod
    def construct_after_grant(cls, config: ExecutionConfig, ledger: BudgetLedger) -> "OpenAIProvider":
        """Construct only after a validated execute grant and budget reservation interface exist."""
~~~

No client is constructed at import time. OpenAIProvider fixes the base URL to https://api.openai.com/v1, rejects all override/proxy/redirect endpoints, disables SDK automatic retries, reserves cost before every physical call, and maps failures to a controlled code. The fake provider imports neither openai nor network modules and reports external_provider_call_count=0.

- [ ] **Step 5: Pass tests and commit**

~~~
uv run python -m pytest -q -p no:cacheprovider scripts/tests/test_study1_call_bound.py scripts/tests/test_airtravel_execution_provider.py
uv run ruff check scripts/study1_call_bound.py scripts/airtravel_execution_provider.py scripts/tests/test_study1_call_bound.py scripts/tests/test_airtravel_execution_provider.py
git add scripts/study1_call_bound.py scripts/tests/test_study1_call_bound.py scripts/airtravel_execution_provider.py scripts/tests/test_airtravel_execution_provider.py
git commit -m "feat: enforce AirTravel call and budget bounds"
~~~

## Task 4: Implement the isolated Q&A lifecycle pipeline

**Files:**
- Create: scripts/airtravel_execution_pipeline.py
- Create: scripts/tests/test_airtravel_execution_pipeline.py

**Interfaces:**
- Consumes: verified frame, config, provider protocol, and QACommunicationRecorder.
- Produces: private qa_events.jsonl, a private pipeline manifest, lifecycle projections, and no automatic Agent-4 queue.

- [ ] **Step 1: Write failing lifecycle tests**

~~~
async def test_two_concurrent_cases_keep_stable_episode_identity() -> None:
    result = await run_fixture(case_ids=["01", "02"], rounds=2)
    episodes = build_episode_projection(load_event_stream(result.qa_events_path))
    assert len(episodes) == 2
    assert all(e["question_count"] == e["answer_count"] == 2 for e in episodes)
    assert len({e["episode_id"] for e in episodes}) == 2

def test_cross_episode_or_missing_answer_is_technical_incomplete() -> None:
    result = run_malformed_fixture("cross_episode_answer")
    assert result.receipt["technical_error_code"] == "MALFORMED_RESPONSE"
    assert result.episode_status == "INCOMPLETE_TECHNICAL"
~~~

Cover duplicate answers, post-termination events, zero-Q&A output, CONVERGED, TERMINATED_MAX_ROUNDS, INCOMPLETE_TECHNICAL, and failure of any fixture-question fallback.

- [ ] **Step 2: Verify failures**

~~~
uv run python -m pytest -q -p no:cacheprovider scripts/tests/test_airtravel_execution_pipeline.py
~~~

- [ ] **Step 3: Implement stable identity and actual Q&A correlation**

~~~
def stable_episode_id(*, run_id: str, setting_id: str, source_agent: str, stage: str,
                      skill: str, target_agent: str, scope: str, case_id: str | None,
                      guideline_id: str | None, pattern_id: str | None) -> str:
    """Hash the frozen episode identity tuple; round index is deliberately excluded."""

async def route_question_answer(*, asking_agent: str, answering_agent: str, case_id: str,
                                stage: str, skill: str, scope: str,
                                question_text: str, provider: ProviderProtocol,
                                recorder: QACommunicationRecorder) -> None:
    """Persist a real generated question, correlate its exact returned answer, then validate lifecycle state."""

async def run_airtravel_pipeline(*, config: ExecutionConfig, provider: ProviderProtocol,
                                 recorder: QACommunicationRecorder,
                                 runtime_root: Path) -> PipelineResult:
    """Run the isolated four-case AirTravel workflow and emit private, schema-valid artifacts."""
~~~

Use actual generated question text when calling `recorder.emit_question`. Call `recorder.emit_answer(question=question_event, answer_text=provider_answer_text, answer_confidence=provider_answer_confidence, evidence_ref=provider_evidence_ref)` only for that returned answer. Preserve asking agent, answering agent, case, stage, skill, and round on each event. Close unfinished episodes in finally with INCOMPLETE_TECHNICAL. Do not write an Agent-4 queue; report it as NOT_AVAILABLE unless a separately validated artifact exists.

- [ ] **Step 4: Apply unchanged Detector-v1 only after validation**

After load_event_stream succeeds, call existing extract_live_corpus and persist its result privately. Tests must prove C1, C2, C3, Alternative, and Non-Satisfied never become Detector-v1 reasons.

- [ ] **Step 5: Pass tests and commit**

~~~
uv run python -m pytest -q -p no:cacheprovider scripts/tests/test_airtravel_execution_pipeline.py VEGO-AI/tests/test_qa_communication.py
uv run ruff check scripts/airtravel_execution_pipeline.py scripts/tests/test_airtravel_execution_pipeline.py
git add scripts/airtravel_execution_pipeline.py scripts/tests/test_airtravel_execution_pipeline.py
git commit -m "feat: add isolated AirTravel Q&A pipeline"
~~~

## Task 5: Compose the gate and CLI modes

**Files:**
- Create: scripts/study1_external_execution_gate.py
- Create: scripts/study1_airtravel_external_runner.py
- Create: scripts/tests/test_study1_external_execution_gate.py

**Interfaces:**
- Consumes: mode, verification, config, manifest, optional grant, current commit.
- Produces: explicit gate decision and private receipt.

- [ ] **Step 1: Write failing mode tests**

~~~
def test_prepare_and_preflight_cannot_construct_openai(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(provider, "OpenAIProvider", FailIfConstructed)
    assert main(["prepare", *fixture_args(tmp_path)]) == 0
    assert main(["preflight", *fixture_args(tmp_path)]) == 0

def test_execute_requires_fresh_exact_grant_before_network(tmp_path: Path) -> None:
    for grant in (None, expired_grant(), replayed_grant(), wrong_manifest_grant()):
        decision = evaluate_gate(mode="execute", grant=grant, **verified_fixture(tmp_path))
        assert decision["status"] == "BLOCKED"
        assert decision["provider_construction_permitted"] is False
~~~

- [ ] **Step 2: Implement the composition gate**

~~~
def evaluate_gate(*, mode: Literal["prepare", "preflight", "execute"],
                  config: ExecutionConfig, verification: Mapping[str, Any],
                  input_manifest: VerifiedInputManifest | None,
                  grant: ExecutionGrant | None, current_commit: str) -> dict[str, Any]:
    """Return a fail-closed status; only execute may permit provider construction."""

def require_execute_authorization(decision: Mapping[str, Any]) -> None:
    """Raise before any provider construction unless the gate has explicitly permitted execution."""
~~~

prepare verifies public bytes and writes the private input manifest. preflight requires that manifest and only allows DeterministicFakeProvider. execute requires all verification plus a matching, unexpired, unused grant before it may call OpenAIProvider.construct_after_grant.

- [ ] **Step 3: Implement the CLI with safe argument boundaries**

~~~
prepare   --config <private-config> --archive <ignored-archive> --source-root <ignored-root> --runtime-root <ignored-root> --amendment <tracked-amendment> --private-root external_data/airtravel-api-runs --run-id <safe-id>
preflight --config <private-config> --input-manifest <private-manifest> --private-root external_data/airtravel-api-runs --run-id <safe-id>
execute   --config <private-config> --input-manifest <private-manifest> --grant <private-grant> --private-root external_data/airtravel-api-runs --run-id <safe-id>
~~~

Reject absolute escape, traversal, symlink/reparse, nonempty/reused roots, and unapproved arguments. Print only compact status and a safe receipt hash; never prompt/answer/grant/API-key content.

- [ ] **Step 4: Pass focused tests and commit**

~~~
uv run python -m pytest -q -p no:cacheprovider scripts/tests/test_study1_external_execution_gate.py scripts/tests/test_airtravel_execution_contract.py scripts/tests/test_airtravel_execution_provider.py scripts/tests/test_airtravel_execution_pipeline.py
uv run ruff check scripts/study1_external_execution_gate.py scripts/study1_airtravel_external_runner.py scripts/tests/test_study1_external_execution_gate.py
git add scripts/study1_external_execution_gate.py scripts/study1_airtravel_external_runner.py scripts/tests/test_study1_external_execution_gate.py
git commit -m "feat: gate AirTravel provider execution"
~~~

## Task 6: Publish sanitized protocol and prepare review packet

**Files:**
- Create: docs/research/phd-proposal/2026-09-12-airtravel-api-execution-protocol.md
- Create: docs/research/phd-proposal/2026-09-12-airtravel-api-execution-grant-template.md
- Create: docs/research/phd-proposal/2026-09-12-airtravel-api-preflight-review-packet.md
- Modify: scripts/tests/test_airtravel_execution_contract.py

**Interfaces:**
- Consumes: exact implementation SHA, verification/preflight receipts, config interface, and blank authorization template.
- Produces: review-ready, no-secret documentation with no measured result.

- [ ] **Step 1: Write safety assertions**

~~~
def test_public_protocol_preserves_boundaries() -> None:
    text = PROTOCOL.read_text(encoding="utf-8")
    assert "VEGO ZIP" in text and "not sent to an external provider" in text
    assert "QuRE" in text and "NOT_ADMITTED" in text
    assert "does not establish accuracy" in text
    assert "<API_KEY>" not in text
    assert "external_data/airtravel-api-runs/<run_id>" not in text
~~~

- [ ] **Step 2: Write sanitized documents**

The protocol specifies public AirTravel only, N=4, reference exclusion, $6 ceiling, prepare to preflight to execute, Detector-v1 claim boundary, and zero automatic correction. The blank grant requires a human-provided model, dated price source, caps, command fingerprint, output root, expiration, and one-time nonce. It explicitly does not authorize VEGO ZIP or QuRE.

- [ ] **Step 3: Run all release checks**

~~~
uv run python -m pytest -q -p no:cacheprovider scripts/tests/test_verify_text2uml_airtravel_runtime.py scripts/tests/test_study1_call_bound.py scripts/tests/test_airtravel_execution_contract.py scripts/tests/test_airtravel_execution_provider.py scripts/tests/test_airtravel_execution_pipeline.py scripts/tests/test_study1_external_execution_gate.py
uv run python -m pytest scripts/tests -q -p no:cacheprovider
uv run python -m pytest VEGO-AI/tests -q -p no:cacheprovider
uv run python -m pytest tests/hlayer_offline -q -p no:cacheprovider
uv run python -m compileall -q VEGO-AI/framework VEGO-AI/eval VEGO-AI/analysis scripts src
uv run ruff check scripts src
uv run python scripts/check_repository_privacy.py
uv run python scripts/security_audit.py --history
uv run python scripts/check_evidence_consistency.py --check
git diff --check "$(git merge-base origin/main HEAD)" HEAD
~~~

Expected: all pass. Any failure yields TECHNICAL_NO_GO and blocks a real run.

- [ ] **Step 4: Prepare, but do not execute, the deterministic fake-provider preflight**

~~~
uv run python scripts/study1_airtravel_external_runner.py preflight --config <private-config> --input-manifest <private-manifest> --private-root external_data/airtravel-api-runs --run-id preflight-<safe-id>
~~~

Do **not** run this exact command during implementation. Include it verbatim in the review packet, together with the expected private engineering receipt fields (`external_provider_call_count=0`, zero scientific results, and zero API calls). The exact preflight remains blocked until a human signs a fresh, hash-bound local fake-preflight authorization after code review and CI are green.

- [ ] **Step 5: Commit, push a draft PR, and request a fresh grant**

~~~
git add docs/research/phd-proposal/2026-09-12-airtravel-api-*.md scripts/tests/test_airtravel_execution_contract.py
git commit -m "docs: prepare AirTravel API preflight review packet"
git pull --rebase origin main
git push -u origin feature/airtravel-api-preflight-gate
~~~

Open a draft PR. Do not merge, execute the exact fake preflight, or execute against a real provider until independent review is green and a human returns the applicable fresh, hash-bound authorization. A real-provider authorization is always distinct from any local fake-preflight authorization.

## Plan Self-Review

- **Spec coverage:** Tasks 1–5 implement public provenance verification, private contracts, global call/cost/egress controls, Q&A lifecycle, and mode gates. Task 6 preserves the public claim/data boundary and packages the future authorization request.
- **No-placeholder check:** Every task names files, interfaces, commands, expected outcomes, and test cases. Angle-bracket CLI values intentionally denote ignored local inputs and are never tracked artifacts.
- **Type consistency:** ExecutionConfig, VerifiedInputManifest, ExecutionGrant, ProviderProtocol, and the three mode names are introduced before their consuming tasks.
