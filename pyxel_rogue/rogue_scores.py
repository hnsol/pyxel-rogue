from __future__ import annotations

import json
import base64
import hashlib
import os
import random
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

from pyxel_rogue.rogue_difficulty import DEFAULT_DIFFICULTY, normalize as normalize_difficulty

SCORE_STORAGE_KEY = "pyxel-rogue-scores-v2"
PLAYER_NAME_STORAGE_KEY = "pyxel-rogue-player-name-v2"
ONLINE_PROFILE_STORAGE_KEY = "pyxel-rogue-online-profile-v3"
ONLINE_SCORE_CACHE_STORAGE_KEY = "pyxel-rogue-online-score-cache-v1"
SCORE_FILE = os.environ.get(
    "PYXEL_ROGUE_SCORE_FILE",
    os.path.join(os.path.expanduser("~"), ".pyxel_rogue_scores_v2.json"),
)
PLAYER_NAME_FILE = os.environ.get(
    "PYXEL_ROGUE_NAME_FILE",
    os.path.join(os.path.expanduser("~"), ".pyxel_rogue_name_v2.json"),
)
ONLINE_PROFILE_FILE = os.environ.get(
    "PYXEL_ROGUE_ONLINE_PROFILE_FILE",
    os.path.join(os.path.expanduser("~"), ".pyxel_rogue_online_profile_v3.json"),
)
ONLINE_SCORE_CACHE_FILE = os.environ.get(
    "PYXEL_ROGUE_ONLINE_SCORE_CACHE_FILE",
    os.path.join(os.path.expanduser("~"), ".pyxel_rogue_online_score_cache_v1.json"),
)
DEFAULT_ONLINE_SCORE_URL = ""
ONLINE_SCORE_URL = os.environ.get("PYXEL_ROGUE_SCORE_URL", DEFAULT_ONLINE_SCORE_URL)
ONLINE_HTTP_TIMEOUT_SECONDS = 15
SCOREBOARD_PERIOD_LOCAL = "local"
SCOREBOARD_PERIOD_WEEKLY = "weekly"
SCOREBOARD_PERIOD_SEASON = "season"
SCOREBOARD_PERIODS = (SCOREBOARD_PERIOD_LOCAL, SCOREBOARD_PERIOD_WEEKLY, SCOREBOARD_PERIOD_SEASON)
USER_NAME_MAX = 8
DUMMY_PLAYER_NAMES = [
    "RODNEY", "YENDOR", "WIZRODNY", "AMULETYN", "HJKLUSER",
    "LEVEL26", "CHMOD777", "DEADBEEF", "SIGSEGV", "NULLPTR",
    "ROOT", "SUDO", "BINSH", "DEVNULL", "TARBALL",
    "PDP11", "VAX1178", "VT100", "BSD43", "V7UNIX",
    "KENTOMP", "DMR", "BJOY", "WICHMAN", "KENARNLD",
    "KESTREL", "GRIFFON", "JABBERWK", "DRAGON", "GRIDBUG",
    "RNGGOD", "RNGHATER", "PERMADTH", "FOODLESS", "SPEEDRUN",
    "SAVE_SC", "LVL26F", "RIPPER", "RETRY", "GAMEOVER",
    "MALLOC", "FREE", "STACKOVF", "BITSHIFT", "XOR",
    "GOTO10", "EXIT0", "STDOUT", "STDIN", "STDERR",
    "ASCII", "HEXDUMP", "BINARY", "BYTE", "OPCODE",
    "TTY0", "ANSI80", "CRLF", "EOF", "SOF",
    "PYXELDEV", "8BITLUV", "PIXELART", "SPRITE", "PALETTE",
    "X86", "Z80A", "6502", "MOTOROLA", "C64",
    "PASCAL", "FORTRAN", "COBOL", "ALGOL", "B_LANG",
    "LOBOLTO", "UMORIA", "NETHACK", "ANGBAND", "DUNGEON",
    "XYZZY", "PLUGH", "FROB", "FOOBAR", "BAZQUX",
    "STR0", "CHAR1", "VOID", "CONST", "STATIC",
    "VOLATILE", "REGISTER", "STRUCT", "UNION", "TYPEDEF",
    "MAXINT", "MININT", "ID001", "USER99", "GUEST",
]
RESERVED_USER_IDS = {"guest", "rogue54"} | {name.lower() for name in DUMMY_PLAYER_NAMES}


