from __future__ import annotations

import json
import os
import sys
from typing import Any


SCORE_STORAGE_KEY = "pyxel-rogue-scores-v1"
SCORE_FILE = os.environ.get(
    "PYXEL_ROGUE_SCORE_FILE",
    os.path.join(os.path.expanduser("~"), ".pyxel_rogue_scores_v1.json"),
)


def score_value(gold: int, result_flags: str) -> int:
    gold = max(0, int(gold))
    if result_flags in ("killed", "killed_with_amulet"):
        return gold * 9 // 10
    return gold


def build_score_entry(
    *,
    score: int = 0,
    result_flags: str,
    level: int,
    killer: str,
    player_name: str,
    timestamp: str,
    gold: int,
) -> dict[str, Any]:
    return {
        "score": int(score) if score else score_value(gold, result_flags),
        "result_flags": result_flags,
        "level": int(level),
        "killer": str(killer),
        "player_name": str(player_name),
        "timestamp": str(timestamp),
    }


def get_top_scores(entries: list[dict[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
    return sorted(entries, key=lambda entry: int(entry.get("score", 0)), reverse=True)[:limit]


def _read_web_scores() -> list[dict[str, Any]]:
    from js import localStorage

    raw = localStorage.getItem(SCORE_STORAGE_KEY)
    if not raw:
        return []
    data = json.loads(str(raw))
    return data if isinstance(data, list) else []


def _write_web_scores(entries: list[dict[str, Any]]) -> None:
    from js import localStorage

    localStorage.setItem(SCORE_STORAGE_KEY, json.dumps(entries, ensure_ascii=False))


def _read_file_scores() -> list[dict[str, Any]]:
    if not os.path.exists(SCORE_FILE):
        return []
    with open(SCORE_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def _write_file_scores(entries: list[dict[str, Any]]) -> None:
    with open(SCORE_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False)


def load_score_entries() -> list[dict[str, Any]]:
    try:
        if sys.platform == "emscripten":
            return _read_web_scores()
        return _read_file_scores()
    except Exception:
        return []


def save_score_entry(entry: dict[str, Any]) -> None:
    try:
        entries = load_score_entries()
        entries.append(entry)
        if sys.platform == "emscripten":
            _write_web_scores(entries)
        else:
            _write_file_scores(entries)
    except Exception:
        return
