from __future__ import annotations

import argparse
from collections.abc import Callable, Sequence
from pathlib import Path

from .adapters import AdapterRegistry
from .dashboard import render_dashboard_note
from .vault import EncryptionUnavailable, ObsidianVault
from .windows_efs import verify_windows_efs


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Initialize or refresh the local Obsidian secondary brain.")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "refresh"):
        command = commands.add_parser(name)
        command.add_argument("--vault-root", type=Path, required=True)
    return parser


def run(
    argv: Sequence[str] | None = None,
    *,
    encryption_verified: Callable[[Path], bool] | None = None,
) -> int:
    args = _parser().parse_args(argv)
    verifier = encryption_verified or verify_windows_efs
    if args.command == "init":
        vault = ObsidianVault.initialize(args.vault_root, encryption_verified=verifier)
        print(f"Initialized private Obsidian vault at {vault.root}")
        return 0
    if not args.vault_root.exists() or not verifier(args.vault_root):
        raise EncryptionUnavailable("Refresh refused because the vault encryption cannot be verified.")
    render_dashboard_note(args.vault_root / "Obsidian Notes", AdapterRegistry.default())
    print("Refreshed local Obsidian dashboard.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
