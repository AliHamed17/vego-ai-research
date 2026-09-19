"""Regression tests for Q&A question-id correlation and unanswered-question reporting."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "framework"))

import agent1_language_advisor as a1  # noqa: E402
import agent2_domain_advisor as a2  # noqa: E402
import orchestrator  # noqa: E402
from qa_instrumented_runner import asked_question_ids  # noqa: E402


def lang_prompt(questions):
    return a1.answer_language_question_prompt(
        language_name="UML", language_template={}, questions=questions)


def dom_prompt(questions):
    return a2.answer_domain_question_prompt(
        domain_description="d", reference_guidelines={}, questions=questions,
        domain_identifier="x")


def test_language_ids_exclude_output_format_examples():
    asked = [{"id": "Q_lang_005", "question": "five"}, {"id": "Q_lang_006", "question": "six"}]
    assert asked_question_ids(lang_prompt(asked)) == ["Q_lang_005", "Q_lang_006"]


def test_domain_ids_exclude_output_format_examples():
    asked = [{"id": "Q_dom_004", "question": "four"}]
    assert asked_question_ids(dom_prompt(asked)) == ["Q_dom_004"]


def test_domain_example_ids_are_never_returned_when_unasked():
    ids = asked_question_ids(dom_prompt([{"id": "Q_dom_004", "question": "four"}]))
    assert "Q_dom_001" not in ids
    assert "Q_dom_002" not in ids


def test_ids_preserve_the_order_they_were_asked_in():
    asked = [{"id": "Q_dom_009", "question": "a"}, {"id": "Q_dom_004", "question": "b"},
             {"id": "Q_dom_007", "question": "c"}]
    assert asked_question_ids(dom_prompt(asked)) == ["Q_dom_009", "Q_dom_004", "Q_dom_007"]


def test_a_real_id_equal_to_the_example_id_is_still_returned_once():
    assert asked_question_ids(lang_prompt([{"id": "Q_lang_001", "question": "a"}])) == ["Q_lang_001"]


def test_prompt_without_questions_yields_no_ids():
    assert asked_question_ids({"system": "no questions here", "user": ""}) == []


def test_unanswered_questions_are_reported_not_dropped(caplog):
    asked = [{"id": "Q_lang_001"}, {"id": "Q_lang_002"}, {"id": "Q_lang_003"}]
    answers = [{"question_id": "Q_lang_002", "answer": "only this one"}]
    with caplog.at_level(logging.WARNING, logger=orchestrator.logger.name):
        missing = orchestrator._report_unanswered(asked, answers, "lang")
    assert missing == ["Q_lang_001", "Q_lang_003"]
    assert "Q_lang_001" in caplog.text and "Q_lang_003" in caplog.text


def test_fully_answered_exchange_reports_nothing(caplog):
    asked = [{"id": "Q_dom_001"}]
    answers = [{"question_id": "Q_dom_001", "answer": "a"}]
    with caplog.at_level(logging.WARNING, logger=orchestrator.logger.name):
        assert orchestrator._report_unanswered(asked, answers, "dom") == []
    assert caplog.text == ""


def test_report_unanswered_tolerates_malformed_answer_entries():
    asked = [{"id": "Q_dom_001"}]
    assert orchestrator._report_unanswered(asked, [None, "junk"], "dom") == ["Q_dom_001"]


@pytest.mark.parametrize("scope,prompt_fn,qid", [
    ("lang", lang_prompt, "Q_lang_012"),
    ("dom", dom_prompt, "Q_dom_012"),
])
def test_correlation_holds_for_both_scopes(scope, prompt_fn, qid):
    assert asked_question_ids(prompt_fn([{"id": qid, "question": "q"}])) == [qid]
