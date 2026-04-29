from __future__ import annotations

import json
import os
import random
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any


SCORE_STORAGE_KEY = "pyxel-rogue-scores-v1"
PLAYER_NAME_STORAGE_KEY = "pyxel-rogue-player-name-v1"
SCORE_FILE = os.environ.get(
    "PYXEL_ROGUE_SCORE_FILE",
    os.path.join(os.path.expanduser("~"), ".pyxel_rogue_scores_v1.json"),
)
PLAYER_NAME_FILE = os.environ.get(
    "PYXEL_ROGUE_NAME_FILE",
    os.path.join(os.path.expanduser("~"), ".pyxel_rogue_name_v1.json"),
)
ONLINE_SCORE_URL = os.environ.get("PYXEL_ROGUE_SCORE_URL", "")
SCOREBOARD_PERIOD_WEEKLY = "weekly"
SCOREBOARD_PERIOD_SEASON = "season"
SCOREBOARD_PERIODS = (SCOREBOARD_PERIOD_WEEKLY, SCOREBOARD_PERIOD_SEASON)
DUMMY_PLAYER_NAMES = [
    "ACE", "NOVA", "RIN", "KAI", "MIO", "LUNA", "SAGE", "ZERO", "NIX", "REI",
    "JIN", "TOMO", "YUKI", "HAL", "ROOK", "MINT", "ECHO", "BYTE", "DOT", "ASH",
    "RUNE", "KITE", "NERO", "ARIA", "LYNX", "VOLT", "ONYX", "MICA", "SORA", "NOA",
    "ZED", "IVY", "REX", "SOL", "NIA", "KUMA", "MIKA", "YURI", "AKI", "MAO",
    "HANA", "RAY", "KIR", "NEMO", "PICO", "LOOP", "BETA", "GAMMA", "DELTA", "SIGMA",
    "TAU", "ORCA", "MARS", "VENUS", "PLUTO", "COMET", "NIM", "FINN", "FAY", "LEO",
    "MAY", "NOEL", "OTTO", "PAX", "QUIN", "RIO", "SKY", "TEO", "UMA", "VAN",
    "WREN", "XAN", "YALE", "ZARA", "BOLT", "CROW", "DUSK", "EMBER", "FLUX", "GLEN",
    "HAZE", "ION", "JADE", "KNOX", "LUX", "MOON", "NEON", "OPAL", "PEARL", "QUEST",
    "RIFT", "SPAR", "TIDE", "ULAN", "VALE", "WAVE", "XENO", "YON", "ZINC", "ATLAS",
]


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


def _parse_timestamp(timestamp: str) -> datetime:
    text = str(timestamp or "").replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        dt = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def season_for_month(month: int) -> str:
    if 3 <= month <= 5:
        return "Spring"
    if 6 <= month <= 8:
        return "Summer"
    if 9 <= month <= 11:
        return "Fall"
    return "Winter"


