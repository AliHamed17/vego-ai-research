"""
qa_registry.py — global, thread-safe Q&A ID counter.

All agents share this counter so that Q_lang_NNN and Q_dom_NNN IDs
are unique across the entire pipeline run, even when case models are
processed concurrently.
"""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass, field
from typing import Literal


QAScope = Literal["lang", "dom"]

_ID_RE = re.compile(r"^Q_(lang|dom)_(\d+)$")


@dataclass
class QARegistry:
    """Monotonically increasing ID registry for both language and domain questions."""

    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)
    _counters: dict[QAScope, int] = field(
        default_factory=lambda: {"lang": 0, "dom": 0}, init=False
    )
    # Accumulated Q&A history keyed by question ID
    lang_qa: list[dict] = field(default_factory=list)
    dom_qa: list[dict] = field(default_factory=list)
    # Counters restart per setting, so ids are unique only within one; every record
    # carries its setting so a cross-setting join can never merge unrelated Q&A.
    setting_id: str = ""

    def seed_counters_from_history(self) -> None:
        """Advance each counter past the highest id already present in lang_qa /
        dom_qa. Called on resume so a restarted run never re-issues an id that a
        previous run already assigned to a different question (which silently
        misattributed one case's answer to another)."""
        for scope, records in (("lang", self.lang_qa), ("dom", self.dom_qa)):
            highest = self._counters[scope]
            for rec in records:
                m = _ID_RE.match(str(rec.get("question_id") or rec.get("id") or ""))
                if m and m.group(1) == scope:
                    highest = max(highest, int(m.group(2)))
            self._counters[scope] = highest

    async def next_id(self, scope: QAScope) -> str:
        async with self._lock:
            self._counters[scope] += 1
            n = self._counters[scope]
        return f"Q_{scope}_{n:03d}"

    async def allocate_ids(
        self, questions: list[dict], scope: QAScope
    ) -> list[dict]:
        """
        Replace placeholder IDs in a list of question dicts with globally unique IDs.
        Returns a new list with updated 'id' fields.
        """
        result = []
        for q in questions:
            new_id = await self.next_id(scope)
            result.append({**q, "id": new_id})
        return result

    async def record_answers(
        self,
        answers: list[dict],
        scope: QAScope,
        questions: list[dict] | None = None,
        provenance: dict | None = None,
    ) -> None:
        """Persist each answer joined to the question that produced it.

        Answers alone cannot be audited: the saved history has to carry the
        originating question text and which agent, case and round asked it, or the
        join is unverifiable once the run is over."""
        by_id = {q.get("id"): q for q in (questions or []) if q.get("id")}
        records = []
        for answer in answers:
            if not isinstance(answer, dict):
                continue
            record = dict(answer)
            source = by_id.get(record.get("question_id")) or {}
            if source.get("question") and not record.get("question"):
                record["question"] = source["question"]
            for key, value in (provenance or {}).items():
                record.setdefault(key, value)
            record.setdefault("scope", scope)
            if self.setting_id:
                record.setdefault("setting_id", self.setting_id)
            records.append(record)
        async with self._lock:
            if scope == "lang":
                self.lang_qa.extend(records)
            else:
                self.dom_qa.extend(records)
