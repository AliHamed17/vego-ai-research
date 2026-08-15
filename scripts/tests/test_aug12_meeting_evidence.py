from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
import wave
from decimal import Decimal
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/build_aug12_meeting_evidence.py"
CONTROL_REGISTER = ROOT / "docs/research/meetings/2026-08-12-control-register.csv"
CROSSWALK = ROOT / "docs/research/meetings/2026-08-12-claude-id-crosswalk.csv"
HANDOFF = ROOT / "docs/research/meetings/2026-08-12-claude-draft-handoff-manifest.json"
SPEC = importlib.util.spec_from_file_location("build_aug12_meeting_evidence", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

PRODUCTION_SOURCE_PROFILE = dict(getattr(MODULE, "AUG12_SOURCE_PROFILE", {}))
TEST_SOURCE_PROFILE = {
    "profile_id": "fixture-profile-v1",
    "media_duration_seconds": "10.000",
    "raw_audio_sha256": hashlib.sha256(b"audio").hexdigest().upper(),
    "raw_audio_bytes": 5,
    "raw_video_sha256": hashlib.sha256(b"video").hexdigest().upper(),
    "raw_video_bytes": 5,
    "encoded_packet_sha256": "A" * 64,
    "packet_timing_sha256": "B" * 64,
    "canonical_pcm_sha256": "C" * 64,
    "canonical_pcm_samples": 160_000,
}
PRIVATE_ARTIFACT_ROLES = (
    "raw_audio",
    "raw_video",
    "raw_chat",
    "recording_config",
    "hebrew_asr",
    "hebrew_asr_readable",
    "asr_generator_script",
    "asr_task_log",
    "media_comparison",
    "media_fingerprint_generator",
    "media_fingerprint_task_log",
    "machine_english",
    "translation_event_log",
    "translation_generator_script",
    "translation_attempt_01_partial",
    "translation_attempt_01_event_log",
    "translation_comparison_generator",
    "translation_comparison_report",
)


@pytest.fixture(autouse=True)
def use_controlled_fixture_media_profile(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture_asr = (os.linesep.join(raw_lines()) + os.linesep).encode("utf-8")
    fixture_controls = os.linesep.join(
        (
            "Control_ID,Type,Summary,Source_Spans,Evidence_Basis,Implementation_Status,Acceptance_Status,Notes",
            'F12-001,Finding,Fixture finding,S12-0001--S12-0003,Fixture,Pending,Pending,""',
            'A12-001,Action,Fixture action,S12-0002,Fixture,Pending,Pending,""',
            "",
        )
    ).encode("utf-8")
    profile = {
        **TEST_SOURCE_PROFILE,
        "raw_chat_sha256": hashlib.sha256(b"chat").hexdigest().upper(),
        "raw_chat_bytes": 4,
        "recording_config_sha256": hashlib.sha256(b"config").hexdigest().upper(),
        "recording_config_bytes": 6,
        "hebrew_asr_sha256": hashlib.sha256(fixture_asr).hexdigest().upper(),
        "hebrew_asr_bytes": len(fixture_asr),
        "hebrew_asr_segment_count": 3,
        "hebrew_asr_schema": "jsonl:start,end,text:v1",
        "hebrew_asr_readable_sha256": hashlib.sha256(b"readable").hexdigest().upper(),
        "hebrew_asr_readable_bytes": 8,
        "asr_generator_script_sha256": hashlib.sha256(b"script").hexdigest().upper(),
        "asr_generator_script_bytes": 6,
        "asr_task_log_sha256": hashlib.sha256(b"log").hexdigest().upper(),
        "asr_task_log_bytes": 3,
        "asr_model_repository": "fixture/model",
        "asr_model_name": "fixture",
        "asr_model_snapshot_commit": "1" * 40,
        "asr_model_snapshot_tree_sha256": "1" * 64,
        "asr_model_blob_sha256": hashlib.sha256(b"asr-model").hexdigest().upper(),
        "asr_model_blob_bytes": 9,
        "control_register_sha256": hashlib.sha256(fixture_controls).hexdigest().upper(),
        "control_register_bytes": len(fixture_controls),
    }
    monkeypatch.setattr(MODULE, "AUG12_SOURCE_PROFILE", profile, raising=False)
    monkeypatch.setattr(MODULE, "RECOMPUTE_MEDIA_FINGERPRINTS", False, raising=False)


def raw_lines() -> list[str]:
    return [
        json.dumps({"start": 1.01, "end": 2.0, "text": "שלום"}, ensure_ascii=False),
        json.dumps({"start": 2.5, "end": 4.0, "text": "עולם"}, ensure_ascii=False),
        json.dumps({"start": 4.0, "end": 9.482, "text": "סיום"}, ensure_ascii=False),
    ]


def fixture_hf_cache_root(private_root: Path) -> Path:
    return private_root / "hf-cache"


def fixture_ollama_cache_root(private_root: Path) -> Path:
    return private_root / "ollama-cache"


def private_provenance(tmp_path: Path, source: Path) -> Path:
    fixture_ollama_cache_root(tmp_path).mkdir(parents=True, exist_ok=True)
    artifacts: list[dict[str, object]] = []
    artifact_paths: dict[str, Path] = {}
    for role, name, payload in (
        ("raw_audio", "source.m4a", b"audio"),
        ("raw_video", "source.mp4", b"video"),
        ("raw_chat", "chat.txt", b"chat"),
        ("recording_config", "recording.conf", b"config"),
        ("asr_generator_script", "transcribe.py", b"script"),
        ("asr_task_log", "transcribe.log", b"log"),
        ("media_fingerprint_generator", "fingerprint.py", b"fingerprint-script"),
        ("media_fingerprint_task_log", "fingerprint.log", b"fingerprint-log"),
    ):
        path = tmp_path / name
        path.write_bytes(payload)
        artifact_paths[role] = path
        artifacts.append(
            {
                "role": role,
                "path": str(path.resolve()),
                "bytes": path.stat().st_size,
                "sha256": MODULE.sha256_file(path),
            }
        )
    asr_model_path = (
        fixture_hf_cache_root(tmp_path)
        / "models--fixture--model"
        / "blobs"
        / str(MODULE.AUG12_SOURCE_PROFILE["asr_model_blob_sha256"]).lower()
    )
    asr_model_path.parent.mkdir(parents=True)
    asr_model_path.write_bytes(b"asr-model")
    artifact_paths["asr_model_blob"] = asr_model_path
    artifacts.append(
        {
            "role": "asr_model_blob",
            "path": str(asr_model_path.resolve()),
            "bytes": asr_model_path.stat().st_size,
            "sha256": MODULE.sha256_file(asr_model_path),
        }
    )
    fingerprint = {
        "encoded_packet_sha256": "A" * 64,
        "packet_timing_sha256": "B" * 64,
        "canonical_pcm_sha256": "C" * 64,
        "canonical_pcm_samples": 160_000,
        "canonical_pcm_rate_hz": 16_000,
        "canonical_pcm_channels": 1,
        "canonical_pcm_format": "s16le",
        "audio_stream_count": 1,
        "audio_codec": "aac",
        "duration_seconds": 10.0,
    }
    primary = {
        **fingerprint,
        "source_name": artifact_paths["raw_audio"].name,
        "source_bytes": artifact_paths["raw_audio"].stat().st_size,
        "source_sha256": MODULE.sha256_file(artifact_paths["raw_audio"]),
    }
    secondary = {
        **fingerprint,
        "source_name": artifact_paths["raw_video"].name,
        "source_bytes": artifact_paths["raw_video"].stat().st_size,
        "source_sha256": MODULE.sha256_file(artifact_paths["raw_video"]),
    }
    comparison_path = tmp_path / "audio-comparison.json"
    comparison_path.write_text(
        json.dumps(
            {
                "schema_version": "Aug12MeetingAudioComparison-v1",
                "primary": primary,
                "secondary": secondary,
                "audio_evidence_equivalent": True,
                "differences": [],
            }
        ),
        encoding="utf-8",
    )
    artifacts.append(
        {
            "role": "media_comparison",
            "path": str(comparison_path.resolve()),
            "bytes": comparison_path.stat().st_size,
            "sha256": MODULE.sha256_file(comparison_path),
        }
    )
    readable_asr = tmp_path / "machine-transcript.he.txt"
    readable_asr.write_bytes(b"readable")
    artifacts.append(
        {
            "role": "hebrew_asr_readable",
            "path": str(readable_asr.resolve()),
            "bytes": readable_asr.stat().st_size,
            "sha256": MODULE.sha256_file(readable_asr),
        }
    )
    control_register = tmp_path / "control-register.csv"
    control_register.write_text(
        "Control_ID,Type,Summary,Source_Spans,Evidence_Basis,Implementation_Status,Acceptance_Status,Notes\n"
        'F12-001,Finding,Fixture finding,S12-0001--S12-0003,Fixture,Pending,Pending,""\n'
        'A12-001,Action,Fixture action,S12-0002,Fixture,Pending,Pending,""\n',
        encoding="utf-8",
    )
    artifacts.append(
        {
            "role": "control_register",
            "path": str(control_register.resolve()),
            "bytes": control_register.stat().st_size,
            "sha256": MODULE.sha256_file(control_register),
        }
    )
    snapshot_commit = str(MODULE.AUG12_SOURCE_PROFILE["asr_model_snapshot_commit"])
    snapshot = (
        fixture_hf_cache_root(tmp_path)
        / "models--fixture--model"
        / "snapshots"
        / snapshot_commit
    )
    snapshot.mkdir(parents=True)
    (snapshot / "config.json").write_bytes(b"fixture-config")
    (snapshot / "model.bin").write_bytes(b"asr-model")
    fixture_profile = dict(MODULE.AUG12_SOURCE_PROFILE)
    fixture_profile["asr_model_snapshot_tree_sha256"] = MODULE.sha256_tree(snapshot)
    MODULE.AUG12_SOURCE_PROFILE = fixture_profile
    for role, path in (("hebrew_asr", source), ("evidence_builder", SCRIPT)):
        artifacts.append(
            {
                "role": role,
                "path": str(path.resolve()),
                "bytes": path.stat().st_size,
                "sha256": MODULE.sha256_file(path),
            }
        )
    provenance = {
        "schema_version": "Aug12MeetingPrivateProvenance-v1",
        "artifacts": artifacts,
        "media": {
            "source_profile_id": "fixture-profile-v1",
            "generator_script_role": "media_fingerprint_generator",
            "task_log_role": "media_fingerprint_task_log",
            "comparison_role": "media_comparison",
            "input_roles": ["raw_audio", "raw_video"],
            "command": {"argv": ["python", "fingerprint.py"], "exit_code": 0},
        },
        "asr": {
            "segment_count": 3,
            "output_schema": MODULE.AUG12_SOURCE_PROFILE["hebrew_asr_schema"],
            "model": {
                "name": "fixture",
                "repository": MODULE.AUG12_SOURCE_PROFILE["asr_model_repository"],
                "snapshot_commit": snapshot_commit,
                "snapshot_path": str(snapshot.resolve()),
                "snapshot_tree_sha256": MODULE.AUG12_SOURCE_PROFILE[
                    "asr_model_snapshot_tree_sha256"
                ],
                "blob_role": "asr_model_blob",
                "blob_sha256": MODULE.sha256_file(artifact_paths["asr_model_blob"]),
            },
            "generator_script_role": "asr_generator_script",
            "task_log_role": "asr_task_log",
            "source_role": "raw_audio",
            "output_role": "hebrew_asr",
            "readable_output_role": "hebrew_asr_readable",
            "command": {"argv": ["python", "transcribe.py"], "exit_code": 0},
            "execution_record": {
                "record_type": "recovered-task-output-binding-v1",
                "source_sha256": MODULE.sha256_file(artifact_paths["raw_audio"]),
                "output_sha256": MODULE.sha256_file(source),
                "readable_output_sha256": MODULE.sha256_file(readable_asr),
                "generator_script_sha256": MODULE.sha256_file(
                    artifact_paths["asr_generator_script"]
                ),
                "task_log_sha256": MODULE.sha256_file(artifact_paths["asr_task_log"]),
                "model_snapshot_tree_sha256": MODULE.AUG12_SOURCE_PROFILE[
                    "asr_model_snapshot_tree_sha256"
                ],
                "model_blob_sha256": MODULE.sha256_file(
                    artifact_paths["asr_model_blob"]
                ),
                "segment_count": 3,
                "exit_code": 0,
            },
        },
        "translation": {"status": "not_started"},
        "builder": {
            "script_role": "evidence_builder",
            "command": {"argv": ["python", "build_aug12_meeting_evidence.py"]},
        },
    }
    path = tmp_path / "source-provenance.private.json"
    path.write_text(json.dumps(provenance), encoding="utf-8")
    return path


def build_package_contents(source_path: Path, **kwargs: object) -> dict[str, str]:
    provenance_path = Path(str(kwargs["provenance_path"]))
    allowed_root = Path(str(kwargs.pop("allowed_root", provenance_path.parent)))
    repo_root = Path(str(kwargs.pop("repo_root", ROOT)))
    hf_cache_root = Path(
        str(kwargs.pop("hf_cache_root", fixture_hf_cache_root(allowed_root)))
    )
    ollama_cache_root = Path(
        str(kwargs.pop("ollama_cache_root", fixture_ollama_cache_root(allowed_root)))
    )
    return MODULE.build_package_contents(
        source_path,
        **kwargs,
        allowed_root=allowed_root,
        repo_root=repo_root,
        hf_cache_root=hf_cache_root,
        ollama_cache_root=ollama_cache_root,
    )


def complete_translation_provenance(
    provenance_path: Path,
    source_rows: list[dict[str, object]],
) -> tuple[Path, Path]:
    translation = provenance_path.parent / "machine.en.jsonl"
    translation_rows = [
        {
            "Segment_ID": str(row["Segment_ID"]),
            "Machine_EN": f"EN-{row['Segment_ID']}",
            "Source_HE_SHA256": str(row["Source_HE_SHA256"]),
        }
        for row in source_rows
    ]
    translation.write_text(MODULE._render_jsonl(translation_rows), encoding="utf-8")
    digest = "a" * 64
    event_log = provenance_path.parent / "translation-events.jsonl"
    run_id = "fixture-run-01"
    events = [
        {
            "timestamp_utc": "2026-08-15T00:00:00+00:00",
            "run_id": run_id,
            "event": "translation_run_started",
            "source_name": provenance_path.parent.joinpath("machine.jsonl").name,
            "source_bytes": provenance_path.parent.joinpath("machine.jsonl").stat().st_size,
            "source_sha256": MODULE.sha256_file(provenance_path.parent / "machine.jsonl"),
            "source_segment_count": len(source_rows),
            "script_sha256": MODULE.sha256_file(SCRIPT),
            "model": "fixture:latest",
            "model_digest": digest,
            "options": MODULE.DEFAULT_OLLAMA_OPTIONS,
            "batch_size": 18,
            "timeout_seconds": 600,
            "translation_prompt_template_sha256": MODULE.sha256_text(
                MODULE.translation_prompt([])
            ),
        },
        {
            "timestamp_utc": "2026-08-15T00:01:00+00:00",
            "run_id": run_id,
            "event": "translation_run_completed",
            "translated_segment_count": len(source_rows),
            "output_bytes": translation.stat().st_size,
            "output_sha256": MODULE.sha256_file(translation),
        },
    ]
    event_log.write_text(MODULE._render_jsonl(events), encoding="utf-8")

    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    model_blob = (
        fixture_ollama_cache_root(provenance_path.parent)
        / "blobs"
        / f"sha256-{hashlib.sha256(b'ollama-model').hexdigest()}"
    )
    model_blob.parent.mkdir(parents=True, exist_ok=True)
    model_blob.write_bytes(b"ollama-model")
    model_manifest = (
        fixture_ollama_cache_root(provenance_path.parent)
        / "manifests"
        / "registry.ollama.ai"
        / "library"
        / "fixture"
        / "latest"
    )
    model_manifest.parent.mkdir(parents=True, exist_ok=True)
    model_manifest.write_text('{"model":"fixture:latest"}', encoding="utf-8")
    attempt_01 = provenance_path.parent / "attempt-01.partial.jsonl"
    attempt_01.write_text(
        MODULE._render_jsonl(
            [
                translation_rows[0],
                {**translation_rows[1], "Machine_EN": "changed-fixture"},
            ]
        ),
        encoding="utf-8",
    )
    attempt_01_events = provenance_path.parent / "attempt-01.events.jsonl"
    attempt_01_events.write_text('{"fixture":"event-bound"}\n', encoding="utf-8")
    comparison_generator = provenance_path.parent / "compare.py"
    comparison_generator.write_bytes(b"comparison-generator")
    translation_generator = provenance_path.parent / "translate.py"
    translation_generator.write_bytes(SCRIPT.read_bytes())
    comparison_report = provenance_path.parent / "comparison.json"
    comparison = {
        "schema_version": "Aug12TranslationAttemptComparison-v1",
        "method": "Compare two aligned JSONL prefixes without transcript text.",
        "prefix_rows": 2,
        "compared_rows": 2,
        "exact_match_rows": 1,
        "changed_rows": 1,
        "changed_segment_ids": ["S12-0002"],
        "attempt_01": {
            "sha256": MODULE.sha256_file(attempt_01),
        },
        "attempt_02": {
            "sha256": MODULE.sha256_file(translation),
        },
        "parameter_comparability": "event_metadata_partially_evidenced",
        "event_evidence": {
            "attempt_01": {
                "event_ledger_sha256": MODULE.sha256_file(attempt_01_events),
            },
            "attempt_02": {
                "event_ledger_sha256": MODULE.sha256_file(event_log),
            },
            "generator_script_hash_match": False,
        },
        "claim_boundary": (
            "Machine-English content differs across reruns and requires bilingual human review."
        ),
        "contains_transcript_text": False,
    }
    comparison_report.write_text(json.dumps(comparison), encoding="utf-8")
    for role, path in (
        ("machine_english", translation),
        ("translation_event_log", event_log),
        ("translation_generator_script", translation_generator),
        ("ollama_model_blob", model_blob),
        ("ollama_model_manifest", model_manifest),
        ("translation_attempt_01_partial", attempt_01),
        ("translation_attempt_01_event_log", attempt_01_events),
        ("translation_comparison_generator", comparison_generator),
        ("translation_comparison_report", comparison_report),
    ):
        provenance["artifacts"].append(
            {
                "role": role,
                "path": str(path.resolve()),
                "bytes": path.stat().st_size,
                "sha256": MODULE.sha256_file(path),
            }
        )
    provenance["translation"] = {
        "status": "complete",
        "segment_count": len(source_rows),
        "model": {
            "name": "fixture:latest",
            "digest": digest,
            "options": MODULE.DEFAULT_OLLAMA_OPTIONS,
            "blob_role": "ollama_model_blob",
            "manifest_role": "ollama_model_manifest",
            "blob_sha256": MODULE.sha256_file(model_blob),
            "manifest_sha256": MODULE.sha256_file(model_manifest),
        },
        "prompt_template_sha256": MODULE.sha256_text(MODULE.translation_prompt([])),
        "generator_script_role": "translation_generator_script",
        "batch_size": 18,
        "timeout_seconds": 600,
        "command": {"argv": ["python", "translate"]},
        "attempt_comparison": {
            "report_role": "translation_comparison_report",
            "generator_script_role": "translation_comparison_generator",
            "attempt_01_role": "translation_attempt_01_partial",
            "attempt_01_event_role": "translation_attempt_01_event_log",
            "attempt_02_role": "machine_english",
            "attempt_02_event_role": "translation_event_log",
        },
    }
    provenance_path.write_text(json.dumps(provenance), encoding="utf-8")
    profile = dict(MODULE.AUG12_SOURCE_PROFILE)
    profile.update(
        {
            "translation_model_name": "fixture:latest",
            "translation_model_digest": digest.upper(),
            "machine_english_sha256": MODULE.sha256_file(translation),
            "machine_english_bytes": translation.stat().st_size,
            "translation_event_log_sha256": MODULE.sha256_file(event_log),
            "translation_event_log_bytes": event_log.stat().st_size,
            "translation_generator_script_sha256": MODULE.sha256_file(SCRIPT),
            "translation_generator_script_bytes": SCRIPT.stat().st_size,
            "ollama_model_blob_sha256": MODULE.sha256_file(model_blob),
            "ollama_model_blob_bytes": model_blob.stat().st_size,
            "ollama_model_manifest_sha256": MODULE.sha256_file(model_manifest),
            "ollama_model_manifest_bytes": model_manifest.stat().st_size,
            "translation_attempt_01_partial_sha256": MODULE.sha256_file(attempt_01),
            "translation_attempt_01_partial_bytes": attempt_01.stat().st_size,
            "translation_attempt_01_event_log_sha256": MODULE.sha256_file(
                attempt_01_events
            ),
            "translation_attempt_01_event_log_bytes": attempt_01_events.stat().st_size,
            "translation_comparison_generator_sha256": MODULE.sha256_file(
                comparison_generator
            ),
            "translation_comparison_generator_bytes": comparison_generator.stat().st_size,
            "translation_comparison_report_sha256": MODULE.sha256_file(
                comparison_report
            ),
            "translation_comparison_report_bytes": comparison_report.stat().st_size,
            "translation_comparison_prefix_rows": 2,
            "translation_comparison_exact_rows": 1,
            "translation_comparison_changed_rows": 1,
        }
    )
    MODULE.AUG12_SOURCE_PROFILE = profile
    return translation, event_log


def normalized_rows() -> list[dict[str, object]]:
    return MODULE.normalize_asr_lines(
        raw_lines(),
        expected_segments=3,
        media_duration=Decimal("10.000"),
    )


def machine_rows() -> list[dict[str, str]]:
    rows = normalized_rows()
    translations = [
        {
            "Segment_ID": "S12-0001",
            "Machine_EN": "Hello",
            "Source_HE_SHA256": MODULE.sha256_text("שלום"),
        },
        {
            "Segment_ID": "S12-0002",
            "Machine_EN": "world",
            "Source_HE_SHA256": MODULE.sha256_text("עולם"),
        },
        {
            "Segment_ID": "S12-0003",
            "Machine_EN": "ending",
            "Source_HE_SHA256": MODULE.sha256_text("סיום"),
        },
    ]
    return MODULE.build_machine_ledger(rows, translations)


def completed_review(
    reviewer: str,
    *,
    second_translation: str = "world",
    gap_rows: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for source, english in zip(
        normalized_rows(),
        ("Hello", second_translation, "ending"),
        strict=True,
    ):
        rows.append(
            {
                "Record_ID": str(source["Segment_ID"]),
                "Record_Type": "Segment",
                "Reviewer_ID": reviewer,
                "Review_Date": "2026-08-15",
                "Reviewed_HE": str(source["Machine_HE"]),
                "Reviewed_EN": english,
                "Speaker": "Unresolved",
                "Speaker_Confidence": "Unknown",
                "Speaker_Basis": "No responsible audiovisual attribution",
                "Content_Class": "Context",
                "Control_IDs": "F12-001",
                "Review_Notes": "Reviewed against media",
            }
        )
    for gap in gap_rows or []:
        rows.append(
            {
                "Record_ID": gap["Gap_ID"],
                "Record_Type": "ASR gap",
                "Reviewer_ID": reviewer,
                "Review_Date": "2026-08-15",
                "Reviewed_HE": "",
                "Reviewed_EN": "",
                "Speaker": "Non-speech",
                "Speaker_Confidence": "High",
                "Speaker_Basis": "Reviewed the uncovered media interval",
                "Content_Class": "Noise or non-speech",
                "Control_IDs": "",
                "Review_Notes": "No substantive speech heard",
            }
        )
    rows.append(
        {
            "Record_ID": "MEDIA-TIMELINE",
            "Record_Type": "Full media timeline",
            "Reviewer_ID": reviewer,
            "Review_Date": "2026-08-15",
            "Reviewed_HE": "",
            "Reviewed_EN": "",
            "Speaker": "Non-speech",
            "Speaker_Confidence": "Unknown",
            "Speaker_Basis": "Full 10-second timeline reviewed",
            "Content_Class": "Noise or non-speech",
            "Control_IDs": "",
            "Review_Notes": MODULE.timeline_attestation(Decimal("10.000")),
        }
    )
    return rows


def review_kwargs(*, adjudicator_id: str | None = None) -> dict[str, object]:
    return {
        "media_duration": Decimal("10.000"),
        "reviewer_a_id": "reviewer-a",
        "reviewer_b_id": "reviewer-b",
        "adjudicator_id": adjudicator_id,
        "registered_control_ids": {"F12-001", "A12-001"},
    }


def fixture_run_context(source_path: Path, source_rows: list[dict[str, object]]) -> dict[str, object]:
    return MODULE.translation_run_context(
        source_path=source_path,
        source_rows=source_rows,
        generator_script_sha256=MODULE.sha256_file(SCRIPT),
        model="fixture:latest",
        model_digest="a" * 64,
        options=MODULE.DEFAULT_OLLAMA_OPTIONS,
        batch_size=2,
        timeout_seconds=60,
    )


def write_completion_events(
    event_log: Path,
    output: Path,
    context: dict[str, object],
    *,
    run_id: str = "run-1",
    expected_segments: int = 3,
) -> None:
    event_log.write_text(
        MODULE._render_jsonl(
            [
                {
                    "timestamp_utc": "2026-08-15T00:00:00+00:00",
                    "run_id": run_id,
                    "event": "translation_run_started",
                    **context,
                },
                {
                    "timestamp_utc": "2026-08-15T00:01:00+00:00",
                    "run_id": run_id,
                    "event": "translation_run_completed",
                    "translated_segment_count": expected_segments,
                    "output_bytes": output.stat().st_size,
                    "output_sha256": MODULE.sha256_file(output),
                },
            ]
        ),
        encoding="utf-8",
    )


def test_normalization_assigns_meeting_scoped_ids_and_preserves_machine_text() -> None:
    rows = normalized_rows()

    assert [row["Segment_ID"] for row in rows] == [
        "S12-0001",
        "S12-0002",
        "S12-0003",
    ]
    assert rows[0]["Start"] == "00:00:01.010"
    assert rows[-1]["End"] == "00:00:09.482"
    assert rows[0]["Machine_HE"] == "שלום"
    assert rows[0]["Source_Line"] == 1


def test_locked_august12_source_profile_matches_audited_media() -> None:
    assert PRODUCTION_SOURCE_PROFILE == {
        "profile_id": "2026-08-12-iris-arnon-zoom-local-v1",
        "media_duration_seconds": "3224.448",
        "raw_audio_sha256": "E562AE340AB8FF87BEB84AA03D5BFD709A01A396F0045F2CAE4EEE71C4C0E798",
        "raw_audio_bytes": 35_684_965,
        "raw_video_sha256": "617824ABBA9A9A1626BB73BDEC536ADC6C3A0F3F2A27CFE0335ECE3FC93E435C",
        "raw_video_bytes": 226_239_003,
        "raw_chat_sha256": "4682711493FD4CA6F694DB0EE0FC116497A8D0A9DA28EB1744F3D070E8E00F94",
        "raw_chat_bytes": 315,
        "recording_config_sha256": "124659343355D5A0EC76C053EC3958BDA39F51BCC7095A19A22A65C902574C7F",
        "recording_config_bytes": 127,
        "hebrew_asr_sha256": "A9267A95B0F93715375D3A21C2E4C897D7E0682EC0552811E4478831C994EC4D",
        "hebrew_asr_bytes": 93_920,
        "hebrew_asr_segment_count": 1_064,
        "hebrew_asr_schema": "jsonl:start,end,text:v1",
        "hebrew_asr_readable_sha256": "3CC7E56757B83BE416089247D4C8053D56A7F03C1A47699163670F421976EE32",
        "hebrew_asr_readable_bytes": 70_581,
        "asr_generator_script_sha256": "C71032EE0CA1579971B6BF71E057417B73BB13EE274DF0ACAAE8342DE4E2A05E",
        "asr_generator_script_bytes": 2_512,
        "asr_task_log_sha256": "C83503AA02ADBA100D13B7889B8E98B6CA4230F588AD88DDBDF141C418FB60B3",
        "asr_task_log_bytes": 1_561,
        "asr_model_repository": "mobiuslabsgmbh/faster-whisper-large-v3-turbo",
        "asr_model_name": "large-v3-turbo",
        "asr_model_snapshot_commit": "0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf",
        "asr_model_snapshot_tree_sha256": "4EDA58772FE73D11E2ECF35D63D1F22F8296181CE6BFEA849B612C3FD574C74D",
        "asr_model_blob_sha256": "E76620F83D5F5B69EFD3D87E3DC180C1BD21DF9FBEBACFD4335E5E1EFCC018DA",
        "asr_model_blob_bytes": 1_617_884_929,
        "control_register_sha256": "5F6422D0573FD144CF99A7D14623F3B52874028197210A9119C41A36B83C79F7",
        "control_register_bytes": 14_902,
        "translation_model_name": "qwen2.5:7b",
        "translation_model_digest": "845DBDA0EA48ED749CAAFD9E6037047AA19ACFCFD82E704D7CA97D631A0B697E",
        "ollama_model_blob_sha256": "2BADA8A7450677000F678BE90653B85D364DE7DB25EB5EA54136ADA5F3933730",
        "ollama_model_blob_bytes": 4_683_073_952,
        "ollama_model_manifest_sha256": "845DBDA0EA48ED749CAAFD9E6037047AA19ACFCFD82E704D7CA97D631A0B697E",
        "ollama_model_manifest_bytes": 858,
        "translation_generator_script_sha256": "0DA0B228BF939DC9B5EEB05CA6FB7F294E51BDAE29DA9978B7A719698C887208",
        "translation_generator_script_bytes": 57_314,
        "machine_english_sha256": "E163DC80783C2AECE0467FAA2456D0536BA950001D917A6C25B4D3013C8DC25B",
        "machine_english_bytes": 168_996,
        "translation_event_log_sha256": "4E5C26D84802158A360BF45E4C31EDC41659DE4904E0CAB9BDFE80EC51D6EA11",
        "translation_event_log_bytes": 92_704,
        "translation_attempt_01_partial_sha256": "D258060249CEFDA4F18F727FED6A41D5AD4362E3EEF73A63ABC327645C8B216E",
        "translation_attempt_01_partial_bytes": 81_051,
        "translation_attempt_01_event_log_sha256": "4B38124EF9EE9FED95EF3B81E791FEC0437666BE888EB1B1419A760FE62D6152",
        "translation_attempt_01_event_log_bytes": 45_808,
        "translation_comparison_generator_sha256": "5F1278880779C1BA747DFE6941E2DFF96BB42AE77E3A71F6996C67DCEB2F22F3",
        "translation_comparison_generator_bytes": 10_120,
        "translation_comparison_report_sha256": "256A8C773F0BAD5A9A244D64FB7EEDF10F36EE720D8E7E1D75069089594F7ADA",
        "translation_comparison_report_bytes": 4_149,
        "translation_comparison_prefix_rows": 198,
        "translation_comparison_exact_rows": 152,
        "translation_comparison_changed_rows": 46,
        "encoded_packet_sha256": "8D639C5FB0DDC66A31F7A303141F2451BE0AA91273242A3C7988906E0F22F67C",
        "packet_timing_sha256": "15EF42A61C432F45293DCFCB3A30A181464D82B957794B626AE6BAAD6DB4D0D2",
        "canonical_pcm_sha256": "60D4A3A25CBBEC7ADC68486E5397355D903C028B55A27A9488E5F77898723266",
        "canonical_pcm_samples": 51_591_168,
    }


def test_normalization_fails_closed_on_empty_or_out_of_order_source() -> None:
    empty = [json.dumps({"start": 0, "end": 1, "text": ""})]
    with pytest.raises(ValueError, match="empty machine Hebrew"):
        MODULE.normalize_asr_lines(empty, expected_segments=1, media_duration=Decimal("1"))

    out_of_order = [
        json.dumps({"start": 2, "end": 3, "text": "a"}),
        json.dumps({"start": 1, "end": 2, "text": "b"}),
    ]
    with pytest.raises(ValueError, match="out-of-order"):
        MODULE.normalize_asr_lines(
            out_of_order,
            expected_segments=2,
            media_duration=Decimal("3"),
        )


def test_gap_ledger_accounts_for_lead_internal_and_tail_intervals() -> None:
    rows = normalized_rows()
    gaps = MODULE.build_gap_rows(rows, media_duration=Decimal("10.000"))
    metrics = MODULE.timeline_metrics(rows, gaps, media_duration=Decimal("10.000"))

    assert [row["Gap_ID"] for row in gaps] == ["G12-0001", "G12-0002", "G12-0003"]
    assert [row["Gap_Type"] for row in gaps] == ["Lead", "Internal", "Tail"]
    assert metrics["uncovered_interval_count"] == 3
    assert metrics["uncovered_seconds"] == 2.028
    assert metrics["asr_interval_union_seconds"] == 7.972
    assert metrics["machine_accounted_timeline_seconds"] == 10.0


def test_translation_alignment_rejects_missing_or_source_mismatched_rows() -> None:
    rows = normalized_rows()
    missing = [
        {
            "Segment_ID": "S12-0001",
            "Machine_EN": "Hello",
            "Source_HE_SHA256": MODULE.sha256_text("שלום"),
        },
        {
            "Segment_ID": "S12-0002",
            "Machine_EN": "world",
            "Source_HE_SHA256": MODULE.sha256_text("עולם"),
        },
    ]
    with pytest.raises(ValueError, match="translation IDs"):
        MODULE.validate_translation_rows(rows, missing)

    mismatched = [
        {"Segment_ID": str(row["Segment_ID"]), "Machine_EN": "x", "Source_HE_SHA256": "0" * 64}
        for row in rows
    ]
    with pytest.raises(ValueError, match="source Hebrew hash mismatch"):
        MODULE.validate_translation_rows(rows, mismatched)


def test_machine_ledger_never_promotes_machine_output_to_human_review() -> None:
    rows = machine_rows()

    assert len(rows) == 3
    assert all(row["Speaker"] == "Unresolved" for row in rows)
    assert all(row["Reviewer_A"] == row["Reviewer_B"] == "" for row in rows)
    assert all(row["Status"] == "Machine-only; human review needed" for row in rows)
    assert rows[1]["Machine_EN"] == "world"


def test_translation_prompt_forbids_speaker_inference_and_requires_exact_ids() -> None:
    prompt = MODULE.translation_prompt(normalized_rows()[:2])

    assert "S12-0001 ||" in prompt
    assert "S12-0002 ||" in prompt
    assert "Do not infer speakers" in prompt
    assert "exactly one" in prompt


def test_adjudication_is_blocked_when_human_reviews_are_missing() -> None:
    with pytest.raises(MODULE.PendingReviews, match="Reviewer A"):
        MODULE.merge_human_reviews(machine_rows(), [], [], [], **review_kwargs())


def test_adjudication_requires_distinct_reviewer_identities() -> None:
    review = completed_review("reviewer-one")
    with pytest.raises(ValueError, match="distinct identities"):
        MODULE.merge_human_reviews(
            machine_rows(),
            review,
            review,
            [],
            **{
                **review_kwargs(),
                "reviewer_a_id": "Ali",
                "reviewer_b_id": "ali",
            },
        )


def test_disagreement_requires_a_distinct_completed_adjudication() -> None:
    reviewer_a = completed_review("reviewer-a")
    reviewer_b = completed_review("reviewer-b", second_translation="the world")

    with pytest.raises(MODULE.PendingReviews, match="S12-0002"):
        MODULE.merge_human_reviews(machine_rows(), reviewer_a, reviewer_b, [], **review_kwargs())

    adjudication = [
        {
            "Record_ID": "S12-0002",
            "Adjudicator_ID": "adjudicator-c",
            "Adjudication_Date": "2026-08-15",
            "Final_HE": "עולם",
            "Final_EN": "the world",
            "Final_Speaker": "Unresolved",
            "Final_Speaker_Confidence": "Unknown",
            "Final_Speaker_Basis": "No responsible audiovisual attribution",
            "Final_Content_Class": "Context",
            "Final_Control_IDs": "F12-001",
            "Adjudication_Rationale": "Reviewer B better preserves context",
            "Decision_Status": "Resolved",
        }
    ]
    merged = MODULE.merge_human_reviews(
        machine_rows(),
        reviewer_a,
        reviewer_b,
        adjudication,
        **review_kwargs(adjudicator_id="adjudicator-c"),
    )

    assert merged[1]["Reviewed_EN"] == "the world"
    assert merged[1]["Adjudication"] == "adjudicator-c"
    assert merged[1]["Status"] == "Human-reviewed adjudicated"
    assert merged[0]["Status"] == "Human-reviewed consensus"


def test_control_ids_use_only_the_august_12_namespace() -> None:
    assert MODULE.canonical_control_ids("F12-001; A12-010; Q12-002") == (
        "F12-001",
        "A12-010",
        "Q12-002",
    )
    with pytest.raises(ValueError, match="invalid August 12 control ID"):
        MODULE.canonical_control_ids("R-01")


def test_translation_response_must_return_each_expected_id_exactly_once() -> None:
    assert MODULE.parse_translation_response(
        "S12-0001 || Hello\nS12-0002 || world\n",
        ("S12-0001", "S12-0002"),
    ) == {"S12-0001": "Hello", "S12-0002": "world"}

    with pytest.raises(ValueError, match="duplicate translation ID"):
        MODULE.parse_translation_response(
            "S12-0001 || Hello\nS12-0001 || Again\n",
            ("S12-0001",),
        )
    with pytest.raises(ValueError, match="missing translation IDs"):
        MODULE.parse_translation_response("S12-0001 || Hello\n", ("S12-0001", "S12-0002"))


def test_local_translation_records_bind_each_result_to_its_hebrew_source() -> None:
    source = normalized_rows()

    def requester(batch: list[dict[str, object]]) -> str:
        return "\n".join(f"{row['Segment_ID']} || EN-{row['Segment_ID']}" for row in batch)

    translated = MODULE.translate_source_rows(source, requester, batch_size=2)

    assert [row["Segment_ID"] for row in translated] == [
        "S12-0001",
        "S12-0002",
        "S12-0003",
    ]
    assert translated[0]["Machine_EN"] == "EN-S12-0001"
    assert translated[0]["Source_HE_SHA256"] == MODULE.sha256_text("שלום")
    MODULE.validate_translation_rows(source, translated)


def test_package_build_is_reproducible_and_prepopulates_all_review_records(tmp_path: Path) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    output = tmp_path / "package"

    first = build_package_contents(
        source,
        expected_segments=3,
        media_duration=Decimal("10.000"),
        provenance_path=provenance,
    )
    MODULE.write_package(output, first, allowed_root=tmp_path)
    second = build_package_contents(
        source,
        expected_segments=3,
        media_duration=Decimal("10.000"),
        provenance_path=provenance,
    )

    assert first == second
    assert MODULE.check_package(output, second, allowed_root=tmp_path) == []
    payload = json.loads(first["preliminary-ledger.json"])
    assert payload["human_review_completed"] is False
    assert payload["coverage"]["segment_count"] == 3
    assert payload["coverage"]["uncovered_interval_count"] == 3
    assert len(payload["rows"]) == 3
    assert payload["control_register"]["registered_control_count"] == 2
    assert payload["rows"][0]["Control_IDs"] == "F12-001"
    assert payload["rows"][1]["Control_IDs"] == "F12-001; A12-001"
    for template in ("reviewer-a.csv", "reviewer-b.csv"):
        rows = list(csv.DictReader(io.StringIO(first[template])))
        assert [row["Record_ID"] for row in rows] == [
            "S12-0001",
            "S12-0002",
            "S12-0003",
            "G12-0001",
            "G12-0002",
            "G12-0003",
            "MEDIA-TIMELINE",
        ]
        assert all(row["Reviewer_ID"] == "" for row in rows)
    assert len(list(csv.reader(io.StringIO(first["adjudication.csv"])))) == 1


def test_package_check_reports_missing_or_changed_files(tmp_path: Path) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    expected = build_package_contents(
        source,
        expected_segments=3,
        media_duration=Decimal("10.000"),
        provenance_path=provenance,
    )
    output = tmp_path / "package"
    MODULE.write_package(output, expected, allowed_root=tmp_path)
    (output / "machine-ledger.csv").write_text("changed", encoding="utf-8")
    (output / "reviewer-b.csv").unlink()

    errors = MODULE.check_package(output, expected, allowed_root=tmp_path)

    assert any("machine-ledger.csv differs" in error for error in errors)
    assert any("reviewer-b.csv is missing" in error for error in errors)


def test_media_comparison_requires_matching_encoded_and_pcm_hashes() -> None:
    left = {
        "encoded_packet_sha256": "A" * 64,
        "packet_timing_sha256": "B" * 64,
        "canonical_pcm_sha256": "C" * 64,
        "canonical_pcm_samples": 100,
    }
    assert MODULE.compare_media_fingerprints(left, dict(left)) == []

    right = dict(left, canonical_pcm_sha256="D" * 64)
    assert MODULE.compare_media_fingerprints(left, right) == ["canonical_pcm_sha256 differs"]


def test_audio_fingerprint_is_stable_for_same_pcm_fixture(tmp_path: Path) -> None:
    pytest.importorskip("av")
    audio = tmp_path / "fixture.wav"
    with wave.open(str(audio), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(16_000)
        handle.writeframes((b"\x00\x00\x01\x00\xff\xff\x00\x00") * 400)

    first = MODULE.fingerprint_audio(audio)
    second = MODULE.fingerprint_audio(audio)

    assert first == second
    assert first["source_sha256"] == MODULE.sha256_file(audio)
    assert first["audio_stream_count"] == 1
    assert first["canonical_pcm_rate_hz"] == 16_000
    assert first["canonical_pcm_channels"] == 1
    assert first["canonical_pcm_samples"] == 1_600
    assert first["duration_seconds"] == 0.1


def test_translation_checkpoint_refuses_an_unbound_existing_prefix(tmp_path: Path) -> None:
    source = normalized_rows()
    output = tmp_path / "machine.en.jsonl"

    def requester(batch: list[dict[str, object]]) -> str:
        return "\n".join(f"{row['Segment_ID']} || EN-{row['Segment_ID']}" for row in batch)

    MODULE.translate_with_checkpoints(source, requester, output, batch_size=2)
    with pytest.raises(ValueError, match="requires bound event-ledger context"):
        MODULE.translate_with_checkpoints(source, requester, output, batch_size=2)


def test_human_review_requires_every_asr_gap_and_full_timeline() -> None:
    gaps = MODULE.build_gap_rows(normalized_rows(), media_duration=Decimal("10.000"))
    reviewer_a = completed_review("reviewer-a")
    reviewer_b = completed_review("reviewer-b")

    with pytest.raises(MODULE.PendingReviews, match="every segment, gap, and timeline"):
        MODULE.merge_human_reviews(
            machine_rows(), reviewer_a, reviewer_b, [], gap_rows=gaps, **review_kwargs()
        )

    reviewer_a = completed_review("reviewer-a", gap_rows=gaps)
    reviewer_b = completed_review("reviewer-b", gap_rows=gaps)
    merged = MODULE.merge_human_reviews(
        machine_rows(), reviewer_a, reviewer_b, [], gap_rows=gaps, **review_kwargs()
    )
    assert len(merged) == 7
    assert [row["Record_ID"] for row in merged] == [
        "S12-0001",
        "S12-0002",
        "S12-0003",
        "G12-0001",
        "G12-0002",
        "G12-0003",
        "MEDIA-TIMELINE",
    ]
    assert all(row["Status"] == "Human-reviewed consensus" for row in merged)


def test_translation_batch_failure_falls_back_per_row_and_logs_attempts(
    tmp_path: Path,
) -> None:
    source = normalized_rows()
    output = tmp_path / "machine.en.jsonl"
    events: list[dict[str, object]] = []

    def requester(batch: list[dict[str, object]]) -> str:
        if len(batch) > 1:
            return "not parseable"
        row = batch[0]
        return f"{row['Segment_ID']} || EN-{row['Segment_ID']}"

    translated = MODULE.translate_with_checkpoints(
        source,
        requester,
        output,
        batch_size=2,
        event_logger=events.append,
    )

    assert len(translated) == 3
    assert [event["event"] for event in events].count("batch_failed") == 1
    assert [event["event"] for event in events].count("row_completed") == 2
    assert events[0]["prompt_sha256"] == MODULE.sha256_text(MODULE.translation_prompt(source[:2]))


def test_cli_build_and_check_detects_private_package_drift(tmp_path: Path) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    output = tmp_path / "package"

    assert (
        MODULE.main(
            [
                "build",
                "--source",
                str(source),
                "--output-dir",
                str(output),
                "--expected-segments",
                "3",
                "--media-duration",
                "10.000",
                "--provenance",
                str(provenance),
                "--allowed-root",
                str(tmp_path),
                    "--repo-root",
                    str(ROOT),
                    "--hf-cache-root",
                    str(fixture_hf_cache_root(tmp_path)),
                ]
        )
        == 0
    )
    assert (
        MODULE.main(
            [
                "check",
                "--source",
                str(source),
                "--output-dir",
                str(output),
                "--expected-segments",
                "3",
                "--media-duration",
                "10.000",
                "--provenance",
                str(provenance),
                "--allowed-root",
                str(tmp_path),
                    "--repo-root",
                    str(ROOT),
                    "--hf-cache-root",
                    str(fixture_hf_cache_root(tmp_path)),
                ]
        )
        == 0
    )
    (output / "machine-ledger.csv").write_text("drift", encoding="utf-8")
    assert (
        MODULE.main(
            [
                "check",
                "--source",
                str(source),
                "--output-dir",
                str(output),
                "--expected-segments",
                "3",
                "--media-duration",
                "10.000",
                "--provenance",
                str(provenance),
                "--allowed-root",
                str(tmp_path),
                    "--repo-root",
                    str(ROOT),
                    "--hf-cache-root",
                    str(fixture_hf_cache_root(tmp_path)),
                ]
        )
        == 1
    )


def test_ollama_model_resolution_requires_exact_name_and_digest() -> None:
    tags = {
        "models": [
            {
                "name": "qwen2.5:7b",
                "digest": "a" * 64,
                "size": 123,
            }
        ]
    }
    model = MODULE.require_ollama_model(tags, "qwen2.5:7b", "a" * 64)
    assert model["size"] == 123

    with pytest.raises(ValueError, match="digest mismatch"):
        MODULE.require_ollama_model(tags, "qwen2.5:7b", "b" * 64)
    with pytest.raises(ValueError, match="not available"):
        MODULE.require_ollama_model(tags, "missing:latest", "a" * 64)


def test_historical_id_crosswalk_is_complete_and_targets_known_controls() -> None:
    expected_old_ids = (
        {f"F{index}" for index in range(1, 18)}
        | {f"A0812-{index:02d}" for index in range(1, 10)}
        | {"A08-01", "A08-03", "A08-05", "D-RQ-01", "D-RQ-02", "E6", "E8"}
    )
    crosswalk_rows = list(csv.DictReader(CROSSWALK.open(encoding="utf-8")))
    assert len(crosswalk_rows) == len(expected_old_ids)
    assert {row["Old_ID"] for row in crosswalk_rows} == expected_old_ids
    assert len({row["Old_ID"] for row in crosswalk_rows}) == len(crosswalk_rows)

    controls = {
        row["Control_ID"] for row in csv.DictReader(CONTROL_REGISTER.open(encoding="utf-8"))
    }
    for row in crosswalk_rows:
        targets = [value.strip() for value in row["New_IDs"].split(";")]
        assert targets
        assert set(targets) <= controls


def test_tracked_aug12_evidence_controls_are_public_safe() -> None:
    for path in (CONTROL_REGISTER, CROSSWALK, HANDOFF):
        text = path.read_text(encoding="utf-8").lower()
        assert "c:\\users\\" not in text
        assert "@gmail.com" not in text
        assert "@is.haifa.ac.il" not in text

    handoff = json.loads(HANDOFF.read_text(encoding="utf-8"))
    assert handoff["gate_0"]["stable_window_seconds"] == 309
    assert handoff["gate_0"]["preserved_dirty_or_untracked_path_count"] == 24


def test_package_rejects_unexpected_files_and_unowned_existing_directory(
    tmp_path: Path,
) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    expected = build_package_contents(
        source,
        expected_segments=3,
        media_duration=Decimal("10.000"),
        provenance_path=provenance,
    )

    unowned = tmp_path / "unowned"
    unowned.mkdir()
    (unowned / "personal.txt").write_text("preserve", encoding="utf-8")
    with pytest.raises(ValueError, match="not owned"):
        MODULE.write_package(unowned, expected, allowed_root=tmp_path)

    owned = tmp_path / "owned"
    MODULE.write_package(owned, expected, allowed_root=tmp_path)
    (owned / "unexpected.txt").write_text("extra", encoding="utf-8")
    errors = MODULE.check_package(owned, expected, allowed_root=tmp_path)
    assert any("unexpected file" in error for error in errors)


def test_package_rejects_traversal_and_symlink_escape(tmp_path: Path) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    expected = build_package_contents(
        source,
        expected_segments=3,
        media_duration=Decimal("10.000"),
        provenance_path=provenance,
    )
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    with pytest.raises(ValueError, match="outside the allowed private root"):
        MODULE.write_package(allowed / ".." / "escaped", expected, allowed_root=allowed)

    outside = tmp_path / "outside"
    outside.mkdir()
    link = allowed / "linked"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("directory symlinks are not available in this environment")
    with pytest.raises(ValueError, match="outside the allowed private root|reparse"):
        MODULE.write_package(link, expected, allowed_root=allowed)


def test_provenance_detects_source_hash_drift(tmp_path: Path) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    raw_audio = tmp_path / "source.m4a"
    raw_audio.write_bytes(b"changed")

    with pytest.raises(ValueError, match="raw_audio hash drift"):
        build_package_contents(
            source,
            expected_segments=3,
            media_duration=Decimal("10.000"),
            provenance_path=provenance,
        )


def test_provenance_detects_model_translation_and_event_ledger_drift(
    tmp_path: Path,
) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    source_rows = MODULE.normalize_asr_lines(
        raw_lines(), expected_segments=3, media_duration=Decimal("10.000")
    )
    translation, event_log = complete_translation_provenance(provenance, source_rows)

    build_package_contents(
        source,
        expected_segments=3,
        media_duration=Decimal("10.000"),
        provenance_path=provenance,
        translation_path=translation,
    )

    original_manifest = provenance.read_text(encoding="utf-8")
    payload = json.loads(original_manifest)
    payload["translation"]["model"]["digest"] = "b" * 64
    provenance.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="model identity|model[_ ]digest drift"):
        build_package_contents(
            source,
            expected_segments=3,
            media_duration=Decimal("10.000"),
            provenance_path=provenance,
            translation_path=translation,
        )

    provenance.write_text(original_manifest, encoding="utf-8")
    original_translation = translation.read_text(encoding="utf-8")
    translation.write_text(original_translation + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="machine_english hash drift"):
        build_package_contents(
            source,
            expected_segments=3,
            media_duration=Decimal("10.000"),
            provenance_path=provenance,
            translation_path=translation,
        )

    translation.write_text(original_translation, encoding="utf-8")
    event_log.write_text(event_log.read_text(encoding="utf-8") + "{}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="translation_event_log hash drift"):
        build_package_contents(
            source,
            expected_segments=3,
            media_duration=Decimal("10.000"),
            provenance_path=provenance,
            translation_path=translation,
        )


@pytest.mark.parametrize(
    "url",
    (
        "https://127.0.0.1:11434",
        "http://example.com:11434",
        "http://0.0.0.0:11434",
        "http://localhost:11434",
        "http://user:pass@127.0.0.1:11434",
        "http://127.0.0.1:11434/path",
        "http://127.0.0.1:11434?leak=yes",
    ),
)
def test_ollama_url_rejects_non_loopback_or_ambiguous_endpoints(url: str) -> None:
    with pytest.raises(ValueError):
        MODULE.validate_ollama_base_url(url)


@pytest.mark.parametrize(
    ("url", "expected"),
    (
        ("http://127.0.0.1:11434/", "http://127.0.0.1:11434"),
        ("http://[::1]:11434", "http://[::1]:11434"),
    ),
)
def test_ollama_url_accepts_only_loopback_http(url: str, expected: str) -> None:
    assert MODULE.validate_ollama_base_url(url) == expected


def test_translation_paths_must_be_private_distinct_and_outside_repo(tmp_path: Path) -> None:
    private = tmp_path / "private"
    private.mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    source = private / "source.jsonl"
    source.write_text("{}\n", encoding="utf-8")
    output = private / "out.jsonl"
    events = private / "events.jsonl"

    assert MODULE.validate_translation_paths(
        source_path=source,
        output_path=output,
        event_log_path=events,
        allowed_root=private,
        repo_root=repo,
    ) == (source.resolve(), output.resolve(), events.resolve())

    with pytest.raises(ValueError, match="outside the allowed private root"):
        MODULE.validate_translation_paths(
            source_path=source,
            output_path=repo / "out.jsonl",
            event_log_path=events,
            allowed_root=private,
            repo_root=repo,
        )
    with pytest.raises(ValueError, match="distinct"):
        MODULE.validate_translation_paths(
            source_path=source,
            output_path=source,
            event_log_path=events,
            allowed_root=private,
            repo_root=repo,
        )
    with pytest.raises(ValueError, match="must not contain the repository"):
        MODULE.validate_translation_paths(
            source_path=source,
            output_path=output,
            event_log_path=events,
            allowed_root=tmp_path,
            repo_root=repo,
        )


def test_rebuild_refuses_to_overwrite_any_changed_human_return(tmp_path: Path) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    expected = build_package_contents(
        source,
        expected_segments=3,
        media_duration=Decimal("10.000"),
        provenance_path=provenance,
    )
    output = tmp_path / "package"
    MODULE.write_package(output, expected, allowed_root=tmp_path)
    reviewer = output / "reviewer-a.csv"
    frozen = b"FROZEN-HUMAN-RETURN\r\n"
    reviewer.write_bytes(frozen)

    with pytest.raises(ValueError, match="refusing to overwrite changed human-return"):
        MODULE.write_package(output, expected, allowed_root=tmp_path)
    assert reviewer.read_bytes() == frozen


def test_substantive_gap_requires_bilingual_text_notes_and_registered_control() -> None:
    gaps = MODULE.build_gap_rows(normalized_rows(), media_duration=Decimal("10.000"))
    reviewer_a = completed_review("reviewer-a", gap_rows=gaps)
    reviewer_b = completed_review("reviewer-b", gap_rows=gaps)
    for rows in (reviewer_a, reviewer_b):
        gap = next(row for row in rows if row["Record_ID"] == "G12-0001")
        gap.update(
            {
                "Speaker": "Iris",
                "Speaker_Confidence": "High",
                "Speaker_Basis": "Audiovisual confirmation: audible and visually confirmed",
                "Content_Class": "Requirement",
                "Control_IDs": "F12-001",
                "Reviewed_HE": "",
                "Reviewed_EN": "",
                "Review_Notes": "",
            }
        )

    with pytest.raises(ValueError, match="empty review notes|empty reviewed Hebrew"):
        MODULE.merge_human_reviews(
            machine_rows(), reviewer_a, reviewer_b, [], gap_rows=gaps, **review_kwargs()
        )


def test_full_media_review_requires_exact_zero_unreviewed_attestation() -> None:
    reviewer_a = completed_review("reviewer-a")
    reviewer_b = completed_review("reviewer-b")
    reviewer_a[-1]["Review_Notes"] = "unreviewed_media_seconds=0"

    with pytest.raises(ValueError, match="exact full-media"):
        MODULE.merge_human_reviews(machine_rows(), reviewer_a, reviewer_b, [], **review_kwargs())


def test_named_attribution_and_dangling_control_fail_closed() -> None:
    reviewer_a = completed_review("reviewer-a")
    reviewer_b = completed_review("reviewer-b")
    for rows in (reviewer_a, reviewer_b):
        rows[0].update(
            {
                "Speaker": "Iris",
                "Speaker_Confidence": "Unknown",
                "Speaker_Basis": "",
                "Content_Class": "Requirement",
                "Control_IDs": "F12-999",
            }
        )
    with pytest.raises(ValueError, match="unsupported named attribution|empty speaker basis"):
        MODULE.merge_human_reviews(machine_rows(), reviewer_a, reviewer_b, [], **review_kwargs())

    for rows in (reviewer_a, reviewer_b):
        rows[0]["Speaker_Confidence"] = "High"
        rows[0]["Speaker_Basis"] = "Audiovisual confirmation"
    with pytest.raises(ValueError, match="unregistered August 12 control ID"):
        MODULE.merge_human_reviews(machine_rows(), reviewer_a, reviewer_b, [], **review_kwargs())


def test_gap_adjudication_requires_rationale_and_is_persisted() -> None:
    gaps = MODULE.build_gap_rows(normalized_rows(), media_duration=Decimal("10.000"))
    reviewer_a = completed_review("reviewer-a", gap_rows=gaps)
    reviewer_b = completed_review("reviewer-b", gap_rows=gaps)
    gap_a = next(row for row in reviewer_a if row["Record_ID"] == "G12-0002")
    gap_b = next(row for row in reviewer_b if row["Record_ID"] == "G12-0002")
    for row, english in ((gap_a, "possible request"), (gap_b, "a request")):
        row.update(
            {
                "Reviewed_HE": "בקשה",
                "Reviewed_EN": english,
                "Speaker": "Unresolved",
                "Speaker_Confidence": "Unknown",
                "Speaker_Basis": "Audio reviewed; speaker unresolved",
                "Content_Class": "Action",
                "Control_IDs": "A12-001",
                "Review_Notes": "Substantive speech found in ASR gap",
            }
        )
    decision = {
        "Record_ID": "G12-0002",
        "Adjudicator_ID": "adjudicator-c",
        "Adjudication_Date": "2026-08-15",
        "Final_HE": "בקשה",
        "Final_EN": "a request",
        "Final_Speaker": "Unresolved",
        "Final_Speaker_Confidence": "Unknown",
        "Final_Speaker_Basis": "Audio reviewed; speaker unresolved",
        "Final_Content_Class": "Action",
        "Final_Control_IDs": "A12-001",
        "Adjudication_Rationale": "",
        "Decision_Status": "Resolved",
    }
    with pytest.raises(ValueError, match="rationale is empty"):
        MODULE.merge_human_reviews(
            machine_rows(),
            reviewer_a,
            reviewer_b,
            [decision],
            gap_rows=gaps,
            **review_kwargs(adjudicator_id="adjudicator-c"),
        )
    decision["Adjudication_Rationale"] = "Reviewer B preserves the obligation"
    merged = MODULE.merge_human_reviews(
        machine_rows(),
        reviewer_a,
        reviewer_b,
        [decision],
        gap_rows=gaps,
        **review_kwargs(adjudicator_id="adjudicator-c"),
    )
    merged_gap = next(row for row in merged if row["Record_ID"] == "G12-0002")
    assert merged_gap["Reviewed_EN"] == "a request"
    assert merged_gap["Status"] == "Human-reviewed adjudicated"
    assert merged_gap["Adjudication_Rationale"] == "Reviewer B preserves the obligation"


def test_media_comparison_schema_and_duration_are_cross_bound(tmp_path: Path) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    manifest = json.loads(provenance.read_text(encoding="utf-8"))
    comparison_record = next(
        row for row in manifest["artifacts"] if row["role"] == "media_comparison"
    )
    comparison_path = Path(comparison_record["path"])
    comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
    comparison["audio_evidence_equivalent"] = False
    comparison["differences"] = ["canonical_pcm_sha256 differs"]
    comparison_path.write_text(json.dumps(comparison), encoding="utf-8")
    comparison_record["bytes"] = comparison_path.stat().st_size
    comparison_record["sha256"] = MODULE.sha256_file(comparison_path)
    provenance.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="does not establish audio evidence equivalence"):
        build_package_contents(
            source,
            expected_segments=3,
            media_duration=Decimal("10.000"),
            provenance_path=provenance,
        )


def test_complete_checkpoint_requires_same_run_and_rejects_later_incomplete_start(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "machine.jsonl"
    source_path.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    rows = normalized_rows()
    output = tmp_path / "machine.en.jsonl"
    output.write_text(
        MODULE._render_jsonl(
            [
                {
                    "Segment_ID": str(row["Segment_ID"]),
                    "Machine_EN": f"EN-{row['Segment_ID']}",
                    "Source_HE_SHA256": str(row["Source_HE_SHA256"]),
                }
                for row in rows
            ]
        ),
        encoding="utf-8",
    )
    events = tmp_path / "events.jsonl"
    context = fixture_run_context(source_path, rows)
    write_completion_events(events, output, context)
    assert MODULE.validate_translation_event_ledger(
        events,
        output_path=output,
        run_context=context,
        expected_segments=3,
        require_complete=True,
    )["status"] == "complete"

    with events.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                {
                    "timestamp_utc": "2026-08-15T00:02:00+00:00",
                    "run_id": "run-2",
                    "event": "translation_run_started",
                    **context,
                }
            )
            + "\n"
        )
    with pytest.raises(ValueError, match="incomplete"):
        MODULE.validate_translation_event_ledger(
            events,
            output_path=output,
            run_context=context,
            expected_segments=3,
            require_complete=True,
        )


def test_csv_formula_cells_are_neutralized_but_jsonl_preserves_raw_text() -> None:
    row = {"Machine_HE": "=HYPERLINK(\"https://example.invalid\")"}
    rendered = MODULE._render_csv([row], ("Machine_HE",))
    parsed = list(csv.DictReader(io.StringIO(rendered)))
    assert parsed[0]["Machine_HE"].startswith("'=")
    assert "'=HYPERLINK" not in MODULE._render_jsonl([row])
    assert "=HYPERLINK" in MODULE._render_jsonl([row])


def test_named_speaker_low_confidence_guess_is_rejected() -> None:
    reviewer_a = completed_review("reviewer-a")
    reviewer_b = completed_review("reviewer-b")
    for rows in (reviewer_a, reviewer_b):
        rows[0].update(
            {
                "Speaker": "Iris",
                "Speaker_Confidence": "Low",
                "Speaker_Basis": "guess",
                "Content_Class": "Requirement",
                "Control_IDs": "F12-001",
            }
        )
    with pytest.raises(ValueError, match="evidence-grade named attribution"):
        MODULE.merge_human_reviews(machine_rows(), reviewer_a, reviewer_b, [], **review_kwargs())


def test_translation_completion_must_be_the_last_event(tmp_path: Path) -> None:
    source_path = tmp_path / "machine.jsonl"
    source_path.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    rows = normalized_rows()
    output = tmp_path / "machine.en.jsonl"
    output.write_text(
        MODULE._render_jsonl(
            [
                {
                    "Segment_ID": str(row["Segment_ID"]),
                    "Machine_EN": f"EN-{row['Segment_ID']}",
                    "Source_HE_SHA256": str(row["Source_HE_SHA256"]),
                }
                for row in rows
            ]
        ),
        encoding="utf-8",
    )
    events = tmp_path / "events.jsonl"
    context = fixture_run_context(source_path, rows)
    write_completion_events(events, output, context)
    with events.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                {
                    "timestamp_utc": "2026-08-15T00:02:00+00:00",
                    "run_id": "run-1",
                    "event": "batch_started",
                    "segment_ids": ["S12-0001"],
                }
            )
            + "\n"
        )
    with pytest.raises(ValueError, match="events after completion"):
        MODULE.validate_translation_event_ledger(
            events,
            output_path=output,
            run_context=context,
            expected_segments=3,
            require_complete=True,
        )


