"""Regression guard: AirTravel fixture helpers must not leak module state."""

from __future__ import annotations

import importlib


def test_airtravel_fixture_helpers_leave_registry_and_context_clean() -> None:
    observer = importlib.import_module("airtravel_local_observer")
    orchestrator = importlib.import_module("orchestrator")
    registry = importlib.import_module("qa_registry")

    assert observer.CURRENT.get() is None
    assert orchestrator.QARegistry is registry.QARegistry
