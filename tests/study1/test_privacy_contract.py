import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

import pytest
from jsonschema import Draft202012Validator

import vego_study1.privacy as privacy
from vego_study1.c0 import candidate_to_replay_event
from vego_study1.privacy import (
    PrivacyValidationError,
    validate_candidate_event,
    validate_tracked_artifacts,
)

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas" / "study1" / "CandidateEscalationEvent-v1.schema.json"
EXAMPLE_PATH = (
    ROOT / "schemas" / "study1" / "examples" / "candidate-escalation-event-v1.synthetic.json"
)
VALIDATOR_SCRIPT = ROOT / "scripts" / "validate_study1_privacy.py"
REVIEW_POLICY_SIGNAL_IDS = (
    "claim_uncertainty",
    "unreviewed_error_consequence",
    "evidence_quality",
    "reviewer_competence_for_claim",
    "current_queue_conditions",
    "novelty_vs_judgment_store",
    "cross_agent_disagreement",
    "expected_future_reuse_value",
)


def synthetic_event() -> dict:
    return {
        "schema_version": "CandidateEscalationEvent-v1",
        "event_id": "8d9f2f51-3f06-4569-9a99-9a12a3286c34",
        "source": {"source_hash": "sha256:" + "a" * 64},
        "stage": "case_inspection",
        "item_type": "candidate_interaction",
        "sanitized_local_locator": {
            "storage_scope": "private_workspace",
            "locator_hash": "sha256:" + "b" * 64,
        },
        "signals": [
            {
                "signal_id": signal_id,
                "observation": {"kind": "policy_input", "normalized_value": 0.25},
                "evidence_state": "observed",
            }
            for signal_id in REVIEW_POLICY_SIGNAL_IDS
        ],
        "claim_boundary": "candidate_escalation_only",
    }


def test_schema_and_public_example_validate_a_synthetic_candidate_event():
    """Catches a missing or invalid published event-contract artifact."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))

    assert validate_candidate_event(synthetic_event(), schema=schema) == synthetic_event()
    assert (
        validate_candidate_event(example, schema=schema)["claim_boundary"]
        == "candidate_escalation_only"
    )


@pytest.mark.parametrize(
    ("mutate", "expected_message"),
    [
        (
            lambda event: event["signals"].__setitem__(
                0,
                {
                    "signal_id": "unknown_signal",
                    "observation": {"kind": "policy_input", "normalized_value": 0.25},
                    "evidence_state": "observed",
                },
            ),
            "unknown signal",
        ),
        (lambda event: event["source"].pop("source_hash"), "source_hash"),
        (lambda event: event["signals"][0].pop("evidence_state"), "evidence_state"),
        (
            lambda event: event["sanitized_local_locator"].update(
                {"raw_locator": "synthetic-local-item"}
            ),
            "raw locator",
        ),
        (lambda event: event.__setitem__("claim_boundary", "verified_finding"), "claim_boundary"),
    ],
)
def test_event_validator_rejects_privacy_or_claim_contract_violations(mutate, expected_message):
    """Catches validation branches that would admit unsafe candidate events."""
    event = synthetic_event()
    mutate(event)

    with pytest.raises(PrivacyValidationError, match=expected_message):
        validate_candidate_event(event)


def test_event_validator_accepts_derived_evidence_state():
    """Catches a contract that rejects the required derived evidence state."""
    event = synthetic_event()
    event["signals"][0]["evidence_state"] = "derived"

    assert validate_candidate_event(event)["signals"][0]["evidence_state"] == "derived"


@pytest.mark.parametrize(
    "observation",
    [
        "C:" + "/" + "private/raw-note.txt",
        {"kind": "unknown", "value": "raw note text"},
        {"kind": "policy_input", "normalized_value": 1.1},
        {"kind": "policy_input"},
    ],
)
def test_event_validator_rejects_free_form_unknown_or_out_of_range_observations(observation):
    """Catches candidate observations that cannot map exactly to replay input."""
    event = synthetic_event()
    event["signals"][0]["observation"] = observation

    with pytest.raises(PrivacyValidationError, match="observation|schema violation"):
        validate_candidate_event(event)


def test_candidate_schema_rejects_numeric_and_force_missing_observation() -> None:
    """Catches contradictory candidate facts satisfying both policy-input branches."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    event = synthetic_event()
    event["signals"][0]["observation"] = {
        "kind": "policy_input",
        "normalized_value": 0.8,
        "missing_value_policy": "force_undetermined",
    }

    assert list(Draft202012Validator(schema).iter_errors(event))


