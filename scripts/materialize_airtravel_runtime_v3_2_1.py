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


def materialize_runtime(upstream_archive: Path, output_root: Path) -> Path:
    """Materialize and archive the exact five bytes with canonical ZIP metadata."""
    with zipfile.ZipFile(upstream_archive) as source:
        members = source.namelist()
        prefix = next(n[: n.rfind("dataset/AirTravel/") + len("dataset/AirTravel/")] for n in members if "dataset/AirTravel/" in n)
        files = {"domain_description/description.md": prefix + "description.md"}
        files.update({f"candidate_models/{i:02d}_{name}": prefix + name for i, name in enumerate(MODELS, 1)})
        output_root.mkdir(parents=True, exist_ok=True)
        for runtime_path, source_path in files.items():
            target = output_root / runtime_path
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
    (output_root / "cd_airtravel.runtime-config.json").write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    archive = output_root.parent / "cd_airtravel-runtime-v1.0.2.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for runtime_path in sorted(files):
            info = zipfile.ZipInfo("runtime_input/" + runtime_path, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            output.writestr(info, (output_root / runtime_path).read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return archive


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream-archive", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    archive = materialize_runtime(args.upstream_archive, args.output_root)
    print(archive)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
