from knowledge_sync.contracts import KnowledgeRecord, validate_record


def test_restricted_record_cannot_target_github() -> None:
    record = KnowledgeRecord(
        record_id="K-20260822-001",
        project="vego-ai",
        classification="restricted",
        source_kind="meeting_export",
        source_ref="restricted:meeting-2026-08-20",
        sha256="a" * 64,
        summary="Restricted meeting evidence.",
        review_state="pending_human_review",
        publish_target="github",
    )

    assert validate_record(record) == ["restricted records cannot publish to github"]