def test_candidate_conversion_rejects_numeric_and_force_missing_observation() -> None:
    """Catches replay conversion discarding a validated numeric observation as missing."""
    event = synthetic_event()
    event["signals"][0]["observation"] = {
        "kind": "policy_input",
        "normalized_value": 0.8,
        "missing_value_policy": "force_undetermined",
    }

    with pytest.raises(PrivacyValidationError, match="observation|schema violation"):
        candidate_to_replay_event(event)


@pytest.mark.parametrize(
    ("evidence_state", "observation"),
    [
        ("unavailable", {"kind": "policy_input", "normalized_value": 0.4}),
        ("observed", {"kind": "unavailable"}),
        ("derived", {"kind": "unavailable"}),
    ],
)
def test_event_validator_ties_observation_shape_to_evidence_state(evidence_state, observation):
    """Catches unavailable evidence carrying values or available evidence carrying no fact."""
    event = synthetic_event()
    event["signals"][0].update({"evidence_state": evidence_state, "observation": observation})

    with pytest.raises(PrivacyValidationError, match="observation|schema violation"):
        validate_candidate_event(event)


def test_event_validator_rejects_non_contract_evidence_state():
    """Catches a contract that admits evidence states outside the three-state vocabulary."""
    event = synthetic_event()
    event["signals"][0]["evidence_state"] = "not_applicable"

    with pytest.raises(PrivacyValidationError, match="evidence_state"):
        validate_candidate_event(event)


def test_event_validator_rejects_duplicate_signal_id_even_when_observations_differ():
    """Catches eight distinct signal objects that do not cover all eight policy signals."""
    event = synthetic_event()
    event["signals"][-1] = {
        "signal_id": "claim_uncertainty",
        "observation": {"kind": "policy_input", "normalized_value": 0.75},
        "evidence_state": "observed",
    }

    with pytest.raises(PrivacyValidationError, match="exactly one observation"):
        validate_candidate_event(event)


def test_event_validator_rejects_non_uuid_event_id():
    """Catches schema-only UUID annotations that do not validate helper input."""
    event = synthetic_event()
    event["event_id"] = "synthetic-event-id"

    with pytest.raises(PrivacyValidationError, match="event_id"):
        validate_candidate_event(event)


def test_event_validator_rejects_legacy_signal_id():
    """Catches a contract that accepts identifiers outside ReviewPolicySignalContract-v1."""
    event = synthetic_event()
    event["signals"][0]["signal_id"] = "prompt_scope"

    with pytest.raises(PrivacyValidationError, match="unknown signal"):
        validate_candidate_event(event)


def test_event_validator_rejects_routing_outcome_as_stage():
    """Catches a stage vocabulary that encodes routing outcomes instead of policy workflow stages."""
    event = synthetic_event()
    event["stage"] = "triaged"

    with pytest.raises(PrivacyValidationError, match="stage"):
        validate_candidate_event(event)


def test_public_example_round_trips_to_bounded_replay_semantics():
    """Catches an example that validates but loses or invents replay signal semantics."""
    example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))

    replay = candidate_to_replay_event(example)
    observations = {item["signalId"]: item for item in replay["signalObservations"]}

    assert observations["claim_uncertainty"] == {
        "signalId": "claim_uncertainty",
        "normalizedValue": 0.8,
        "missing": False,
    }
    assert replay["explicitEscalationRequests"] == [
        {
            "signalId": "claim_uncertainty",
            "trigger": "agent_requested_human_review",
            "evidenceState": "observed",
        }
    ]
    assert observations["evidence_quality"] == {
        "signalId": "evidence_quality",
        "missing": True,
        "missingValuePolicy": "force_undetermined",
    }
    assert observations["novelty_vs_judgment_store"] == {
        "signalId": "novelty_vs_judgment_store",
        "normalizedValue": 0.9,
        "missing": False,
    }
    assert observations["unreviewed_error_consequence"] == {
        "signalId": "unreviewed_error_consequence",
        "missing": True,
        "missingValuePolicy": "exclude_from_score",
    }


