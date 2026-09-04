"""Materialize the five-file AirTravel runtime pack from verified upstream bytes."""
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

MODELS = [
    "result_one_claude-sonnet-4-6.txt",
    "result_one_codestral-2508.txt",
    "result_one_deepseek-chat.txt",
    "result_one_gemini-2.5-flash.txt",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream-archive", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    with zipfile.ZipFile(args.upstream_archive) as source:
        members = source.namelist()
        prefix = next(n[: n.rfind("dataset/AirTravel/") + len("dataset/AirTravel/")] for n in members if "dataset/AirTravel/" in n)
        files = {"domain_description/description.md": prefix + "description.md"}
        files.update({f"candidate_models/{i:02d}_{name}": prefix + name for i, name in enumerate(MODELS, 1)})
        args.output_root.mkdir(parents=True, exist_ok=True)
        for runtime_path, source_path in files.items():
            target = args.output_root / runtime_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read(source_path))
    config = {
        "setting_id": "cd_airtravel",
        "corpus_id": "text2uml_airtravel_253b26dc",
        "provider_execution_enabled": False,
        "description_path": "domain_description/description.md",
        "candidate_models_dir": "candidate_models",
        "runtime_files": sorted(files),
    }
    (args.output_root / "cd_airtravel.runtime-config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    archive = args.output_root.parent / "cd_airtravel-runtime-v1.0.2.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as output:
        for runtime_path in sorted(files):
            output.write(args.output_root / runtime_path, "runtime_input/" + runtime_path)
    print(archive)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
