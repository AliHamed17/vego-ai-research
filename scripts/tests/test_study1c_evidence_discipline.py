"""Regression tests for the evidence discipline the package must not lose again.

Each test corresponds to a claim that was published and then withdrawn. The point is not that the
code currently behaves; it is that a future edit which restores the old behaviour fails loudly
instead of shipping.

  * a run whose evidence chain is not verifiable from the head is never labelled executed;
  * no artefact of the hotspot study carries `PROSPECTIVE EMPIRICAL EVIDENCE`;
  * `CONDITIONAL GO` is prohibited by the ledger and absent from the tracked package;
  * a screening fraction always carries the sentence denying it is saved work;
  * rows from two runs cannot reach a table that scores one denominator;
  * a results builder refuses to publish an unverifiable run.

No provider is contacted and nothing is executed.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import study1_hotspot_analysis as analysis  # noqa: E402
import study1c_claim_ledger as ledger_module  # noqa: E402
import study1c_reconciliation as recon_module  # noqa: E402

RECON_JSON = ROOT / "docs/research/phd-proposal/study1c-reconciliation.json"
LEDGER_JSON = ROOT / "docs/research/phd-proposal/study1c-claim-ledger.json"
MANIFEST_JSON = ROOT / "docs/research/phd-proposal/study1-hotspot-manifest.json"
UNVERIFIED = "PREREGISTERED_NOT_EXECUTED_OR_UNVERIFIED"


WITHDRAWAL_MARKERS = (
    "never", "withdrawn", "not be labelled", "unattainable", "~~", "prohibited",
    "no artefact", "not verifiable", "no longer", "why_prohibited", "unsupported",
    "was wrong", "implies a scope", "replaced by",
    "נמשכה", "אסור", "בלתי־מאומתת",
)
CONTEXT_BEFORE, CONTEXT_AFTER = 3, 4


def denied_in_context(lines: list[str], index: int) -> bool:
    """A denial rarely sits on the same line as the phrase it denies.

    In prose it wraps onto the previous line; in a pretty-printed JSON object it lands several
    keys later. The window spans both, and the negative control below proves the guard still
    rejects a bare assertion with no denial anywhere near it.
    """
    window = " ".join(lines[max(0, index - CONTEXT_BEFORE): index + CONTEXT_AFTER]).lower()
    return any(marker.lower() in window for marker in WITHDRAWAL_MARKERS)


def tracked_text_files() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "docs/research/phd-proposal", "scripts"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    keep = {".md", ".json", ".html", ".py", ".ps1"}
    return [
        ROOT / line
        for line in out.stdout.splitlines()
        if line.strip() and Path(line).suffix in keep and (ROOT / line).is_file()
    ]


class TestUnverifiedRunsAreNeverPublishedAsExecuted:
    @pytest.fixture(scope="class")
    @staticmethod
    def recon():
        return json.loads(RECON_JSON.read_text(encoding="utf-8"))

    def test_hotspot_is_labelled_unverified(self, recon):
        row = next(r for r in recon["runs"] if r["run_id"] == "HOTSPOT-01")
        assert row["execution_status"] == UNVERIFIED
        assert row["evidence_class"] == UNVERIFIED
        assert row["sample_class"] == "PILOT_INFORMED_POST_OUTCOME"

    def test_an_unverified_run_publishes_no_counts(self, recon):
        row = next(r for r in recon["runs"] if r["execution_status"] == UNVERIFIED)
        for key in ("complete_episodes", "detector_class_STRONG_ALERT",
                    "detector_class_WEAK_ALERT", "detector_class_NO_ALERT",
                    "calls_reserved", "calls_completed"):
            assert row[key] == "NOT_AVAILABLE", f"{key} leaked a value for an unverified run"
        assert row["cost"]["status"] == "NOT_AVAILABLE"

    def test_execution_status_never_rests_on_a_local_artefact(self, recon):
        for row in recon["runs"]:
            if row["execution_status"] == "EXECUTED":
                assert row.get("private_evidence_mounted_locally") is True
        row = next(r for r in recon["runs"] if r["run_id"] == "HOTSPOT-01")
        assert row["private_evidence_mounted_locally"] != row["independently_verifiable_from_this_head"]

    def test_every_row_carries_the_generating_head_sha(self, recon):
        """The recorded SHA is the head the file was generated against.

        It cannot equal the live HEAD, because committing the file moves HEAD past it. What must
        hold is that every row agrees with the report's own header and that the value is a real
        commit id, so a reader can tell which tree the numbers came from.
        """
        top = recon["head_sha"]
        assert len(top) == 40 and all(c in "0123456789abcdef" for c in top)
        for row in recon["runs"]:
            assert row["head_sha"] == top

    def test_there_is_no_total_row(self, recon):
        ids = [row["run_id"] for row in recon["runs"]]
        assert not any(token in i.upper() for i in ids for token in ("TOTAL", "POOLED", "ALL_RUNS"))
        assert recon["pooling"].startswith("PROHIBITED")

    def test_the_five_required_rows_are_present(self, recon):
        assert {row["run_id"] for row in recon["runs"]} == {
            "REAL-efe686a-20260905T2303Z", "FULLFRAME-01", "FULLFRAME-02",
            "HOTSPOT-01", "OFFLINE_FIXTURES",
        }


class TestVerdictAndProhibitedWording:
    @pytest.fixture(scope="class")
    @staticmethod
    def ledger():
        return json.loads(LEDGER_JSON.read_text(encoding="utf-8"))

    def test_the_reconciliation_carries_the_required_verdict(self):
        recon = json.loads(RECON_JSON.read_text(encoding="utf-8"))
        assert recon["verdict"] == (
            "DESCRIPTIVE_RULE_BEHAVIOUR_ONLY / NOT_READY_FOR_SCIENTIFIC_CONCLUSION"
        )

    def test_conditional_go_is_prohibited_by_the_ledger(self, ledger):
        assert any("CONDITIONAL GO" in row["claim"] for row in ledger["prohibited"])

    @pytest.mark.parametrize(
        "phrase",
        ["demonstrably prioritizes", "only remaining blocker", "Retention of review-worthy"],
    )
    def test_each_withdrawn_claim_is_listed_as_prohibited(self, ledger, phrase):
        assert any(phrase in row["claim"] for row in ledger["prohibited"])

    def test_conditional_go_is_never_asserted_only_ever_withdrawn(self):
        offenders = []
        for path in tracked_text_files():
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
            for index, line in enumerate(lines):
                if "CONDITIONAL GO" in line and not denied_in_context(lines, index):
                    offenders.append(f"{path.name}: {line.strip()[:90]}")
        assert not offenders, (
            "CONDITIONAL GO asserted rather than withdrawn:\n" + "\n".join(offenders)
        )

    def test_the_guard_rejects_a_bare_assertion_with_no_denial_nearby(self):
        """Negative control: without it, widening the window could make the guard inert."""
        planted = ["filler"] * 8 + ["This run is CONDITIONAL GO."] + ["filler"] * 8
        assert not denied_in_context(planted, 8)
        denied = ["The verdict was withdrawn."] + ["This run was CONDITIONAL GO."]
        assert denied_in_context(denied, 1)

    def test_no_hotspot_artefact_asserts_prospective_evidence(self):
        offenders = []
        for path in tracked_text_files():
            if "hotspot" not in path.name.lower():
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            lines = text.splitlines()
            for index, line in enumerate(lines):
                if "PROSPECTIVE EMPIRICAL EVIDENCE" not in line:
                    continue
                if not denied_in_context(lines, index):
                    offenders.append(f"{path.name}: {line.strip()[:90]}")
        assert not offenders, "prospective evidence asserted:\n" + "\n".join(offenders)


class TestScreeningFractionCarriesItsDenial:
    def test_the_denial_sentence_is_exact(self):
        assert recon_module.SCREENING_DENIAL == (
            "A reduced number of episodes selected by a rule is not evidence of reduced human "
            "workload, retained useful cases, correctness, benefit, or safety without blinded "
            "human ratings and measured review time."
        )

    def test_every_scored_row_attaches_the_denial(self):
        recon = json.loads(RECON_JSON.read_text(encoding="utf-8"))
        for row in recon["runs"]:
            if row.get("unvalidated_screening_fraction") is not None and "NOT_AVAILABLE" not in str(
                row.get("unvalidated_screening_fraction")
            ):
                assert row["unvalidated_screening_fraction_meaning"] == recon_module.SCREENING_DENIAL

    def test_the_report_states_the_denial_at_top_level(self):
        recon = json.loads(RECON_JSON.read_text(encoding="utf-8"))
        assert recon["unvalidated_screening_fraction_meaning"] == recon_module.SCREENING_DENIAL


class TestPoolingIsImpossibleByDefault:
    def rows(self, label):
        return [
            {"run_label": label, "episode_id": f"{label}-1", "complete": True,
             "classification": "STRONG_ALERT"},
        ]

    def test_two_runs_in_one_table_raise(self):
        with pytest.raises(analysis.PooledDenominatorError):
            analysis.table_b(self.rows("A") + self.rows("B"), None, None)

    def test_two_runs_in_the_operational_table_raise(self):
        with pytest.raises(analysis.PooledDenominatorError):
            analysis.table_c(self.rows("A") + self.rows("B"), None, None, [], None)

    def test_a_single_run_is_accepted(self):
        assert analysis.table_b(self.rows("A"), None, None)["denominator_complete_episodes"] == 1


class TestResultsBuildersRefuseUnverifiableRuns:
    def test_the_package_builder_refuses_while_the_run_is_unverifiable(self):
        module = __import__("build_study1_hotspot_package_he")
        with pytest.raises(module.UnverifiableRunError, match="not verifiable from this head"):
            module.refuse_unverifiable(RECON_JSON)

    def test_the_package_builder_refuses_when_the_reconciliation_is_absent(self):
        module = __import__("build_study1_hotspot_package_he")
        with pytest.raises(module.UnverifiableRunError, match="absent"):
            module.refuse_unverifiable(ROOT / "docs/research/phd-proposal/does-not-exist.json")

    def test_the_deck_builder_carries_the_same_guard(self):
        """Checked by source: the deck imports python-pptx, which CI does not install."""
        source = (ROOT / "scripts/build_study1_hotspot_deck_he.py").read_text(encoding="utf-8")
        assert "class UnverifiableRunError" in source
        assert "refuse_unverifiable(ROOT /" in source
        assert "PREREGISTERED_NOT_EXECUTED_OR_UNVERIFIED" in source


class TestManifestKeepsItsFrozenStatus:
    def test_the_manifest_still_declares_not_executed(self):
        manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        assert manifest["status"] == "PREREGISTERED_NOT_EXECUTED"

    def test_the_manifest_declares_the_post_outcome_sample_class(self):
        manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        assert manifest["sample_class"] == "PILOT_INFORMED_POST_OUTCOME"

    def test_the_ledger_and_reconciliation_agree_on_the_verdict(self):
        recon = json.loads(RECON_JSON.read_text(encoding="utf-8"))
        ledger = json.loads(LEDGER_JSON.read_text(encoding="utf-8"))
        assert any(recon["verdict"] in row["claim"] for row in ledger["permitted"])

    def test_the_ledger_module_and_its_output_agree(self):
        built = ledger_module.build()
        published = json.loads(LEDGER_JSON.read_text(encoding="utf-8"))
        assert built["counts"] == published["counts"]