def test_candidate_conversion_validates_input_before_replay_translation():
    """Catches conversion paths that silently reinterpret malformed candidate observations."""
    event = synthetic_event()
    event["signals"][0]["observation"] = {"kind": "unavailable"}

    with pytest.raises(PrivacyValidationError, match="observation|schema violation"):
        candidate_to_replay_event(event)


def test_candidate_conversion_preserves_observed_request_and_derived_confidence() -> None:
    """Catches co-occurring facts being collapsed into one missing numeric observation."""
    event = synthetic_event()
    event["signals"][0].update(
        {
            "observation": {"kind": "policy_input", "normalized_value": 0.8},
            "evidence_state": "derived",
            "escalation_request": {
                "kind": "requires_human_review",
                "evidence_state": "observed",
            },
        }
    )

    validated = validate_candidate_event(event)
    replay = candidate_to_replay_event(validated)

    assert validated["signals"][0]["escalation_request"]["evidence_state"] == "observed"
    assert replay["signalObservations"][0] == {
        "signalId": "claim_uncertainty",
        "normalizedValue": 0.8,
        "missing": False,
    }
    assert replay["explicitEscalationRequests"] == [
        {
            "signalId": "claim_uncertainty",
            "trigger": "agent_requested_human_review",
            "evidenceState": "observed",
        }
    ]


def test_candidate_validator_rejects_legacy_collapsed_force_escalation_observation() -> None:
    """Catches review requests being encoded as missing numeric signal values again."""
    event = synthetic_event()
    event["signals"][0]["observation"] = {
        "kind": "policy_input",
        "normalized_value": 0.8,
        "missing_value_policy": "force_escalation",
    }

    with pytest.raises(PrivacyValidationError, match="observation.*enum|schema violation"):
        validate_candidate_event(event)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda event: event["signals"][1].update(
            {
                "escalation_request": {
                    "kind": "requires_human_review",
                    "evidence_state": "observed",
                }
            }
        ),
        lambda event: event["signals"][0].update(
            {
                "escalation_request": {
                    "kind": "requires_human_review",
                    "evidence_state": "derived",
                }
            }
        ),
    ],
)
def test_candidate_validator_bounds_explicit_review_request_semantics(mutate) -> None:
    """Catches review-request facts attached to the wrong signal or provenance state."""
    event = synthetic_event()
    mutate(event)

    with pytest.raises(PrivacyValidationError, match="schema violation"):
        validate_candidate_event(event)


@pytest.mark.parametrize("non_finite", [float("nan"), float("inf"), float("-inf")])
def test_candidate_validator_rejects_non_finite_numbers_without_echoing_values(
    non_finite: float,
) -> None:
    """Catches non-finite candidate values crossing the JSON validation boundary."""
    event = synthetic_event()
    event["signals"][0]["observation"]["normalized_value"] = non_finite

    with pytest.raises(PrivacyValidationError, match="non_finite_number") as captured:
        validate_candidate_event(event)

    assert repr(non_finite) not in str(captured.value).casefold()


def test_candidate_non_finite_error_does_not_echo_adversarial_instance_key() -> None:
    """Catches arbitrary input keys leaking through a recursive validation path."""
    event = synthetic_event()
    private_key = "C:" + "/" + "sensitive/control" + "led/field"
    event[private_key] = float("nan")

    with pytest.raises(PrivacyValidationError, match="non_finite_number") as captured:
        validate_candidate_event(event)

    assert private_key not in str(captured.value)


def test_candidate_schema_errors_report_only_field_and_category() -> None:
    """Catches rejected private instance text being reflected in validation errors."""
    event = synthetic_event()
    private_value = "C:" + "/" + "sensitive/control" + "led/item.json"
    event["stage"] = private_value

    with pytest.raises(PrivacyValidationError) as captured:
        validate_candidate_event(event)

    message = str(captured.value)
    assert message == "candidate event schema violation at stage [enum]"
    assert private_value not in message