@pytest.mark.parametrize("malformed", ("S12-000X", "S12_0001", "S12 -0001", "S12/0001"))
def test_control_mapping_rejects_malformed_s12_like_tokens(
    tmp_path: Path, malformed: str
) -> None:
    control_register = tmp_path / "controls.csv"
    control_register.write_text(
        f"Control_ID,Source_Spans\nF12-001,{malformed}\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="malformed segment span"):
        MODULE.load_control_mapping(control_register, normalized_rows())


def test_readiness_recomputes_media_and_rejects_fabricated_dummy_sources(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    monkeypatch.setattr(MODULE, "RECOMPUTE_MEDIA_FINGERPRINTS", True, raising=False)

    with pytest.raises((RuntimeError, ValueError, OSError)):
        build_package_contents(
            source,
            expected_segments=3,
            media_duration=Decimal("10.000"),
            provenance_path=provenance,
        )


def test_execution_model_script_and_task_log_roles_are_semantically_bound(
    tmp_path: Path,
) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    original = provenance.read_text(encoding="utf-8")

    payload = json.loads(original)
    payload["media"]["command"]["exit_code"] = 1
    provenance.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="media fingerprint command"):
        build_package_contents(
            source,
            expected_segments=3,
            media_duration=Decimal("10.000"),
            provenance_path=provenance,
        )

    payload = json.loads(original)
    payload["asr"]["model"]["blob_sha256"] = "0" * 64
    provenance.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="ASR model blob hash"):
        build_package_contents(
            source,
            expected_segments=3,
            media_duration=Decimal("10.000"),
            provenance_path=provenance,
        )

    provenance.write_text(original, encoding="utf-8")
    rows = MODULE.normalize_asr_lines(
        raw_lines(), expected_segments=3, media_duration=Decimal("10.000")
    )
    translation, _ = complete_translation_provenance(provenance, rows)
    payload = json.loads(provenance.read_text(encoding="utf-8"))
    payload["translation"]["model"]["manifest_sha256"] = "0" * 64
    provenance.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="translation model manifest hash"):
        build_package_contents(
            source,
            expected_segments=3,
            media_duration=Decimal("10.000"),
            provenance_path=provenance,
            translation_path=translation,
        )


