from __future__ import annotations

from dataclasses import dataclass

from .contracts import KnowledgeRecord


class ConnectorNotConfigured(RuntimeError):
    """Raised when an external connector is not explicitly configured and approved."""


@dataclass(frozen=True)
class SyncManifest:
    target: str
    record_ids: list[str]
    mode: str = "dry_run"


def plan_sync(*, target: str, records: list[KnowledgeRecord]) -> SyncManifest:
    if target == "codecium":
        raise ConnectorNotConfigured(
            "Codecium is disabled until product, workspace, authentication, retention, and approval are configured."
        )
    if target not in {"local", "github"}:
        raise ValueError("unsupported sync target")
    unsafe = [record.record_id for record in records if record.classification in {"restricted", "secret"}]
    if unsafe and target != "local":
        raise ValueError(f"{target} cannot receive restricted records: {', '.join(unsafe)}")
    return SyncManifest(target=target, record_ids=[record.record_id for record in records])
