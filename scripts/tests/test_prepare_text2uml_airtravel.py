from __future__ import annotations

import argparse
import json
import pathlib
import sys
from pathlib import Path

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from prepare_text2uml_airtravel import prepare  # noqa: E402


def test_airtravel_preparation_is_metadata_only_and_separates_references(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    source = repo / "dataset" / "AirTravel"
    source.mkdir(parents=True)
    (repo / "LICENSE").write_text("GPL-3.0\n", encoding="utf-8")
    (source / "description.md").write_text("domain", encoding="utf-8")
    (source / "metadata.txt").write_text("name: Air Travel", encoding="utf-8")
    (source / "plantuml.txt").write_text("@startuml\nclass A\n@enduml\n", encoding="utf-8")
    (source / "plantuml_adjusted.txt").write_text("@startuml\nclass A\n@enduml\n", encoding="utf-8")
    (source / "result_one_claude-sonnet-4-6.txt").write_text("@startuml\nclass A\n@enduml\n", encoding="utf-8")
    (source / "result_one_codestral-2508.txt").write_text("@startuml\nclass B\n@enduml\n", encoding="utf-8")
    (source / "result_one_deepseek-chat.txt").write_text("@startuml\nclass C\n@enduml\n", encoding="utf-8")
    (source / "result_one_gemini-2.5-flash.txt").write_text("@startuml\nclass D\n@enduml\n", encoding="utf-8")
    args = argparse.Namespace(source_root=source, repository_root=repo,
                              output_root=tmp_path / "out", upstream_sha="a" * 40,
                              archive=None, stage_root=tmp_path / "external",
                              retrieval_timestamp="2026-09-04T00:00:00+00:00")
    prepare(args)
    manifest = json.loads((args.output_root / "source-manifest.json").read_text())
    assert len(manifest["files"]) == 8
    proposal = json.loads((args.output_root / "candidate-subset-proposal.json").read_text())
    assert proposal["actual_proposed_n"] == 4
    staged = json.loads((args.output_root / "staging-hash-check.json").read_text())
    assert [row["case_id"] for row in staged] == ["01", "02", "03", "04"]
    assert all(row["byte_identical"] for row in staged)
    assert not (args.stage_root / "prepared" / "AirTravel" / "runtime_input" / "candidate_models" / "plantuml.txt").exists()
