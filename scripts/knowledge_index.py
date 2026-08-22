from __future__ import annotations

import argparse
from pathlib import Path

from knowledge_sync.retrieve import build_index

parser = argparse.ArgumentParser()
parser.add_argument("--records-root", required=True, type=Path)
parser.add_argument("--database", required=True, type=Path)
args = parser.parse_args()
build_index(args.records_root, args.database)
print(args.database)