@pytest.mark.parametrize(
    "payload",
    [b'{"value":NaN}', b'{"value":Infinity}', b'{"value":-Infinity}', b'{"value":1e999}'],
)
def test_public_json_byte_scanner_rejects_every_non_finite_numeric_form(payload: bytes) -> None:
    """Catches non-portable JSON numbers in exact tracked or staged object bytes."""
    assert (1, "non_finite_json_number") in privacy.public_artifact_byte_findings(
        payload, relative_path="docs/public.json"
    )


def test_tracked_artifact_validator_reports_only_unsafe_synthetic_markers(tmp_path):
    """Catches a scanner that misses proposed tracked-artifact privacy leaks."""
    safe = tmp_path / "safe.json"
    safe.write_text('{"source_hash": "sha256:synthetic"}', encoding="utf-8")
    unsafe = tmp_path / "unsafe.txt"
    unsafe.write_text(
        "\n".join(
            (
                "RAW_" + "CONTROLLED_CONTENT",
                "https://" + "drive.google.com/file/d/" + "1" + "abcdefghijklmnopqrstuvwxYZ",
                "API_" + "KEY=synthetic-token-value",
            )
        ),
        encoding="utf-8",
    )

    findings = validate_tracked_artifacts([safe, unsafe])

    assert [finding.kind for finding in findings] == [
        "controlled_content_marker",
        "drive_url",
        "drive_id",
        "credential_like",
    ]
    assert all(finding.path == unsafe for finding in findings)


@pytest.mark.parametrize(
    ("unsafe_content", "expected_kind"),
    [
        ('{"uri": "file' + '://host/private.bin"}', "remote_or_unc_reference"),
        ("uri: 's3" + "://private-bucket/object'", "remote_or_unc_reference"),
        ('{"uri": "gs' + '://private-bucket/object"}', "remote_or_unc_reference"),
        ('{"path": "/' + "/" + 'server/share/object"}', "remote_or_unc_reference"),
        ('{"path": "/' + 'mnt/secure/object"}', "absolute_path_reference"),
        ('{"host": "review.' + 'internal"}', "private_host_reference"),
        ('{"endpoint": "https://' + 'service.' + 'local/value"}', "private_url"),
    ],
)
def test_privacy_scanner_rejects_quoted_remote_values_and_private_hosts(
    tmp_path, unsafe_content, expected_kind
):
    """Catches public-artifact URI leaks regardless of JSON/YAML quoting."""
    unsafe = tmp_path / "unsafe.yaml"
    unsafe.write_text(unsafe_content, encoding="utf-8")

    assert expected_kind in {finding.kind for finding in validate_tracked_artifacts([unsafe])}


def _structured_credential_bytes(suffix: str) -> bytes:
    """Build credential-shaped bytes at runtime without tracking a complete sample."""
    field_name = "api_" + "key"
    field_value = "abc" + "DEF12345" + "67890"
    if suffix == ".json":
        encoded_name = field_name.replace("k", "\\u006b", 1)
        return (
            '{"'
            + encoded_name
            + '":"'
            + field_value[:8]
            + "\\n"
            + field_value[8:]
            + '"}'
        ).encode()
    return (field_name + ": >-\n  " + field_value[:8] + "\n  " + field_value[8:] + "\n").encode()


def _credential_fallback_bytes(suffix: str) -> bytes:
    """Build an unsafe shell fallback only at runtime so no credential sample is tracked."""
    field_name = "api_" + "key"
    fallback = (
        "${"
        + "STUDY1_TOKEN"
        + ":-"
        + "abc"
        + "DEF12345"
        + "67890"
        + "}"
    )
    if suffix == ".json":
        return json.dumps({field_name: fallback}).encode()
    return (field_name + ": " + json.dumps(fallback) + "\n").encode()


def _encoded_drive_locator() -> str:
    locator = (
        "https://"
        + "drive."
        + "google.com/file/d/"
        + "1"
        + "A" * 28
    )
    return quote(locator, safe="")


