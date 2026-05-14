"""Online scoreboard period and sync display helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from pyxel_rogue.rogue_lang import LANG_JA
from pyxel_rogue.rogue_online_text import online_text
from pyxel_rogue.rogue_scores import (
    SCOREBOARD_PERIOD_LOCAL,
    SCOREBOARD_PERIOD_SEASON,
    SCOREBOARD_PERIOD_WEEKLY,
    format_score_line,
    score_period_keys,
)
from pyxel_rogue.rogue_text import TextCatalog
from pyxel_rogue.rogue_variant import score_entry_is_nyandor


SCOREBOARD_PERIOD_ORDER = (SCOREBOARD_PERIOD_LOCAL, SCOREBOARD_PERIOD_WEEKLY, SCOREBOARD_PERIOD_SEASON)
SYNC_COOLDOWN_HOURS = 1


@dataclass(frozen=True)
class ScoreboardEntryRow:
    line: str
    highlight: bool = False


def scoreboard_period_key(period, timestamp=None):
    if period == SCOREBOARD_PERIOD_LOCAL:
        return ""
    keys = score_period_keys(timestamp)
    if period == SCOREBOARD_PERIOD_SEASON:
        return keys["period_season"]
    return keys["period_week"]


def cycle_scoreboard_period(current, delta, periods=SCOREBOARD_PERIOD_ORDER):
    try:
        index = periods.index(current)
    except ValueError:
        index = 0
    return periods[(index + delta) % len(periods)]


def scoreboard_period_label(period, lang, timestamp=None):
    if period == SCOREBOARD_PERIOD_LOCAL:
        return online_text(lang, "score_period_local")
    return scoreboard_period_key(period, timestamp)


def score_period_tab_label(period, lang):
    return {
        SCOREBOARD_PERIOD_LOCAL: online_text(lang, "score_period_local"),
        SCOREBOARD_PERIOD_WEEKLY: online_text(lang, "score_tab_weekly"),
        SCOREBOARD_PERIOD_SEASON: online_text(lang, "score_tab_season"),
    }.get(period, scoreboard_period_label(period, lang))


def scoreboard_title(period, lang):
    return {
        SCOREBOARD_PERIOD_LOCAL: online_text(lang, "score_title_local"),
        SCOREBOARD_PERIOD_WEEKLY: online_text(lang, "score_title_weekly"),
        SCOREBOARD_PERIOD_SEASON: online_text(lang, "score_title_season"),
    }.get(period, online_text(lang, "score_title_local"))


def _parse_utc(value, fallback=None):
    if value is None:
        return fallback or datetime.now(timezone.utc)
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)
    text = str(value).replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return fallback or datetime.now(timezone.utc)
    return dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def format_utc_minute(value):
    text = str(value or "")
    if not text:
        return "-"
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return text
    dt = dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    return f"UTC {dt:%Y-%m-%d %H:%M}"


def format_utc_short_minute(value):
    text = str(value or "")
    if not text:
        return "-"
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return text
    dt = dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    return f"{dt:%m-%d %H:%M}"


def sync_post_after_display(last_sync, next_sync):
    last_text = str(last_sync or "")
    next_text = str(next_sync or "")
    if not last_text or not next_text:
        return next_text
    try:
        last = datetime.fromisoformat(last_text.replace("Z", "+00:00"))
        next_dt = datetime.fromisoformat(next_text.replace("Z", "+00:00"))
    except ValueError:
        return next_text
    last = last.astimezone(timezone.utc) if last.tzinfo else last.replace(tzinfo=timezone.utc)
    next_dt = next_dt.astimezone(timezone.utc) if next_dt.tzinfo else next_dt.replace(tzinfo=timezone.utc)
    policy_next = last + timedelta(hours=SYNC_COOLDOWN_HOURS)
    return min(next_dt, policy_next).isoformat().replace("+00:00", "Z")


def scoreboard_period_end(period, now=None):
    if period == SCOREBOARD_PERIOD_LOCAL:
        return None
    dt = _parse_utc(now)
    if period == SCOREBOARD_PERIOD_WEEKLY:
        start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        return start + timedelta(days=7 - start.weekday())
    y, m = dt.year, dt.month
    if 3 <= m <= 5:
        return datetime(y, 6, 1, tzinfo=timezone.utc)
    if 6 <= m <= 8:
        return datetime(y, 9, 1, tzinfo=timezone.utc)
    if 9 <= m <= 11:
        return datetime(y, 12, 1, tzinfo=timezone.utc)
    return datetime(y + 1 if m == 12 else y, 3, 1, tzinfo=timezone.utc)


def scoreboard_period_ends_line(period, lang, now=None, local_line=""):
    if period == SCOREBOARD_PERIOD_LOCAL:
        return local_line
    dt = _parse_utc(now)
    end = scoreboard_period_end(period, dt)
    seconds = max(0, int((end - dt).total_seconds()))
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, _seconds = divmod(rem, 60)
    if period == SCOREBOARD_PERIOD_WEEKLY:
        remain = f"{days}d {hours:02d}h {minutes:02d}m"
        label = online_text(lang, "period_week")
    else:
        weeks, days = divmod(days, 7)
        remain = f"{weeks}w {days}d {hours:02d}h {minutes:02d}m"
        label = online_text(lang, "period_season")
    display_end = end - timedelta(minutes=1)
    if lang == LANG_JA:
        return f"{label}の集計終了まで {remain} / UTC {display_end:%Y-%m-%d %H:%M}"
    return f"{label} ends in {remain} at UTC {display_end:%Y-%m-%d %H:%M}"


def online_sync_hint_line(profile, lang):
    if profile.get("local_only", True):
        return online_text(lang, "local_only_hint")
    last_sync = profile.get("last_sync_at", "")
    if last_sync:
        next_sync = profile.get("next_sync_at", "")
        if next_sync:
            next_sync = sync_post_after_display(last_sync, next_sync)
            return (
                f"{online_text(lang, 'posted')} UTC {format_utc_short_minute(last_sync)}"
                f" / {online_text(lang, 'post_after')} {format_utc_short_minute(next_sync)}"
            )
        return f"{online_text(lang, 'posted')} {format_utc_minute(last_sync)}"
    return ""


def online_result_lines(message, lang, limit=27):
    text = online_text(lang, str(message or "").strip())
    if ". " in text:
        head, tail = text.split(". ", 1)
        head = f"{head}."
        if len(head) <= limit and len(tail) <= limit:
            return [head, tail]
    if "。" in text:
        head, tail = text.split("。", 1)
        head = f"{head}。"
        tail = tail.strip()
        if tail:
            tail = tail if tail.endswith("。") else f"{tail}。"
        if tail and len(head) <= limit and len(tail) <= limit:
            return [head, tail]
    words = text.split()
    if not words:
        return []
    lines = []
    i = 0
    while i < len(words) and len(lines) < 2:
        line = words[i]
        i += 1
        while i < len(words) and len(line) + 1 + len(words[i]) <= limit:
            line = f"{line} {words[i]}"
            i += 1
        lines.append(line[:limit])
    return lines[:2]


def online_sync_box_lines(post_allowed, lang):
    if bool(post_allowed):
        return [online_text(lang, "sync_scores"), online_text(lang, "please_wait")]
    return [online_text(lang, "refresh_ranking"), online_text(lang, "please_wait")]


def format_score_line_for_board(rank, entry, lang):
    row = dict(entry)
    if row.get("result_flags") == "winner" and score_entry_is_nyandor(row):
        score = int(row.get("score", 0))
        name = str(row.get("player_name", "rogue"))
        if lang == LANG_JA:
            return f"{rank:2d} {score:5d} {name}: ニャンダーのねこを連れ帰りし者"
        return f"{rank:2d} {score:5d} {name}: returned with the Nyandor cat."
    if lang == LANG_JA:
        return format_score_line_for_board_ja(rank, row)
    return format_score_line(rank, row)


def format_score_line_for_board_ja(rank, entry):
    score = int(entry.get("score", 0))
    name = str(entry.get("player_name", "rogue"))
    flags = str(entry.get("result_flags", ""))
    level = int(entry.get("level", entry.get("depth", 0)) or 0)
    if flags == "winner":
        reason = "運命の洞窟より生きて帰りたる勇者"
        return f"{rank:2d} {score:5d} {name}: {reason}"
    if flags == "quit":
        reason = f"{level}階で中断"
    elif flags == "killed_with_amulet":
        killer = score_killer_name(LANG_JA, entry.get("killer", ""))
        reason = f"アミュレット所持中、{level}階で{killer}に倒された"
    elif flags == "killed":
        killer = score_killer_name(LANG_JA, entry.get("killer", ""))
        reason = f"{level}階で{killer}に倒された"
    else:
        reason = flags
    return f"{rank:2d} {score:5d} {name}: {reason}。"


def score_killer_name(lang, killer):
    name = str(killer or "").strip()
    if not name:
        return "何者か" if lang == LANG_JA else ""
    if lang != LANG_JA:
        return name
    special = {
        "fire": "炎",
        "starvation": "飢え",
        "hypothermia": "寒さ",
    }
    if name in special:
        return special[name]
    translated = TextCatalog.monster(lang, name)
    if translated != name:
        return translated
    translated = TextCatalog.bolt(lang, name)
    return translated


def is_current_result_score(entry, current):
    if not current:
        return False
    entry_id = str(entry.get("score_id", ""))
    current_id = str(current.get("score_id", ""))
    if entry_id and current_id:
        return entry_id == current_id
    return (
        str(entry.get("timestamp", "")) == str(current.get("timestamp", ""))
        and str(entry.get("player_name", "")).upper() == str(current.get("player_name", "")).upper()
        and int(entry.get("score", 0)) == int(current.get("score", 0))
    )


def mark_current_score_line(line):
    return ">" + line[1:] if str(line).startswith(" ") else ">" + str(line)


def scoreboard_entry_rows(scores, period, lang, current_player_name="", current_entry=None, limit=10):
    player_name = str(current_player_name).upper()[:16]
    rows = []
    for rank, entry in enumerate(list(scores)[:limit], start=1):
        name = str(entry.get("player_name", "")).upper()[:16]
        current_result = (
            period == SCOREBOARD_PERIOD_LOCAL
            and bool(current_entry)
            and is_current_result_score(entry, current_entry)
        )
        highlight = current_result or (period != SCOREBOARD_PERIOD_LOCAL and name == player_name)
        line = format_score_line_for_board(rank, entry, lang)
        if current_result:
            line = mark_current_score_line(line)
        rows.append(ScoreboardEntryRow(line=line, highlight=highlight))
    return rows


def score_guest_local_best_row(entry, period, lang):
    if not entry or period not in (SCOREBOARD_PERIOD_WEEKLY, SCOREBOARD_PERIOD_SEASON):
        return None
    line = format_score_line_for_board(0, entry, lang)
    line = "--" + line[2:] if len(line) >= 2 else f"-- {line}"
    return ScoreboardEntryRow(line=line, highlight=True)
