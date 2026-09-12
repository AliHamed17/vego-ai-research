from __future__ import annotations

import argparse

from knowledge_sync.sync import ConnectorNotConfigured, plan_sync

parser = argparse.ArgumentParser()
parser.add_argument("--target", required=True)
args = parser.parse_args()
try:
    print(plan_sync(target=args.target, records=[]))
except ConnectorNotConfigured as error:
    raise SystemExit(str(error)) from error