@pytest.mark.parametrize(
    "role",
    (
        "raw_chat",
        "recording_config",
        "hebrew_asr",
        "hebrew_asr_readable",
        "asr_generator_script",
        "asr_task_log",
        "asr_model_blob",
        "control_register",
    ),
)
def test_locked_source_chain_rejects_self_consistent_fabricated_substitutes(
    tmp_path: Path,
    role: str,
) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    payload = json.loads(provenance.read_text(encoding="utf-8"))
    record = next(item for item in payload["artifacts"] if item["role"] == role)
    artifact = Path(record["path"])
    if role == "hebrew_asr":
        artifact.write_text(
            "\n".join(
                json.dumps({"start": index, "end": index + 0.5, "text": "fabricated"})
                for index in (1, 2, 3)
            )
            + "\n",
            encoding="utf-8",
        )
    else:
        artifact.write_bytes(b"fabricated-substitute")
    record["bytes"] = artifact.stat().st_size
    record["sha256"] = MODULE.sha256_file(artifact)
    if role == "asr_model_blob":
        payload["asr"]["model"]["blob_sha256"] = record["sha256"]
    provenance.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="locked August 12 evidence"):
        build_package_contents(
            source,
            expected_segments=3,
            media_duration=Decimal("10.000"),
            provenance_path=provenance,
        )