def _unicode_locator_cases() -> tuple[tuple[str, str], ...]:
    return (
        (_encoded_drive_locator(), "drive_url"),
        ("/" + "安全" + "/" + "記録", "absolute_path_reference"),
        (
            chr(92) * 2 + "伺服器" + chr(92) + "共享" + chr(92) + "記録",
            "remote_or_unc_reference",
        ),
    )


@pytest.mark.parametrize("suffix", [".json", ".yaml"])
def test_structured_scanner_preserves_credential_key_value_association(suffix: str) -> None:
    """Catches escaped or folded structured credentials split into separately safe scalars."""
    findings = privacy.public_artifact_byte_findings(
        _structured_credential_bytes(suffix),
        relative_path="docs/public" + suffix,
    )

    assert "credential_like" in {kind for _line, kind in findings}


@pytest.mark.parametrize(
    ("payload", "relative_path"),
    [
        (
            json.dumps(
                {"serviceAccount" + "Password" + "Value": "סוד"},
                ensure_ascii=False,
            ).encode(),
            "docs/public.json",
        ),
        (
            (("service-" + "token-copy") + ': "秘密"\n').encode(),
            "docs/public.yaml",
        ),
        (
            json.dumps({"client_" + "secret_hint": True}).encode(),
            "docs/public.json",
        ),
    ],
)
def test_structured_scanner_rejects_any_non_placeholder_credential_scalar(
    payload: bytes, relative_path: str
) -> None:
    """Catches compound credential keys, Unicode values, and non-string scalar bypasses."""
    findings = privacy.public_artifact_byte_findings(payload, relative_path=relative_path)

    assert "credential_like" in {kind for _line, kind in findings}


def test_structured_scanner_preserves_credential_context_for_a_reused_yaml_alias() -> None:
    """Catches a safe-first YAML alias skipped when reused under a credential-like key."""
    payload = (
        'public_label: &shared "synthetic unicode 私密"\n'
        + ("service-" + "token-copy")
        + ": *shared\n"
    ).encode()

    findings = privacy.public_artifact_byte_findings(
        payload,
        relative_path="docs/public.yaml",
    )

    assert "credential_like" in {kind for _line, kind in findings}


def test_structured_scanner_terminates_safely_on_a_cyclic_yaml_alias() -> None:
    """Catches per-context alias traversal that recurses forever on a YAML cycle."""
    findings = privacy.public_artifact_byte_findings(
        b"root: &node\n  child: *node\n",
        relative_path="docs/public.yaml",
    )

    assert "unparseable_structured_artifact" not in {kind for _line, kind in findings}


def test_structured_scanner_keeps_explicit_credential_placeholders_public_safe() -> None:
    """Catches credential hardening that rejects an explicit environment placeholder."""
    payload = json.dumps(
        {"serviceAccount" + "Password" + "Value": "${STUDY1_PLACEHOLDER}"}
    ).encode()

    findings = privacy.public_artifact_byte_findings(
        payload,
        relative_path="docs/public.json",
    )

    assert "credential_like" not in {kind for _line, kind in findings}


@pytest.mark.parametrize("suffix", [".json", ".yaml"])
def test_direct_scanner_rejects_shell_fallbacks_under_credential_keys(suffix: str) -> None:
    """Catches a literal fallback hidden inside a non-bare credential placeholder."""
    findings = privacy.public_artifact_byte_findings(
        _credential_fallback_bytes(suffix),
        relative_path="docs/public" + suffix,
    )

    assert "credential_like" in {kind for _line, kind in findings}


def test_direct_scanner_rejects_shell_fallbacks_in_plain_assignments() -> None:
    """Catches arbitrary text treating every shell expansion as a safe credential placeholder."""
    findings = privacy.public_artifact_byte_findings(
        _credential_fallback_bytes(".env"),
        relative_path="docs/public.env",
    )

    assert "credential_like" in {kind for _line, kind in findings}


@pytest.mark.parametrize(("locator", "expected_kind"), _unicode_locator_cases())
def test_direct_scanner_decodes_and_classifies_encoded_or_unicode_locators(
    locator: str, expected_kind: str
) -> None:
    """Catches locator classification before percent decoding or with ASCII-only path tokens."""
    findings = privacy.public_artifact_byte_findings(
        ("Locator " + locator).encode(),
        relative_path="docs/public.md",
    )

    assert expected_kind in {kind for _line, kind in findings}


