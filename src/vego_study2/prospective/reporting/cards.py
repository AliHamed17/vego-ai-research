"""Blinded, redacted rater cards built from private ON evidence.

Cards carry no case id, episode id, condition label, Detector-v1 label or
timestamp.  The unblinding key is written next to them in the private root.
Only the card count and digests are published.
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path
from typing import Any

from .. import constants as c

ROOT = Path(__file__).resolve().parents[4]


def _framework_on_path() -> None:
    path = str(ROOT / "VEGO-AI" / "framework")
    if path not in sys.path:
        sys.path.insert(0, path)


def _histories(pipeline_dir: Path) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for name in ("lang_qa_history.json", "dom_qa_history.json"):
        path = pipeline_dir / name
        if not path.is_file():
            continue
        for row in json.loads(path.read_text(encoding="utf-8")):
            if isinstance(row, dict) and row.get("question_id"):
                lookup[str(row["question_id"])] = row
    return lookup


def build_cards(output_root: Path, public_dir: Path, *, seed: int = c.SELECTION_SEED) -> dict[str, Any]:
    _framework_on_path()
    from qa_communication import build_episode_projection, load_event_stream

    on_dir = output_root / "on"
    event_path = on_dir / "qa_events.jsonl"
    review_dir = output_root / "human-review"
    review_dir.mkdir(exist_ok=True)
    if not event_path.is_file():
        summary = {"cards": 0, "reason": "no ON event stream"}
        _write_public(public_dir, summary)
        return summary
    events = load_event_stream(event_path)
    episodes = build_episode_projection(events)
    histories = _histories(on_dir / "pipeline")
    by_episode: dict[str, list[dict[str, Any]]] = {}
    case_by_episode: dict[str, str | None] = {}
    for event in events:
        if event["event_type"] == "QUESTION_EMITTED":
            by_episode.setdefault(event["episode_id"], []).append(event)
            case_by_episode.setdefault(event["episode_id"], event.get("case_id"))
    answers_by_episode: dict[str, dict[str, dict[str, Any]]] = {}
    for event in events:
        if event["event_type"] == "ANSWER_RECEIVED":
            answers_by_episode.setdefault(event["episode_id"], {})[str(event.get("question_id"))] = event

    rng = random.Random(seed)
    cards, key = [], []
    for episode in episodes:
        if not episode["scientific_complete"]:
            continue
        exchanges = []
        for question in by_episode.get(episode["episode_id"], []):
            qid = str(question.get("question_id"))
            history = histories.get(qid, {})
            answer_event = answers_by_episode.get(episode["episode_id"], {}).get(qid, {})
            evidence = history.get("evidence")
            exchanges.append({
                "question": history.get("question") or "[question text not recovered]",
                "answer": history.get("answer") or "[answer text not recovered]",
                "reported_confidence": answer_event.get("answer_confidence") or history.get("confidence"),
                "reported_evidence": evidence if evidence else None,
                "target_advisor": "language" if question.get("target_agent") == "agent1" else "domain",
            })
        card_id = f"CARD-{rng.getrandbits(40):010x}"
        cards.append({
            "card_id": card_id,
            "round_count": episode["round_count"],
            "termination": {"CONVERGED": "converged", "TERMINATED_MAX_ROUNDS": "reached the maximum number of rounds"}.get(
                episode["termination_reason"], str(episode["termination_reason"])),
            "exchanges": exchanges,
            "decision": None,
            "action": None,
            "R1": None, "R2": None, "R3": None, "R4": None, "R5": None,
            "note": "",
        })
        key.append({"card_id": card_id, "episode_id": episode["episode_id"], "case_id": case_by_episode.get(episode["episode_id"]) or "SETTING_LEVEL"})
    rng.shuffle(cards)
    order = {card["card_id"]: index for index, card in enumerate(cards)}
    key.sort(key=lambda row: order[row["card_id"]])
    cards_path = review_dir / "cards.json"
    key_path = review_dir / "card-key.json"
    cards_path.write_text(json.dumps(cards, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    key_path.write_text(json.dumps(key, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    summary = {
        "cards": len(cards),
        "exchanges": sum(len(card["exchanges"]) for card in cards),
        "cards_sha256": hashlib.sha256(cards_path.read_bytes()).hexdigest(),
        "key_sha256": hashlib.sha256(key_path.read_bytes()).hexdigest(),
        "location": f"{c.PRIVATE_ROOT_TOKEN}/study2-prospective/{output_root.name}/human-review/",
        "blinding": "no case id, episode id, condition, detector label or timestamp on any card; order shuffled with a fixed seed",
        "status": "NOT_MEASURED",
        "raters_scored": 0,
    }
    _write_public(public_dir, summary)
    return summary


def _write_public(public_dir: Path, summary: dict[str, Any]) -> None:
    public_dir.mkdir(parents=True, exist_ok=True)
    (public_dir / "human-review-cards.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