@pytest.mark.parametrize(
    "field",
    (
        "source_sha256",
        "output_sha256",
        "readable_output_sha256",
        "generator_script_sha256",
        "task_log_sha256",
        "model_snapshot_tree_sha256",
        "model_blob_sha256",
        "segment_count",
        "exit_code",
    ),
)
def test_asr_execution_record_is_cross_bound_to_locked_artifacts(
    tmp_path: Path,
    field: str,
) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    payload = json.loads(provenance.read_text(encoding="utf-8"))
    payload["asr"]["execution_record"][field] = (
        1 if field in {"segment_count", "exit_code"} else "F" * 64
    )
    provenance.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="execution record"):
        build_package_contents(
            source,
            expected_segments=3,
            media_duration=Decimal("10.000"),
            provenance_path=provenance,
        )


def test_asr_snapshot_tree_drift_is_recomputed(tmp_path: Path) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    payload = json.loads(provenance.read_text(encoding="utf-8"))
    snapshot = Path(payload["asr"]["model"]["snapshot_path"])
    (snapshot / "config.json").write_bytes(b"changed-after-manifest")

    with pytest.raises(ValueError, match="snapshot bytes"):
        build_package_contents(
            source,
            expected_segments=3,
            media_duration=Decimal("10.000"),
            provenance_path=provenance,
        )