def score_period_keys(timestamp: str | None = None) -> dict[str, str]:
    dt = _parse_timestamp(timestamp or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    iso = dt.isocalendar()
    season_year = dt.year + 1 if dt.month == 12 else dt.year
    return {
        "period_day": dt.strftime("%Y-%m-%d"),
        "period_week": f"{iso.year}-W{iso.week:02d}",
        "period_season": f"{season_year}-{season_for_month(dt.month)}",
    }


def with_score_periods(entry: dict[str, Any]) -> dict[str, Any]:
    out = dict(entry)
    keys = score_period_keys(str(out.get("timestamp", "")))
    out.setdefault("period_day", keys["period_day"])
    out.setdefault("period_week", keys["period_week"])
    out.setdefault("period_season", keys["period_season"])
    return out


def get_top_scores(entries: list[dict[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
    return sorted(entries, key=lambda entry: int(entry.get("score", 0)), reverse=True)[:limit]


def _period_field(period: str) -> str:
    return "period_season" if period == SCOREBOARD_PERIOD_SEASON else "period_week"


def get_period_scores(entries: list[dict[str, Any]], period: str, key: str, limit: int = 10) -> list[dict[str, Any]]:
    field = _period_field(period)
    best: dict[str, dict[str, Any]] = {}
    for raw in entries:
        entry = with_score_periods(raw)
        if str(entry.get(field, "")) != str(key):
            continue
        name = str(entry.get("player_name", "ROGUE")).strip().upper()[:8] or "ROGUE"
        score = int(entry.get("score", 0))
        old = best.get(name)
        if old is None or score > int(old.get("score", 0)):
            copy = dict(entry)
            copy["player_name"] = name
            best[name] = copy
    return get_top_scores(list(best.values()), limit=limit)


def build_dummy_score_rows(timestamp: str, count: int = 24, seed: int | None = None) -> list[dict[str, Any]]:
    rng = random.Random(seed if seed is not None else timestamp)
    names = DUMMY_PLAYER_NAMES[:]
    rng.shuffle(names)
    keys = score_period_keys(timestamp)
    rows = []
    for i, name in enumerate(names[:max(0, count)]):
        score = rng.randint(40, 850) + rng.randint(0, 450) + (i % 7) * 13
        rows.append(
            {
                "timestamp": timestamp,
                **keys,
                "player_name": name,
                "score": score,
                "depth": rng.randint(1, 13),
                "result_flags": "killed",
                "killer": rng.choice(["bat", "orc", "hobgoblin", "snake", "kestrel", "centaur"]),
                "client_build": "dummy",
                "is_dummy": True,
            }
        )
    return rows


def sync_missing_local_best(
    local_entries: list[dict[str, Any]],
    online_entries: list[dict[str, Any]],
    period: str,
    key: str,
    post_entry,
) -> bool:
    local = get_period_scores(local_entries, period, key, limit=1)
    if not local:
        return False
    online = get_period_scores(online_entries, period, key, limit=10)
    best = local[0]
    name = str(best.get("player_name", "")).upper()
    online_score = max((int(e.get("score", 0)) for e in online if str(e.get("player_name", "")).upper() == name), default=-1)
    if int(best.get("score", 0)) <= online_score:
        return False
    post_entry(best)
    return True


def score_reason(result_flags: str) -> str:
    # Rogue 5.4.4 rip.c:score() reason[] table.
    return {
        "killed": "killed",
        "quit": "quit",
        "winner": "A total winner",
        "killed_with_amulet": "killed with Amulet",
    }.get(str(result_flags), str(result_flags))


def article_for(name: str) -> str:
    if not name:
        return ""
    return "an" if name[0].lower() in "aeiou" else "a"


def format_score_line(rank: int, entry: dict[str, Any]) -> str:
    score = int(entry.get("score", 0))
    name = str(entry.get("player_name", "rogue"))
    flags = str(entry.get("result_flags", ""))
    level = int(entry.get("level", 0))
    line = f"{rank:2d} {score:5d} {name}: {score_reason(flags)} on level {level}"
    if flags in ("killed", "killed_with_amulet"):
        killer = str(entry.get("killer", "")).strip()
        if killer:
            line += f" by {article_for(killer)} {killer}"
    return line + "."


def format_top_score_lines(entries: list[dict[str, Any]], limit: int = 10) -> list[str]:
    lines = ["Top Ten Scores:", "   Score Name"]
    lines.extend(format_score_line(i, entry) for i, entry in enumerate(entries[:limit], start=1))
    return lines


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


def sanitize_player_name(name: str) -> str:
    out = "".join(ch for ch in str(name).upper() if ch == " " or ch.isalnum())[:8].strip()
    return out or "ROGUE"


def load_player_name(default: str = "ROGUE") -> str:
    try:
        if sys.platform == "emscripten":
            from js import localStorage

            return sanitize_player_name(localStorage.getItem(PLAYER_NAME_STORAGE_KEY) or default)
        if os.path.exists(PLAYER_NAME_FILE):
            with open(PLAYER_NAME_FILE, encoding="utf-8") as f:
                data = json.load(f)
            return sanitize_player_name(data.get("player_name", default))
    except Exception:
        pass
    return sanitize_player_name(default)


def save_player_name(name: str) -> str:
    clean = sanitize_player_name(name)
    try:
        if sys.platform == "emscripten":
            from js import localStorage

            localStorage.setItem(PLAYER_NAME_STORAGE_KEY, clean)
        else:
            with open(PLAYER_NAME_FILE, "w", encoding="utf-8") as f:
                json.dump({"player_name": clean}, f, ensure_ascii=False)
    except Exception:
        pass
    return clean


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
        entries.append(with_score_periods(entry))
        if sys.platform == "emscripten":
            _write_web_scores(entries)
        else:
            _write_file_scores(entries)
    except Exception:
        return


def _http_json(url: str, payload: dict[str, Any] | None = None) -> Any:
    if sys.platform == "emscripten":
        from js import XMLHttpRequest

        xhr = XMLHttpRequest.new()
        method = "POST" if payload is not None else "GET"
        xhr.open(method, url, False)
        xhr.setRequestHeader("Content-Type", "application/json")
        xhr.send(json.dumps(payload) if payload is not None else None)
        if int(xhr.status) >= 400:
            raise RuntimeError(f"HTTP {xhr.status}")
        return json.loads(str(xhr.responseText or "[]"))
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=4) as res:
        return json.loads(res.read().decode("utf-8"))


def submit_online_score(entry: dict[str, Any], url: str | None = None) -> bool:
    target = url if url is not None else ONLINE_SCORE_URL
    if not target:
        return False
    try:
        _http_json(target, {"action": "submit", "entry": with_score_periods(entry)})
        return True
    except Exception:
        return False


def fetch_online_scores(period: str, url: str | None = None, timestamp: str | None = None) -> list[dict[str, Any]]:
    target = url if url is not None else ONLINE_SCORE_URL
    if not target:
        return []
    key = score_period_keys(timestamp).get(_period_field(period), "")
    try:
        sep = "&" if "?" in target else "?"
        query = urllib.parse.urlencode({"period": period, "key": key})
        data = _http_json(target + sep + query)
        if isinstance(data, dict):
            data = data.get("scores", [])
        return data if isinstance(data, list) else []
    except Exception:
        return []