@pytest.mark.parametrize(
    ("unsafe_content", "expected_kind"),
    [
        ("Review endpoint: https://" + "10." + "23.4.5:8443/item", "private_url"),
        ("Review endpoint: https://" + "[fd00" + "::1]/item", "private_url"),
        ("Open " + "/" + "mnt/secure/item.json next", "absolute_path_reference"),
        ("Contact ali" + "ce@" + "example.test for access", "email_identifier"),
        ("Fetch g" + chr(115) + ":private-bucket/item", "remote_or_unc_reference"),
        (
            "Open "
            + chr(0xFF23)
            + chr(0xFF1A)
            + chr(0xFF3C)
            + "private"
            + chr(0xFF3C)
            + "item.json",
            "absolute_path_reference",
        ),
        (
            "Open " + chr(0xFF0F) * 2 + "server" + chr(0xFF0F) + "share/item",
            "remote_or_unc_reference",
        ),
        (
            "Download https://"
            + "drive."
            + "usercontent.google.com/download?id="
            + "0B"
            + "A" * 28,
            "drive_url",
        ),
        ("Legacy locator " + "0B" + "A" * 28, "drive_id"),
        ("Host review" + chr(0xFF0E) + "internal", "private_host_reference"),
    ],
)
def test_text_scanner_classifies_locator_and_identifier_tokens(
    unsafe_content: str, expected_kind: str
) -> None:
    """Catches private locators and direct identifiers embedded in ordinary prose."""
    findings = privacy.public_artifact_byte_findings(
        unsafe_content.encode(),
        relative_path="docs/public.md",
    )

    assert expected_kind in {kind for _line, kind in findings}


def test_text_scanner_allows_a_public_scholarly_url() -> None:
    """Catches broad locator matching that blocks a public scholarly citation."""
    findings = privacy.public_artifact_byte_findings(
        b"See https://proceedings.mlr.press/v119/example.html for context.",
        relative_path="docs/public.md",
    )

    assert not findings


@pytest.mark.parametrize(
    ("payload", "expected_kind"),
    [
        (b'{"uri":"g\\u0073:\\/\\/private-bucket\\/item"}', "remote_or_unc_reference"),
        (b'{"uri":"' + b"data" + b':text/plain;base64,U0VDUkVU"}', "remote_or_unc_reference"),
        (
            b'{"path":"' + b"\\" + b"u002fmnt" + b"\\" + b'u002fsecure/item"}',
            "absolute_path_reference",
        ),
        (
            b'{"path":"'
            + b"\\"
            + b"u005c"
            + b"\\"
            + b"u005cserver"
            + b"\\"
            + b"u005cshare/item"
            + b'"}',
            "remote_or_unc_reference",
        ),
        (b'{"host":"review\\u002einternal"}', "private_host_reference"),
        (
            b'{"uri":"' + b"sha256" + b':\\/\\/server\\/share\\/item"}',
            "remote_or_unc_reference",
        ),
        (b'{"host":"10\\u002e0\\u002e0\\u002e1"}', "private_host_reference"),
    ],
)
def test_structured_scanner_rejects_decoded_json_scalar_values(
    payload: bytes, expected_kind: str
) -> None:
    """Catches encoded structured values bypassing the raw-byte matcher."""
    findings = privacy.public_artifact_byte_findings(
        payload,
        relative_path="docs/public.json",
    )

    assert expected_kind in {kind for _line, kind in findings}


@pytest.mark.parametrize(
    ("payload", "relative_path"),
    [
        (b'{"unterminated":', "docs/public.json"),
        (b"value: [unterminated\n", "docs/public.yaml"),
    ],
)
def test_structured_scanner_fails_closed_when_decoding_is_impossible(
    payload: bytes, relative_path: str
) -> None:
    """Catches malformed structured artifacts being treated as sanitized text."""
    assert (1, "unparseable_structured_artifact") in privacy.public_artifact_byte_findings(
        payload,
        relative_path=relative_path,
    )