def score_entry_id(entry: dict[str, Any]) -> str:
    fields = (
        str(entry.get("timestamp", "")),
        sanitize_player_name(str(entry.get("player_name", "ROGUE"))),
        str(int(entry.get("score", 0))),
        str(int(entry.get("level", entry.get("depth", 0)) or 0)),
        str(entry.get("result_flags", "")),
        str(entry.get("killer", "")),
        normalize_difficulty(str(entry.get("difficulty", DEFAULT_DIFFICULTY))),
    )
    return hashlib.sha1("|".join(fields).encode("utf-8")).hexdigest()[:16]


def score_value(gold: int, result_flags: str) -> int:
    gold = max(0, int(gold))
    if result_flags in ("killed", "killed_with_amulet"):
        return gold * 9 // 10
    return gold


def total_winner_item_worth(item: dict[str, Any]) -> int:
    """Rogue 5.4.4 rip.c:total_winner() pack item worth calculation."""
    cat = item.get("cat")
    qty = int(item.get("qty", 1) or 1)
    worth = 0
    if cat == "food":
        worth = 2 * qty
    elif cat == "wpn":
        worth = int(item.get("base_worth", 0))
        worth *= 3 * (int(item.get("hit_plus", 0)) + int(item.get("dam_plus", 0))) + qty
    elif cat == "arm":
        base_ac = int(item.get("base_ac", 10))
        current_ac = base_ac - int(item.get("ench", 0))
        worth = int(item.get("base_worth", 0))
        worth += (9 - current_ac) * 100
        worth += 10 * (base_ac - current_ac)
    elif cat in ("scr", "pot"):
        worth = int(item.get("base_worth", 0)) * qty
        if not item.get("type_known", False):
            worth //= 2
    elif cat == "ring":
        worth = int(item.get("base_worth", 0))
        if item.get("name") in {"add strength", "increase damage", "protection", "dexterity"}:
            ench = int(item.get("ench", 0))
            worth = worth + ench * 100 if ench > 0 else 10
        if not item.get("known", False):
            worth //= 2
    elif cat == "stick":
        worth = int(item.get("base_worth", 0)) + 20 * int(item.get("charges", 0))
        if not item.get("known", False):
            worth //= 2
    elif cat == "amulet":
        worth = 1000
    return max(0, worth)


def total_winner_score(gold: int, items: list[dict[str, Any]]) -> int:
    """Rogue 5.4.4 rip.c:total_winner() adds sold pack worth to purse."""
    return max(0, int(gold)) + sum(total_winner_item_worth(item) for item in items)


def build_score_entry(
    *,
    score: int = 0,
    result_flags: str,
    level: int,
    killer: str,
    player_name: str,
    timestamp: str,
    gold: int,
    difficulty: str = DEFAULT_DIFFICULTY,
    variant: str | None = None,
) -> dict[str, Any]:
    entry = {
        "score": int(score) if score else score_value(gold, result_flags),
        "result_flags": result_flags,
        "level": int(level),
        "killer": str(killer),
        "player_name": str(player_name),
        "timestamp": str(timestamp),
        "difficulty": normalize_difficulty(difficulty),
    }
    if variant:
        entry["variant"] = str(variant)
    entry["score_id"] = score_entry_id(entry)
    return entry


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
    out["difficulty"] = normalize_difficulty(str(out.get("difficulty", DEFAULT_DIFFICULTY)))
    out.setdefault("score_id", score_entry_id(out))
    return out


def get_top_scores(entries: list[dict[str, Any]], limit: int = 10, difficulty: str | None = None) -> list[dict[str, Any]]:
    if difficulty is not None:
        diff = normalize_difficulty(difficulty)
        entries = [entry for entry in entries if normalize_difficulty(str(entry.get("difficulty", DEFAULT_DIFFICULTY))) == diff]
    return sorted(entries, key=lambda entry: int(entry.get("score", 0)), reverse=True)[:limit]


def _period_field(period: str) -> str:
    return "period_season" if period == SCOREBOARD_PERIOD_SEASON else "period_week"