def test_asr_output_schema_is_locked(tmp_path: Path) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    payload = json.loads(provenance.read_text(encoding="utf-8"))
    payload["asr"]["output_schema"] = "untrusted-schema"
    provenance.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="output count or schema"):
        build_package_contents(
            source,
            expected_segments=3,
            media_duration=Decimal("10.000"),
            provenance_path=provenance,
        )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("changed_rows", 0, "counts drift"),
        ("contains_transcript_text", True, "claim boundary"),
        ("claim_boundary", "This is deterministic translation.", "claim boundary|forbidden"),
    ),
)
def test_translation_comparison_fails_closed_on_self_consistent_unsafe_report(
    tmp_path: Path,
    field: str,
    value: object,
    message: str,
) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    translation, _ = complete_translation_provenance(provenance, normalized_rows())
    payload = json.loads(provenance.read_text(encoding="utf-8"))
    artifact = next(
        item
        for item in payload["artifacts"]
        if item["role"] == "translation_comparison_report"
    )
    report_path = Path(artifact["path"])
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report[field] = value
    report_path.write_text(json.dumps(report), encoding="utf-8")
    artifact["bytes"] = report_path.stat().st_size
    artifact["sha256"] = MODULE.sha256_file(report_path)
    profile = dict(MODULE.AUG12_SOURCE_PROFILE)
    profile["translation_comparison_report_bytes"] = artifact["bytes"]
    profile["translation_comparison_report_sha256"] = artifact["sha256"]
    MODULE.AUG12_SOURCE_PROFILE = profile
    provenance.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        build_package_contents(
            source,
            expected_segments=3,
            media_duration=Decimal("10.000"),
            provenance_path=provenance,
            translation_path=translation,
        )


