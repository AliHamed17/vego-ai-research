from __future__ import annotations

import argparse
from pathlib import Path

from knowledge_sync.retrieve import retrieve

parser = argparse.ArgumentParser()
parser.add_argument("--database", required=True, type=Path)
parser.add_argument("--project", required=True)
parser.add_argument("--query", required=True)
parser.add_argument("--max-records", type=int, default=5)
args = parser.parse_args()
print(retrieve(args.database, project=args.project, query=args.query, max_records=args.max_records).rendered_markdown)
