import pytest

from knowledge_sync.sync import ConnectorNotConfigured, plan_sync


def test_codecium_sync_is_blocked_without_configured_connector() -> None:
    with pytest.raises(ConnectorNotConfigured):
        plan_sync(target="codecium", records=[])