def get_period_scores(entries: list[dict[str, Any]], period: str, key: str, limit: int = 10, difficulty: str | None = None) -> list[dict[str, Any]]:
    if period == SCOREBOARD_PERIOD_LOCAL or period not in (SCOREBOARD_PERIOD_WEEKLY, SCOREBOARD_PERIOD_SEASON):
        return []
    field = _period_field(period)
    best: dict[str, dict[str, Any]] = {}
    for raw in entries:
        entry = with_score_periods(raw)
        if difficulty is not None and entry["difficulty"] != normalize_difficulty(difficulty):
            continue
        if str(entry.get(field, "")) != str(key):
            continue
        name = str(entry.get("player_name", "rogue54")).strip()[:16] or "rogue54"
        name_key = name.upper()
        score = int(entry.get("score", 0))
        old = best.get(name_key)
        if old is None or score > int(old.get("score", 0)):
            copy = dict(entry)
            copy["player_name"] = name
            best[name_key] = copy
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
    best_id = str(best.get("score_id", ""))
    if best_id and any(str(entry.get("score_id", "")) == best_id for entry in online_entries):
        return False
    name = str(best.get("player_name", "")).upper()
    online_score = max((int(e.get("score", 0)) for e in online if str(e.get("player_name", "")).upper() == name), default=-1)
    if int(best.get("score", 0)) <= online_score:
        return False
    post_entry(best)
    return True


def local_best_sync_entries(
    entries: list[dict[str, Any]],
    timestamp: str | None = None,
    player_name: str | None = None,
) -> list[dict[str, Any]]:
    keys = score_period_keys(timestamp)
    if player_name is not None:
        name_key = str(player_name).lower()
        entries = [
            entry for entry in entries
            if str(entry.get("player_name", "")).lower() == name_key
        ]
    out = []
    seen_ids = set()
    for period, key in (
        (SCOREBOARD_PERIOD_WEEKLY, keys["period_week"]),
        (SCOREBOARD_PERIOD_SEASON, keys["period_season"]),
    ):
        best = get_period_scores(entries, period, key, limit=1)
        if not best:
            continue
        entry = with_score_periods(best[0])
        entry_id = str(entry.get("score_id", ""))
        if entry_id and entry_id in seen_ids:
            continue
        seen_ids.add(entry_id)
        out.append(entry)
    return out


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
    # Rogue 5.4.4 rip.c:killname() marks these deaths as no-article.
    if name in ("hypothermia", "starvation"):
        return ""
    return "an" if name[0].lower() in "aeiou" else "a"


def format_score_line(rank: int, entry: dict[str, Any]) -> str:
    score = int(entry.get("score", 0))
    name = str(entry.get("player_name", "rogue"))
    flags = str(entry.get("result_flags", ""))
    level = int(entry.get("level", entry.get("depth", 0)) or 0)
    line = f"{rank:2d} {score:5d} {name}: {score_reason(flags)} on level {level}"
    if flags in ("killed", "killed_with_amulet"):
        killer = str(entry.get("killer", "")).strip()
        if killer:
            article = article_for(killer)
            line += f" by {article + ' ' if article else ''}{killer}"
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
    out = "".join(ch for ch in str(name).lower() if "a" <= ch <= "z" or "0" <= ch <= "9")[:USER_NAME_MAX]
    return out or "rogue54"


def sanitize_user_id(user_id: str) -> str:
    out = "".join(ch for ch in str(user_id).lower() if "a" <= ch <= "z" or "0" <= ch <= "9")[:USER_NAME_MAX]
    return out or "rogue54"


def can_register_user_id(user_id: str) -> bool:
    return sanitize_user_id(user_id) not in RESERVED_USER_IDS


def validate_user_password(user_password: str) -> str:
    text = str(user_password)
    if len(text) != 6 or not text.isdigit():
        raise ValueError("user password must be 6 digits")
    return text


def display_score_name(entry: dict[str, Any], local_only: bool | None = None) -> str:
    profile = normalize_online_profile(entry)
    return profile["user_name"]


def _token_key(user_name: str) -> bytes:
    return hashlib.sha256(("pyxel-rogue:" + sanitize_user_id(user_name)).encode("utf-8")).digest()


def obfuscate_server_token(server_token: str, user_name: str) -> str:
    raw = str(server_token).encode("utf-8")
    key = _token_key(user_name)
    masked = bytes(b ^ key[i % len(key)] for i, b in enumerate(raw))
    return base64.urlsafe_b64encode(masked).decode("ascii")


def deobfuscate_server_token(encoded_token: str, user_name: str) -> str:
    try:
        raw = base64.urlsafe_b64decode(str(encoded_token).encode("ascii"))
        key = _token_key(user_name)
        return bytes(b ^ key[i % len(key)] for i, b in enumerate(raw)).decode("utf-8")
    except Exception:
        return ""


