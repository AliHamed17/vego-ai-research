from pathlib import Path

from obsidian_brain.search import VaultSearch
from obsidian_brain.vault import ObsidianVault


def test_search_returns_a_hash_linked_result_without_exposing_source_body(tmp_path: Path) -> None:
    vault = ObsidianVault.initialize(tmp_path / "Private Brain", encryption_verified=lambda _: True)
    search = VaultSearch(vault)
    search.index(
        item_id="OBS-1",
        sha256="a" * 64,
        title="Electricity bill",
        text="Account 123456; amount due 125 ILS",
    )

    result = search.query("electricity")

    assert result == [result[0]]
    assert result[0].item_id == "OBS-1"
    assert result[0].sha256 == "a" * 64
    assert not hasattr(result[0], "text")
    assert search.database.is_relative_to(vault.archive_root)
