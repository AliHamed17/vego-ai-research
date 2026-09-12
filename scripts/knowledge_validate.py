from __future__ import annotations

import argparse
from pathlib import Path

from knowledge_sync.validate import validate_records

parser = argparse.ArgumentParser()
parser.add_argument("--records-root", required=True, type=Path)
args = parser.parse_args()
errors = validate_records(args.records_root)
if errors:
    raise SystemExit("\n".join(errors))
print("PASS")