def normalize_online_profile(profile: dict[str, Any] | None) -> dict[str, Any]:
    profile = dict(profile or {})
    has_v3_name = "user_name" in profile
    user_name = sanitize_user_id(profile.get("user_name", "guest")) if has_v3_name else "guest"
    token = str(profile.get("server_token", "")) if has_v3_name else ""
    if not token and profile.get("server_token_obf"):
        token = deobfuscate_server_token(str(profile.get("server_token_obf", "")), user_name)
    local_only = True if not token else bool(profile.get("local_only", False))
    return {
        "user_name": user_name,
        "local_only": local_only,
        "server_token": token,
        "last_sync_at": str(profile.get("last_sync_at", "")),
        "next_sync_at": str(profile.get("next_sync_at", "")),
        "profile_exists": bool(profile.get("profile_exists", has_v3_name)),
    }


def load_online_profile() -> dict[str, Any]:
    try:
        if sys.platform == "emscripten":
            from js import localStorage

            raw = localStorage.getItem(ONLINE_PROFILE_STORAGE_KEY)
            return normalize_online_profile(json.loads(str(raw))) if raw else normalize_online_profile(None)
        if os.path.exists(ONLINE_PROFILE_FILE):
            with open(ONLINE_PROFILE_FILE, encoding="utf-8") as f:
                return normalize_online_profile(json.load(f))
    except Exception:
        pass
    return normalize_online_profile(None)