def test_drive_id_matcher_ignores_public_package_url_path_tokens() -> None:
    """Catches content-addressed package paths being confused with bare Drive IDs."""
    public_token = "1" + "a" * 63
    payloads = (
        f"https://files.pythonhosted.org/packages/{public_token}/package.whl".encode(),
        f"https://files.pythonhosted.org/packages/public-package-1-{public_token}.whl".encode(),
    )

    for payload in payloads:
        assert "drive_id" not in {
            kind
            for _line, kind in privacy.public_artifact_byte_findings(
                payload,
                relative_path="uv.lock",
            )
        }


def test_privacy_validator_cli_accepts_the_public_synthetic_example():
    """Catches direct CLI execution that loses the repository src import path."""
    result = subprocess.run(
        [sys.executable, str(VALIDATOR_SCRIPT), "--repository-root", str(ROOT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def _git(repository: Path, *arguments: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
    )


def _staged_repository(tmp_path: Path, content: bytes, *, name: str = "public.json") -> Path:
    repository = tmp_path / "staged-repository"
    repository.mkdir()
    _git(repository, "init", "-q")
    _git(repository, "config", "user.email", "study1@" + "example.test")
    _git(repository, "config", "user.name", "Study 1 Test")
    (repository / "README.md").write_text("base\n", encoding="utf-8")
    _git(repository, "add", "README.md")
    _git(repository, "commit", "-qm", "base")
    artifact = repository / "docs" / name
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(content)
    _git(repository, "add", "--", f"docs/{name}")
    return repository


def test_staged_privacy_scan_decodes_exact_index_json_scalars(tmp_path: Path) -> None:
    """Catches staged encoded private hosts hidden from the raw index-byte matcher."""
    repository = _staged_repository(
        tmp_path,
        b'{"host":"review\\u002einternal","uri":"i\\u0070f'
        + b's:'
        + b"\\/"
        + b"\\/"
        + b'private-item"}',
    )

    scan = privacy.scan_staged_artifacts(repository)

    assert {finding.kind for finding in scan.findings} >= {
        "private_host_reference",
        "remote_or_unc_reference",
    }


@pytest.mark.parametrize("suffix", [".json", ".yaml"])
def test_staged_privacy_scan_detects_structured_credential_association(
    tmp_path: Path, suffix: str
) -> None:
    """Catches the index scan losing decoded credential key/value association."""
    repository = _staged_repository(
        tmp_path,
        _structured_credential_bytes(suffix),
        name="public" + suffix,
    )

    scan = privacy.scan_staged_artifacts(repository)

    assert "credential_like" in {finding.kind for finding in scan.findings}


def test_staged_privacy_scan_preserves_reused_yaml_alias_credential_context(
    tmp_path: Path,
) -> None:
    """Catches exact index scanning that loses the second context of a YAML alias."""
    payload = (
        'public_label: &shared "synthetic unicode 私密"\n'
        + ("service-" + "token-copy")
        + ": *shared\n"
    ).encode()
    repository = _staged_repository(tmp_path, payload, name="public.yaml")

    scan = privacy.scan_staged_artifacts(repository)

    assert "credential_like" in {finding.kind for finding in scan.findings}


@pytest.mark.parametrize("suffix", [".json", ".yaml"])
def test_staged_privacy_scan_rejects_credential_shell_fallbacks(
    tmp_path: Path, suffix: str
) -> None:
    """Catches exact index scanning that allowlists a non-bare credential placeholder."""
    repository = _staged_repository(
        tmp_path,
        _credential_fallback_bytes(suffix),
        name="public" + suffix,
    )

    scan = privacy.scan_staged_artifacts(repository)

    assert "credential_like" in {finding.kind for finding in scan.findings}


@pytest.mark.parametrize(("locator", "expected_kind"), _unicode_locator_cases())
def test_staged_privacy_scan_decodes_and_classifies_encoded_or_unicode_locators(
    tmp_path: Path, locator: str, expected_kind: str
) -> None:
    """Catches exact index scans that miss encoded Drive and Unicode path or UNC tokens."""
    repository = _staged_repository(
        tmp_path,
        ("Locator " + locator + "\n").encode(),
        name="public.md",
    )

    scan = privacy.scan_staged_artifacts(repository)

    assert expected_kind in {finding.kind for finding in scan.findings}


def test_staged_privacy_scan_normalizes_arbitrary_text_locator_tokens(tmp_path: Path) -> None:
    """Catches exact index scanning that classifies raw rather than normalized prose."""
    payload = ("Fetch g" + chr(115) + ":private-bucket/item\n").encode()
    repository = _staged_repository(tmp_path, payload, name="public.md")

    scan = privacy.scan_staged_artifacts(repository)

    assert "remote_or_unc_reference" in {finding.kind for finding in scan.findings}


@pytest.mark.parametrize(
    ("name", "expected_kind"),
    [
        ("archive/review." + "internal/public.md", "private_host_reference"),
        ("archive/ali" + "ce@" + "example.test/public.md", "email_identifier"),
        (
            "archive/api_" + "key=abc" + "DEF1234567890/public.md",
            "credential_like",
        ),
    ],
)
def test_staged_privacy_scan_applies_privacy_rules_to_the_whole_pathname(
    tmp_path: Path, name: str, expected_kind: str
) -> None:
    """Catches path-only private metadata outside the legacy special directory names."""
    repository = _staged_repository(tmp_path, b"sanitized\n", name=name)

    scan = privacy.scan_staged_artifacts(repository)

    assert expected_kind in {finding.kind for finding in scan.findings}


def test_privacy_cli_scans_nul_delimited_index_bytes_from_any_cwd(tmp_path: Path) -> None:
    """Catches dirty masking, CWD drift, and working-tree reads in one regression."""
    unsafe = ("RAW" + "_CONTROLLED_CONTENT\n").encode()
    repository = _staged_repository(tmp_path, unsafe, name="public artifact.json")
    artifact = repository / "docs" / "public artifact.json"
    artifact.write_text('{"status": "sanitized dirty mask"}\n', encoding="utf-8")
    nested_cwd = repository / "nested" / "cwd"
    nested_cwd.mkdir(parents=True)
    environment = dict(os.environ)
    environment.pop("PYTHONPATH", None)

    completed = subprocess.run(
        [
            sys.executable,
            "-B",
            str(VALIDATOR_SCRIPT),
            "--repository-root",
            str(repository),
        ],
        cwd=nested_cwd,
        env=environment,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 1, completed.stderr
    assert "controlled_content_marker" in completed.stdout
    assert "public artifact.json" not in completed.stdout


def test_staged_path_parser_preserves_newlines_inside_nul_delimited_names() -> None:
    """Catches line-oriented parsing of Git's NUL-delimited staged path stream."""
    assert hasattr(privacy, "_decode_nul_paths")
    assert privacy._decode_nul_paths(b"docs/public\nartifact.json\0docs/second.json\0") == (
        "docs/public\nartifact.json",
        "docs/second.json",
    )


def test_staged_privacy_scan_fails_closed_for_undecodable_object_bytes(tmp_path: Path) -> None:
    """Catches invalid UTF-8 staged object bytes being silently skipped."""
    repository = _staged_repository(tmp_path, b"\xff\xfeprivate")

    assert hasattr(privacy, "scan_staged_artifacts")
    scan = privacy.scan_staged_artifacts(repository)

    assert [finding.kind for finding in scan.findings] == ["undecodable_or_binary_artifact"]


def test_staged_privacy_scan_fails_closed_when_an_index_object_is_missing(tmp_path: Path) -> None:
    """Catches a missing staged object being treated as an empty or safe artifact."""
    repository = _staged_repository(tmp_path, b'{"status": "safe"}\n')
    object_id = _git(repository, "rev-parse", ":docs/public.json").stdout.decode("ascii").strip()
    loose_object = repository / ".git" / "objects" / object_id[:2] / object_id[2:]
    os.chmod(loose_object, 0o600)
    loose_object.unlink()

    assert hasattr(privacy, "scan_staged_artifacts")
    with pytest.raises(PrivacyValidationError, match="staged_object_unreadable"):
        privacy.scan_staged_artifacts(repository)