def test_translation_comparison_requires_exact_role_binding(tmp_path: Path) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    translation, _ = complete_translation_provenance(provenance, normalized_rows())
    payload = json.loads(provenance.read_text(encoding="utf-8"))
    payload["translation"]["attempt_comparison"]["attempt_02_role"] = "unbound"
    provenance.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="roles are not fully bound"):
        build_package_contents(
            source,
            expected_segments=3,
            media_duration=Decimal("10.000"),
            provenance_path=provenance,
            translation_path=translation,
        )


@pytest.mark.parametrize("role", PRIVATE_ARTIFACT_ROLES)
def test_build_rejects_exact_byte_evidence_copy_inside_repository(
    tmp_path: Path, role: str
) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    translation, _ = complete_translation_provenance(provenance, normalized_rows())
    payload = json.loads(provenance.read_text(encoding="utf-8"))
    record = next(item for item in payload["artifacts"] if item["role"] == role)
    original = Path(record["path"])
    generated_root = ROOT / "reports" / "generated"
    generated_root.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        prefix="aug12-private-root-adversary-", dir=generated_root
    ) as temporary_repo_dir:
        copied = Path(temporary_repo_dir) / original.name
        shutil.copyfile(original, copied)
        assert MODULE.sha256_file(copied) == record["sha256"]
        record["path"] = str(copied.resolve())
        provenance.write_text(json.dumps(payload), encoding="utf-8")
        selected_source = copied if role == "hebrew_asr" else source
        selected_translation = copied if role == "machine_english" else translation

        with pytest.raises(
            ValueError,
            match=rf"{role}.*outside the allowed private root",
        ):
            build_package_contents(
                selected_source,
                expected_segments=3,
                media_duration=Decimal("10.000"),
                provenance_path=provenance,
                translation_path=selected_translation,
                allowed_root=tmp_path,
                repo_root=ROOT,
                hf_cache_root=fixture_hf_cache_root(tmp_path),
                ollama_cache_root=fixture_ollama_cache_root(tmp_path),
            )


