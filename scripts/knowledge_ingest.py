from __future__ import annotations

import argparse
from pathlib import Path

from knowledge_sync.ingest import ingest_file

parser = argparse.ArgumentParser()
parser.add_argument("--source", required=True, type=Path)
parser.add_argument("--records-root", required=True, type=Path)
parser.add_argument("--project", required=True)
parser.add_argument("--classification", required=True)
parser.add_argument("--source-kind", required=True)
args = parser.parse_args()
record = ingest_file(
    source=args.source,
    records_root=args.records_root,
    project=args.project,
    classification=args.classification,
    source_kind=args.source_kind,
)
print(record.record_id)
