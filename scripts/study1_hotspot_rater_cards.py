"""Build blinded episode cards for independent human raters, and the key that unblinds them.

A rating is only independent if the rater cannot read the answer off the card. Two things would
destroy that, and both are removed here rather than merely discouraged:

  * **the Detector-v1 classification and its signal names**, which would turn the rating into
    agreement-by-construction;
  * **the per-answer confidence label**, which is Detector-v1's dominant input. A rater shown
    `Low` is largely being asked to restate S1.

Cards are shuffled under a fixed seed and numbered, so card order carries no information about
run, case or alert class. The mapping back to episodes lives in a **separate key file** that no
rater receives. Nothing here computes or stores a label.

The card fields are exactly the five frozen in the manifest. This module refuses to emit a card
that carries a withheld field, so a future edit that widens the card fails instead of silently
unblinding the study.

No provider is contacted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from airtravel_detector_analysis import project_episodes  # noqa: E402

SHUFFLE_SEED = 20260909
COMPLETE = {"CONVERGED", "TERMINATED_MAX_ROUNDS"}
FORBIDDEN_IN_CARD = re.compile(
    r"STRONG_ALERT|WEAK_ALERT|NO_ALERT|EXCLUDED|S1_|S2_|S3_|S6_|S7_"
    r"|answer_confidence|detector|FULLFRAME|REAL-efe686a",
    re.IGNORECASE,
)
ALLOWED_CARD_KEYS = {
    "card_id",
    "exchanges",
    "route",
    "round_count",
    "question_count",
    "answers_with_evidence",
    "answers_without_evidence",
}


def load_events(output_dir: Path) -> list[dict[str, Any]]:
    path = output_dir / "qa_events.jsonl"
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def load_qa_text(output_dir: Path) -> dict[str, dict[str, Any]]:
    """Question and answer prose, keyed by question id, from both history files."""
    text: dict[str, dict[str, Any]] = {}
    for name in ("dom_qa_history.json", "lang_qa_history.json"):
        path = output_dir / name
        if not path.is_file():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload if isinstance(payload, list) else payload.get("qa_history", [])
        for row in rows:
            if isinstance(row, dict) and row.get("question_id"):
                text[row["question_id"]] = row
    return text


def build_cards(run_label: str, output_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    events = load_events(output_dir)
    qa_text = load_qa_text(output_dir)
    episodes = {ep["episode_id"]: ep for ep in project_episodes(events)}

    ordered: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        if event["event_type"] == "QUESTION_EMITTED":
            ordered.setdefault(event["episode_id"], []).append(event)
    answers = {
        (event["episode_id"], event.get("question_id")): event
        for event in events
        if event["event_type"] == "ANSWER_RECEIVED"
    }

    cards, key = [], []
    for episode_id, episode in episodes.items():
        if episode.get("termination_reason") not in COMPLETE:
            continue
        questions = ordered.get(episode_id, [])
        if not questions:
            continue
        exchanges, with_evidence, without_evidence, missing_text = [], 0, 0, 0
        for question in questions:
            row = qa_text.get(question.get("question_id"))
            if not row:
                missing_text += 1
                continue
            answer_event = answers.get((episode_id, question.get("question_id")))
            reference = (answer_event or {}).get("answer_evidence_ref")
            length = (reference or {}).get("length", 0)
            if length > 0:
                with_evidence += 1
            else:
                without_evidence += 1
            exchanges.append(
                {
                    "round": question.get("round_index"),
                    "question": row.get("question", ""),
                    "answer": row.get("answer", ""),
                    "evidence_present": bool(length),
                    "evidence_length_characters": length,
                }
            )
        if not exchanges:
            continue
        routes = sorted(
            {
                f"{question['source_agent']} asks {question['target_agent']}"
                for question in questions
            }
        )
        card = {
            "card_id": None,
            "exchanges": exchanges,
            "route": routes,
            "round_count": episode.get("round_count"),
            "question_count": len(questions),
            "answers_with_evidence": with_evidence,
            "answers_without_evidence": without_evidence,
        }
        cards.append(card)
        key.append(
            {
                "card_id": None,
                "run_label": run_label,
                "episode_id": episode_id,
                "exchanges_rendered": len(exchanges),
                "exchanges_without_retrievable_text": missing_text,
            }
        )
    return cards, key


def assign_ids(cards: list[dict[str, Any]], key: list[dict[str, Any]]) -> None:
    order = list(range(len(cards)))
    random.Random(SHUFFLE_SEED).shuffle(order)
    for position, index in enumerate(order, start=1):
        card_id = f"CARD-{position:03d}"
        cards[index]["card_id"] = card_id
        key[index]["card_id"] = card_id
    cards.sort(key=lambda card: card["card_id"])
    key.sort(key=lambda row: row["card_id"])


def audit_blinding(cards: list[dict[str, Any]]) -> list[str]:
    """Refuse to emit a card that carries a withheld field or a detector token."""
    problems = []
    for card in cards:
        extra = set(card) - ALLOWED_CARD_KEYS
        if extra:
            problems.append(f"{card['card_id']}: unexpected field(s) {sorted(extra)}")
        blob = json.dumps(card, ensure_ascii=False)
        for match in set(FORBIDDEN_IN_CARD.findall(blob)):
            problems.append(f"{card['card_id']}: contains withheld token {match!r}")
    return problems


def rater_form(cards: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "study1-hotspot-rater-form-v1",
        "instructions": (
            "For each card, answer all three questions using only what the card shows. Do not "
            "consult any other source, and do not discuss any card with the other rater. If the "
            "card does not give you enough to judge, choose 'Insufficient information' - that is "
            "a real answer, not a failure, and it is never treated as 'No'."
        ),
        "questions": [
            {
                "id": "R1_WORTHY",
                "prompt": "Is this episode worthy of human review?",
                "options": ["Yes", "No", "Insufficient information"],
                "select": "exactly one",
            },
            {
                "id": "R2_REASON",
                "prompt": "Why?",
                "options": [
                    "Low confidence",
                    "Missing evidence",
                    "Repeated clarification",
                    "Non-convergence",
                    "Other",
                ],
                "select": "one or more",
            },
            {
                "id": "R3_ACTION",
                "prompt": "What action would be appropriate?",
                "options": ["Verify", "Clarify", "Revise guideline", "No action"],
                "select": "exactly one",
            },
        ],
        "optional_time_field": {
            "id": "R4_MINUTES",
            "prompt": "Minutes spent on this card (optional).",
            "note": (
                "Leave blank if not measured. Review-time savings are reported only when this is "
                "actually recorded; they are never estimated."
            ),
        },
        "responses": [
            {"card_id": card["card_id"], "R1_WORTHY": None, "R2_REASON": [], "R3_ACTION": None,
             "R4_MINUTES": None}
            for card in cards
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="append", required=True, metavar="LABEL=OUTPUT_DIR")
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    all_cards: list[dict[str, Any]] = []
    all_key: list[dict[str, Any]] = []
    for spec in args.run:
        label, _, path = spec.partition("=")
        directory = Path(path)
        if not (directory / "qa_events.jsonl").is_file():
            print(json.dumps({"skipped": label, "reason": "no event log"}))
            continue
        cards, key = build_cards(label, directory)
        if not cards:
            print(json.dumps({"skipped": label, "reason": "no episode has retrievable Q&A text"}))
            continue
        all_cards.extend(cards)
        all_key.extend(key)

    if not all_cards:
        raise SystemExit("no cards could be built from any supplied run")

    assign_ids(all_cards, all_key)
    problems = audit_blinding(all_cards)
    if problems:
        raise SystemExit("blinding audit failed:\n" + "\n".join(problems))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    cards_path = args.out_dir / "rater-cards.json"
    key_path = args.out_dir / "card-key-DO-NOT-SHARE-WITH-RATERS.json"
    form_path = args.out_dir / "rater-form-template.json"

    cards_payload = {
        "schema_version": "study1-hotspot-cards-v1",
        "card_count": len(all_cards),
        "blinding_audit": "PASS",
        "withheld": [
            "Detector-v1 classification and signal names",
            "per-answer confidence label",
            "run, case and generating-model identifiers",
        ],
        "cards": all_cards,
    }
    cards_path.write_text(
        json.dumps(cards_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    key_path.write_text(
        json.dumps({"schema_version": "study1-hotspot-card-key-v1", "key": all_key},
                   indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    form_path.write_text(
        json.dumps(rater_form(all_cards), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(
        json.dumps(
            {
                "cards": len(all_cards),
                "blinding_audit": "PASS",
                "cards_sha256": hashlib.sha256(cards_path.read_bytes()).hexdigest(),
                "cards_path": str(cards_path),
                "key_path": str(key_path),
                "form_path": str(form_path),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