def save_online_profile(profile: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_online_profile(profile)
    normalized["profile_exists"] = True
    stored = dict(normalized)
    token = stored.pop("server_token", "")
    stored["server_token_obf"] = obfuscate_server_token(token, normalized["user_name"]) if token else ""
    try:
        if sys.platform == "emscripten":
            from js import localStorage

            localStorage.setItem(ONLINE_PROFILE_STORAGE_KEY, json.dumps(stored, ensure_ascii=False))
        else:
            with open(ONLINE_PROFILE_FILE, "w", encoding="utf-8") as f:
                json.dump(stored, f, ensure_ascii=False)
    except Exception:
        pass
    return normalized


def save_local_only_profile(user_id: str, display_name: str | None = None) -> dict[str, Any]:
    clean_id = sanitize_user_id(user_id)
    return save_online_profile({
        "user_name": clean_id,
        "local_only": True,
        "profile_exists": True,
    })


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


def _read_online_score_cache() -> dict[str, Any]:
    try:
        if sys.platform == "emscripten":
            from js import localStorage

            raw = localStorage.getItem(ONLINE_SCORE_CACHE_STORAGE_KEY)
            data = json.loads(str(raw)) if raw else {}
        elif os.path.exists(ONLINE_SCORE_CACHE_FILE):
            with open(ONLINE_SCORE_CACHE_FILE, encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write_online_score_cache(data: dict[str, Any]) -> None:
    try:
        if sys.platform == "emscripten":
            from js import localStorage

            localStorage.setItem(ONLINE_SCORE_CACHE_STORAGE_KEY, json.dumps(data, ensure_ascii=False))
        else:
            with open(ONLINE_SCORE_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
    except Exception:
        return


def load_online_score_cache(period: str, key: str) -> list[dict[str, Any]]:
    if period not in (SCOREBOARD_PERIOD_WEEKLY, SCOREBOARD_PERIOD_SEASON):
        return []
    record = _read_online_score_cache().get(period, {})
    if not isinstance(record, dict) or str(record.get("key", "")) != str(key):
        return []
    scores = record.get("scores", [])
    return scores if isinstance(scores, list) else []


def save_online_score_cache(period: str, key: str, scores: list[dict[str, Any]]) -> None:
    if period not in (SCOREBOARD_PERIOD_WEEKLY, SCOREBOARD_PERIOD_SEASON):
        return
    data = _read_online_score_cache()
    data[period] = {
        "key": str(key),
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "scores": [with_score_periods(score) for score in scores[:10]],
    }
    _write_online_score_cache(data)


def _http_json(url: str, payload: dict[str, Any] | None = None) -> Any:
    if sys.platform == "emscripten":
        from js import XMLHttpRequest

        xhr = XMLHttpRequest.new()
        method = "POST" if payload is not None else "GET"
        xhr.open(method, url, False)
        if payload is not None:
            xhr.setRequestHeader("Content-Type", "text/plain;charset=utf-8")
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
    with urllib.request.urlopen(req, timeout=ONLINE_HTTP_TIMEOUT_SECONDS) as res:
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


def register_online_user(
    user_name: str,
    user_password: str,
    url: str | None = None,
    variant: str | None = None,
) -> dict[str, Any]:
    clean_id = sanitize_user_id(user_name)
    if not can_register_user_id(clean_id):
        return {"ok": False, "status": "reserved"}
    payload = {
        "action": "registerUser",
        "user_name": clean_id,
        "user_password": validate_user_password(user_password),
    }
    if variant:
        payload["variant"] = str(variant)
    try:
        data = _http_json(url if url is not None else ONLINE_SCORE_URL, payload)
        return data if isinstance(data, dict) else {"ok": False, "status": "failed"}
    except Exception:
        return {"ok": False, "status": "failed"}


def link_online_user(
    user_name: str,
    user_password: str,
    url: str | None = None,
    variant: str | None = None,
) -> dict[str, Any]:
    clean_id = sanitize_user_id(user_name)
    payload = {
        "action": "linkUser",
        "user_name": clean_id,
        "user_password": validate_user_password(user_password),
    }
    if variant:
        payload["variant"] = str(variant)
    try:
        data = _http_json(url if url is not None else ONLINE_SCORE_URL, payload)
        return data if isinstance(data, dict) else {"ok": False, "status": "failed"}
    except Exception:
        return {"ok": False, "status": "failed"}


def check_online_user(user_name: str, url: str | None = None, variant: str | None = None) -> dict[str, Any]:
    clean = sanitize_user_id(user_name)
    payload = {"action": "checkUser", "user_name": clean}
    if variant:
        payload["variant"] = str(variant)
    try:
        data = _http_json(url if url is not None else ONLINE_SCORE_URL, payload)
        return data if isinstance(data, dict) else {"ok": False, "status": "failed", "exists": False}
    except Exception:
        return {"ok": False, "status": "failed", "exists": False}


def sync_online_scoreboard(
    profile: dict[str, Any],
    entries: list[dict[str, Any]],
    url: str | None = None,
    variant: str | None = None,
) -> dict[str, Any]:
    clean = normalize_online_profile(profile)
    if clean["local_only"] or not clean["server_token"]:
        return {"ok": False, "status": "auth_failed", "scores": {}}
    payload = {
        "action": "syncScoreboard",
        "user_name": clean["user_name"],
        "server_token": clean["server_token"],
        "entries": [with_score_periods(entry) for entry in entries],
        "periods": [SCOREBOARD_PERIOD_WEEKLY, SCOREBOARD_PERIOD_SEASON],
    }
    if variant:
        payload["variant"] = str(variant)
    try:
        data = _http_json(url if url is not None else ONLINE_SCORE_URL, payload)
        return data if isinstance(data, dict) else {"ok": False, "status": "failed", "scores": {}}
    except Exception:
        return {"ok": False, "status": "failed", "scores": {}}


def record_guest_scoreboard_sync(url: str | None = None, variant: str | None = None) -> bool:
    target = url if url is not None else ONLINE_SCORE_URL
    if not target:
        return False
    try:
        payload = {"action": "guestScoreboardSync"}
        if variant:
            payload["variant"] = str(variant)
        data = _http_json(target, payload)
        return bool(isinstance(data, dict) and data.get("ok"))
    except Exception:
        return False


def seed_dummy_online_scores(url: str | None = None, variant: str | None = None) -> bool:
    target = url if url is not None else ONLINE_SCORE_URL
    if not target:
        return False
    try:
        sep = "&" if "?" in target else "?"
        query = {"action": "seedDummy"}
        if variant:
            query["variant"] = str(variant)
        _http_json(target + sep + urllib.parse.urlencode(query))
        return True
    except Exception:
        return False


def fetch_online_scores(
    period: str,
    url: str | None = None,
    timestamp: str | None = None,
    variant: str | None = None,
) -> list[dict[str, Any]] | None:
    if period == SCOREBOARD_PERIOD_LOCAL or period not in (SCOREBOARD_PERIOD_WEEKLY, SCOREBOARD_PERIOD_SEASON):
        return []
    target = url if url is not None else ONLINE_SCORE_URL
    if not target:
        return None
    key = score_period_keys(timestamp).get(_period_field(period), "")
    try:
        sep = "&" if "?" in target else "?"
        params = {"period": period, "key": key}
        if variant:
            params["variant"] = str(variant)
        query = urllib.parse.urlencode(params)
        data = _http_json(target + sep + query)
        if isinstance(data, dict):
            data = data.get("scores", [])
        return data if isinstance(data, list) else []
    except Exception:
        return None
