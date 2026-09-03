"""Deterministic, bidi-aware supervisor-artifact text scanning helpers."""

import argparse
import json
import unicodedata
from pathlib import Path


BIDI_CONTROL_CODEPOINTS = {
    0x202A,  # LRE
    0x202B,  # RLE
    0x202C,  # PDF
    0x202D,  # LRO
    0x202E,  # RLO
    0x2066,  # LRI
    0x2067,  # RLI
    0x2068,  # FSI
    0x2069,  # PDI
    0x200E,  # LRM
    0x200F,  # RLM
    0x200B,  # zero-width space found in some PDF extractors
}
BIDI_CONTROLS = "".join(chr(codepoint) for codepoint in sorted(BIDI_CONTROL_CODEPOINTS))


def strip_bidi_controls(text: str) -> str:
    """Remove bidi/zero-width controls before deterministic pattern matching."""

    return unicodedata.normalize("NFC", text).translate({ord(char): None for char in BIDI_CONTROLS})


def scan_patterns(text: str, patterns: list[str]) -> dict[str, dict[str, object]]:
    """Return a result for every pattern; one missing pattern never aborts the scan."""

    normalized = strip_bidi_controls(text)
    return {
        pattern: {"found": pattern in normalized, "count": normalized.count(pattern)}
        for pattern in patterns
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("pattern", nargs="+", help="patterns to scan")
    args = parser.parse_args()
    text = args.file.read_text(encoding="utf-8")
    print(json.dumps(scan_patterns(text, args.pattern), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
