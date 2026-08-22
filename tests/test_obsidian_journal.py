from pathlib import Path

from obsidian_brain.journal import InteractionJournal
from obsidian_brain.vault import ObsidianVault


def test_prompt_journal_retains_hashes_and_writes_no_prompt_body_to_note(tmp_path: Path) -> None:
    vault = ObsidianVault.initialize(tmp_path / "Private Brain", encryption_verified=lambda _: True)
    journal = InteractionJournal(vault)

    event = journal.record(
        source="codex", user_input="Summarize account 123456", output="Summary complete"
    )

    note = (vault.notes_root / "Activity" / f"{event.event_id}.md").read_text(
        encoding="utf-8"
    )
    assert event.input_sha256 in note
    assert event.output_sha256 in note
    assert "account 123456" not in note.casefold()


def test_prompt_journal_rejects_untrusted_source_labels(tmp_path: Path) -> None:
    vault = ObsidianVault.initialize(tmp_path / "Private Brain", encryption_verified=lambda _: True)
    journal = InteractionJournal(vault)

    try:
        journal.record(source="codex\nprivate body", user_input="prompt", output="output")
    except ValueError as error:
        assert "source" in str(error)
    else:
        raise AssertionError("untrusted source label was accepted")
