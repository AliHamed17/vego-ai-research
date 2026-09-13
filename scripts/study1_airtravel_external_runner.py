"""Strict prepare/preflight/execute CLI. No provider imports until authorization.

The canonical command is exactly the mode-and-options argv passed to main (no
launcher). Preflight authorization is supplied separately at the fixed private
manifest sibling `fake_preflight_authorization.json`; no execute grant option
is accepted in preflight. This module does not create authorization artifacts.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import sys
from pathlib import Path

import airtravel_execution_contract as contract
import study1_external_execution_gate as gate
import verify_text2uml_airtravel_runtime as verifier


def _verification_inputs(manifest):
    values = dict(manifest.verification_inputs)
    if set(values) != gate.VERIFICATION_KEYS:
        raise contract.ContractValidationError("verification paths are missing")
    paths = {
        key: gate.checked_input(value, directory=key.endswith("root"))
        for key, value in values.items()
    }
    # Public source pack is ignored; the approved amendment is tracked.
    for key, path in paths.items():
        relative = path.relative_to(contract.REPOSITORY_ROOT).as_posix()
        tracked = contract._git("ls-files", "--", relative)
        if key == "amendment_manifest":
            if tracked.returncode or tracked.stdout.strip() != relative:
                raise contract.ContractValidationError("amendment must be tracked")
            gate.assert_committed_file(relative, gate.current_commit())
        elif (
            tracked.returncode
            or tracked.stdout.strip()
            or contract._git("check-ignore", "--no-index", "--quiet", "--", relative).returncode
        ):
            raise contract.ContainmentError("source input must be ignored and untracked")
    return paths


def _frame(manifest, paths, run_id):
    from airtravel_execution_pipeline import PipelineCase, VerifiedPipelineFrame

    values = {}
    for binding in manifest.runtime_files:
        relative = (
            (paths["runtime_root"] / binding.path).relative_to(contract.REPOSITORY_ROOT).as_posix()
        )
        path = gate.checked_input(relative)
        raw = path.read_bytes()
        if len(raw) != binding.bytes or hashlib.sha256(raw).hexdigest() != binding.sha256:
            raise contract.ContractValidationError("runtime snapshot changed")
        values[binding.path] = raw.decode("utf-8")
    candidates = sorted(name for name in values if name.startswith("candidate_models/"))
    domain = next(values[name] for name in values if name.startswith("domain_description/"))
    return VerifiedPipelineFrame(
        run_id=run_id,
        setting_id="cd_airtravel",
        corpus_id="text2uml_airtravel_253b26dc",
        input_manifest=manifest,
        domain_description=domain,
        cases=tuple(
            PipelineCase(f"{index:02}", name, values[name])
            for index, name in enumerate(candidates, 1)
        ),
        max_rounds=manifest.max_rounds,
    )


async def _run(*, mode, config, manifest, paths, root, decision, grant, command, ledger):
    gate.authorize_invocation(
        decision,
        mode=mode,
        config=config,
        manifest=manifest,
        command=command,
        run_root=root,
        grant=grant,
    )
    from airtravel_execution_pipeline import QACommunicationRecorder, run_airtravel_pipeline
    from airtravel_execution_provider import DeterministicFakeProvider

    frame = _frame(manifest, paths, root.name)
    provider = None
    try:
        if mode == "preflight":
            rows = []
            for _ in range(4):
                rows.append(
                    {
                        "output": {"context": "Local fake context."},
                        "input_tokens": 10,
                        "output_tokens": 5,
                    }
                )
                rows.extend(
                    {
                        "output": {
                            "stage_output": "Local fake output.",
                            "complete": True,
                            "questions": [],
                        },
                        "input_tokens": 10,
                        "output_tokens": 5,
                    }
                    for _ in range(3)
                )
            provider = DeterministicFakeProvider(rows)
            if type(provider) is not DeterministicFakeProvider:
                raise contract.GrantValidationError("non-fake preflight provider")
        else:
            if gate.current_commit() != manifest.code_sha:
                raise contract.GrantValidationError("code changed before construction")
            from airtravel_execution_provider import OpenAIProvider

            provider = OpenAIProvider.construct_after_grant(
                config,
                ledger,
                grant=grant,
                manifest=manifest,
                current_commit=manifest.code_sha,
                command=command,
            )
        return await run_airtravel_pipeline(
            config=config,
            frame=frame,
            provider=provider,
            recorder=QACommunicationRecorder(root / "qa_events.jsonl", run_id=root.name),
            ledger=ledger,
            runtime_root=root,
            max_rounds=config.max_rounds,
        )
    finally:
        if mode == "execute" and provider is not None:
            await provider.aclose()


def main(argv=None) -> int:
    """Print only compact status/hash; never exception text or input payloads."""
    command = list(sys.argv[1:] if argv is None else argv)
    root = config = manifest = ledger = pipeline = None
    status, code, receipt_hash = "BLOCKED", "GRANT_INVALID", None
    mode = "prepare"
    try:
        parsed = gate.parse_complete_command(command)
        mode = parsed["mode"]
        root = contract.assert_private_empty_run_root(
            Path(parsed["private_root"]), parsed["run_id"]
        )
        config = contract.ExecutionConfig.from_json(
            gate.checked_input(parsed["config"], private=True)
        )
        commit = gate.current_commit()
        if mode == "prepare":
            locations = tuple(
                sorted(
                    ("amendment_manifest" if key == "amendment" else key, value)
                    for key, value in parsed.items()
                    if key in gate.VERIFICATION_KEYS or key == "amendment"
                )
            )

            # A path container only; no unverified manifest is accepted as proof.
            class Locations:
                verification_inputs = locations

            paths = _verification_inputs(Locations())
            verification = verifier.verify_pack(**paths)
            manifest = contract.build_input_manifest(
                verification=verification,
                config=config,
                code_sha=commit,
                verification_inputs=locations,
            )
            decision = gate.evaluate_gate(
                mode=mode,
                config=config,
                verification=verification,
                input_manifest=manifest,
                grant=None,
                current_commit=commit,
                command=command,
            )
            if decision["status"] != "PASS":
                code = decision["technical_error_code"]
                raise contract.GrantValidationError("prepare blocked")
            gate.write_private(root, "input_manifest.json", manifest.to_dict(), immutable=True)
        else:
            manifest_path = gate.checked_input(parsed["input_manifest"], private=True)
            manifest = contract.VerifiedInputManifest.from_dict(contract._load_json(manifest_path))
            paths = _verification_inputs(manifest)
            verification = verifier.verify_pack(**paths)
            authorization_path = (
                parsed["grant"]
                if mode == "execute"
                else (manifest_path.parent / "fake_preflight_authorization.json")
                .relative_to(contract.REPOSITORY_ROOT)
                .as_posix()
            )
            raw = contract._load_json(gate.checked_input(authorization_path, private=True))
            grant = contract.ExecutionGrant.from_dict(raw) if mode == "execute" else raw
            decision = gate.evaluate_gate(
                mode=mode,
                config=config,
                verification=verification,
                input_manifest=manifest,
                grant=grant,
                current_commit=commit,
                command=command,
                run_root=root,
            )
            if decision["status"] != "PASS":
                code = decision["technical_error_code"]
                raise contract.GrantValidationError("authorization blocked")
            from airtravel_execution_provider import BudgetLedger

            ledger = BudgetLedger(config)
            status, code = "INCOMPLETE_TECHNICAL", "INTERNAL_FAILURE"
            pipeline = asyncio.run(
                _run(
                    mode=mode,
                    config=config,
                    manifest=manifest,
                    paths=paths,
                    root=root,
                    decision=decision,
                    grant=grant,
                    command=command,
                    ledger=ledger,
                )
            )
        status, code = (
            (pipeline.status, pipeline.receipt["technical_error_code"])
            if pipeline
            else ("PASS", "NONE")
        )
    except (Exception, KeyboardInterrupt) as error:
        # Preserve provider denial only after authorization loaded this lane.
        # Prepare/preflight gate failures never trigger an SDK/provider import.
        if ledger is not None:
            from airtravel_execution_provider import receipt_error_code

            code = receipt_error_code(error)
    finally:
        if root is not None:
            try:
                if (
                    config is not None
                    and manifest is not None
                    and config.sha256 == manifest.config_sha256
                ):
                    receipt = gate.compose_receipt(
                        config=config,
                        manifest=manifest,
                        mode=mode,
                        run_root=root,
                        status=status,
                        code=code,
                        pipeline=pipeline,
                        ledger=ledger,
                    )
                else:
                    receipt = {
                        "schema_version": "airtravel-terminal-failure-v1",
                        "mode": mode,
                        "run_id": root.name,
                        "status": "BLOCKED",
                        "technical_error_code": code,
                        "external_provider_call_count": 0,
                        "scientific_result_count": 0,
                    }
                gate.write_private(root, "receipt.json", receipt)
                receipt_hash = contract.canonical_json_sha256(receipt)
            except Exception:
                status = "INCOMPLETE_TECHNICAL" if ledger is not None else "BLOCKED"
                # Full composition may fail while containment still permits a
                # compact terminal record. Never invent zero usage after calls.
                try:
                    receipt = {
                        "schema_version": "airtravel-terminal-failure-v1",
                        "mode": mode,
                        "run_id": root.name,
                        "status": status,
                        "technical_error_code": "INTERNAL_FAILURE",
                        "physical_call_count": ledger.physical_call_count if ledger else 0,
                        "external_provider_call_count": ledger.external_provider_call_count
                        if ledger
                        else 0,
                        "scientific_result_count": 0,
                    }
                    gate.write_private(root, "receipt.json", receipt)
                    receipt_hash = contract.canonical_json_sha256(receipt)
                except Exception:
                    receipt_hash = None
        print(json.dumps({"status": status, "receipt_sha256": receipt_hash}, separators=(",", ":")))
    return 0 if status == "PASS" and receipt_hash is not None else 2


if __name__ == "__main__":
    raise SystemExit(main())