def test_build_rejects_exact_byte_provenance_copy_inside_repository(tmp_path: Path) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    generated_root = ROOT / "reports" / "generated"
    generated_root.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        prefix="aug12-provenance-root-adversary-", dir=generated_root
    ) as temporary_repo_dir:
        copied = Path(temporary_repo_dir) / provenance.name
        shutil.copyfile(provenance, copied)
        assert MODULE.sha256_file(copied) == MODULE.sha256_file(provenance)
        with pytest.raises(ValueError, match="private provenance.*outside the allowed private root"):
            build_package_contents(
                source,
                expected_segments=3,
                media_duration=Decimal("10.000"),
                provenance_path=copied,
                allowed_root=tmp_path,
                repo_root=ROOT,
                hf_cache_root=fixture_hf_cache_root(tmp_path),
                ollama_cache_root=fixture_ollama_cache_root(tmp_path),
            )


@pytest.mark.parametrize("command", ("build", "check"))
def test_cli_build_and_check_apply_identical_input_containment(
    tmp_path: Path, command: str
) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    output = tmp_path / "package"
    base_args = [
        "--source",
        str(source),
        "--output-dir",
        str(output),
        "--expected-segments",
        "3",
        "--media-duration",
        "10.000",
        "--provenance",
        str(provenance),
        "--allowed-root",
        str(tmp_path),
        "--repo-root",
        str(ROOT),
        "--hf-cache-root",
        str(fixture_hf_cache_root(tmp_path)),
    ]
    assert MODULE.main(["build", *base_args]) == 0
    payload = json.loads(provenance.read_text(encoding="utf-8"))
    record = next(
        item for item in payload["artifacts"] if item["role"] == "hebrew_asr_readable"
    )
    original = Path(record["path"])
    generated_root = ROOT / "reports" / "generated"
    generated_root.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        prefix="aug12-cli-root-adversary-", dir=generated_root
    ) as temporary_repo_dir:
        copied = Path(temporary_repo_dir) / original.name
        shutil.copyfile(original, copied)
        record["path"] = str(copied.resolve())
        provenance.write_text(json.dumps(payload), encoding="utf-8")
        with pytest.raises(
            ValueError,
            match="hebrew_asr_readable.*outside the allowed private root",
        ):
            MODULE.main([command, *base_args])


def test_private_artifact_rejects_symlinked_ancestor_inside_private_root(
    tmp_path: Path,
) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    payload = json.loads(provenance.read_text(encoding="utf-8"))
    record = next(item for item in payload["artifacts"] if item["role"] == "raw_chat")
    target = Path(record["path"])
    alias = tmp_path / "linked-evidence"
    try:
        alias.symlink_to(target.parent, target_is_directory=True)
    except OSError:
        pytest.skip("directory symlinks are not available in this environment")
    record["path"] = str(alias / target.name)
    provenance.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="raw_chat.*symlink or reparse"):
        build_package_contents(
            source,
            expected_segments=3,
            media_duration=Decimal("10.000"),
            provenance_path=provenance,
        )


def test_hf_model_blob_requires_the_exact_cache_location(tmp_path: Path) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    payload = json.loads(provenance.read_text(encoding="utf-8"))
    record = next(item for item in payload["artifacts"] if item["role"] == "asr_model_blob")
    original = Path(record["path"])
    substituted = fixture_hf_cache_root(tmp_path) / "same-cache-wrong-path.bin"
    shutil.copyfile(original, substituted)
    record["path"] = str(substituted.resolve())
    provenance.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="asr_model_blob.*exact Hugging Face cache path"):
        build_package_contents(
            source,
            expected_segments=3,
            media_duration=Decimal("10.000"),
            provenance_path=provenance,
        )


@pytest.mark.parametrize("role", ("ollama_model_blob", "ollama_model_manifest"))
def test_ollama_model_artifacts_require_exact_cache_locations(
    tmp_path: Path, role: str
) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    translation, _ = complete_translation_provenance(provenance, normalized_rows())
    payload = json.loads(provenance.read_text(encoding="utf-8"))
    record = next(item for item in payload["artifacts"] if item["role"] == role)
    original = Path(record["path"])
    substituted = fixture_ollama_cache_root(tmp_path) / f"wrong-{role}.bin"
    shutil.copyfile(original, substituted)
    record["path"] = str(substituted.resolve())
    provenance.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match=rf"{role}.*exact Ollama cache path"):
        build_package_contents(
            source,
            expected_segments=3,
            media_duration=Decimal("10.000"),
            provenance_path=provenance,
            translation_path=translation,
        )


def test_unknown_provenance_role_is_not_a_path_policy_bypass(tmp_path: Path) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    payload = json.loads(provenance.read_text(encoding="utf-8"))
    payload["artifacts"].append(
        {
            "role": "unclassified_transcript_copy",
            "path": str(source.resolve()),
            "bytes": source.stat().st_size,
            "sha256": MODULE.sha256_file(source),
        }
    )
    provenance.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="unsupported private provenance roles"):
        build_package_contents(
            source,
            expected_segments=3,
            media_duration=Decimal("10.000"),
            provenance_path=provenance,
        )


def test_hf_snapshot_symlink_must_resolve_inside_explicit_cache_root(tmp_path: Path) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    payload = json.loads(provenance.read_text(encoding="utf-8"))
    snapshot = Path(payload["asr"]["model"]["snapshot_path"])
    config = snapshot / "config.json"
    config.unlink()
    outside = tmp_path.parent / f"{tmp_path.name}-escaped-model-config.json"
    outside.write_bytes(b"fixture-config")
    try:
        config.symlink_to(outside)
    except OSError:
        outside.unlink(missing_ok=True)
        pytest.skip("file symlinks are not available in this environment")
    try:
        snapshot_sha = MODULE.sha256_tree(snapshot)
        payload["asr"]["model"]["snapshot_tree_sha256"] = snapshot_sha
        payload["asr"]["execution_record"]["model_snapshot_tree_sha256"] = snapshot_sha
        profile = dict(MODULE.AUG12_SOURCE_PROFILE)
        profile["asr_model_snapshot_tree_sha256"] = snapshot_sha
        MODULE.AUG12_SOURCE_PROFILE = profile
        provenance.write_text(json.dumps(payload), encoding="utf-8")

        with pytest.raises(ValueError, match="snapshot.*symlink.*outside.*cache root"):
            build_package_contents(
                source,
                expected_segments=3,
                media_duration=Decimal("10.000"),
                provenance_path=provenance,
            )
    finally:
        outside.unlink(missing_ok=True)


def test_trusted_builder_rejects_symlinked_repo_alias(tmp_path: Path) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    payload = json.loads(provenance.read_text(encoding="utf-8"))
    record = next(item for item in payload["artifacts"] if item["role"] == "evidence_builder")
    generated_root = ROOT / "reports" / "generated"
    generated_root.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        prefix="aug12-trusted-role-alias-", dir=generated_root
    ) as temporary_repo_dir:
        alias = Path(temporary_repo_dir) / "linked-scripts"
        try:
            alias.symlink_to(SCRIPT.parent, target_is_directory=True)
        except OSError:
            pytest.skip("directory symlinks are not available in this environment")
        record["path"] = str(alias / SCRIPT.name)
        provenance.write_text(json.dumps(payload), encoding="utf-8")

        with pytest.raises(ValueError, match="evidence_builder.*exact trusted repository"):
            build_package_contents(
                source,
                expected_segments=3,
                media_duration=Decimal("10.000"),
                provenance_path=provenance,
            )


@pytest.mark.parametrize("selected", ("source", "translation"))
def test_selected_transcript_inputs_reject_reparse_alias(
    tmp_path: Path, selected: str
) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    translation, _ = complete_translation_provenance(provenance, normalized_rows())
    target = source if selected == "source" else translation
    alias = tmp_path / f"linked-{target.name}"
    try:
        alias.symlink_to(target)
    except OSError:
        pytest.skip("file symlinks are not available in this environment")

    with pytest.raises(ValueError, match=rf"selected {selected}.*symlink or reparse"):
        build_package_contents(
            alias if selected == "source" else source,
            expected_segments=3,
            media_duration=Decimal("10.000"),
            provenance_path=provenance,
            translation_path=alias if selected == "translation" else translation,
        )


def test_hf_snapshot_internal_cache_symlinks_are_narrowly_allowed(tmp_path: Path) -> None:
    source = tmp_path / "machine.jsonl"
    source.write_text("\n".join(raw_lines()) + "\n", encoding="utf-8")
    provenance = private_provenance(tmp_path, source)
    payload = json.loads(provenance.read_text(encoding="utf-8"))
    snapshot = Path(payload["asr"]["model"]["snapshot_path"])
    config = snapshot / "config.json"
    cache_blob = snapshot.parents[1] / "blobs" / "fixture-config"
    cache_blob.write_bytes(config.read_bytes())
    config.unlink()
    try:
        config.symlink_to(cache_blob)
    except OSError:
        pytest.skip("file symlinks are not available in this environment")
    snapshot_sha = MODULE.sha256_tree(snapshot)
    payload["asr"]["model"]["snapshot_tree_sha256"] = snapshot_sha
    payload["asr"]["execution_record"]["model_snapshot_tree_sha256"] = snapshot_sha
    profile = dict(MODULE.AUG12_SOURCE_PROFILE)
    profile["asr_model_snapshot_tree_sha256"] = snapshot_sha
    MODULE.AUG12_SOURCE_PROFILE = profile
    provenance.write_text(json.dumps(payload), encoding="utf-8")

    assert build_package_contents(
        source,
        expected_segments=3,
        media_duration=Decimal("10.000"),
        provenance_path=provenance,
    )["artifact-manifest.json"]
