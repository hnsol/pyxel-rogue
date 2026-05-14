"""Online scoreboard UI state defaults."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone

from pyxel_rogue.rogue_scores import SCOREBOARD_PERIOD_SEASON, SCOREBOARD_PERIOD_WEEKLY, normalize_online_profile

ONLINE_SCORE_SYNC_PERIODS = (SCOREBOARD_PERIOD_WEEKLY, SCOREBOARD_PERIOD_SEASON)

ONLINE_SCORE_STATE_DEFAULTS = {
    "online_score_cache": {},
    "online_score_loaded": set(),
    "online_rank_cache": {},
    "online_sync_pending": False,
    "online_syncing": False,
    "online_sync_wait": 0,
    "online_sync_force": False,
    "online_sync_post_allowed": True,
    "online_sync_periods": [],
    "online_sync_status": "",
    "online_sync_result": "",
    "online_score_load_result": "",
    "online_register_prompt": False,
    "online_pending_action": "",
    "online_pending_wait": 0,
}


def ensure_online_score_state(target):
    for name, default in ONLINE_SCORE_STATE_DEFAULTS.items():
        if not hasattr(target, name):
            setattr(target, name, deepcopy(default))


def online_sync_due(profile, now=None):
    next_sync = str(normalize_online_profile(profile).get("next_sync_at", ""))
    if not next_sync:
        return True
    try:
        due = datetime.fromisoformat(next_sync.replace("Z", "+00:00"))
    except ValueError:
        return True
    if due.tzinfo is None:
        due = due.replace(tzinfo=timezone.utc)
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return current.astimezone(timezone.utc) >= due.astimezone(timezone.utc)


def begin_online_period_score_request(target, post_allowed=True, force=False):
    ensure_online_score_state(target)
    periods = list(ONLINE_SCORE_SYNC_PERIODS)
    if force:
        target.online_score_loaded.difference_update(periods)
    target.online_sync_post_allowed = bool(post_allowed)
    target.online_sync_pending = True
    target.online_syncing = True
    target.online_sync_wait = 1
    target.online_sync_force = bool(force)
    target.online_sync_periods = periods
    target.online_sync_status = "loading scoreboard..."
    target.online_sync_result = ""
    return True


def advance_online_pending_sync(target):
    ensure_online_score_state(target)
    if not target.online_sync_pending:
        return "idle"
    if target.online_sync_wait > 0:
        target.online_sync_wait -= 1
        return "waiting"
    target.online_sync_pending = False
    target.online_syncing = True
    target.online_sync_force = False
    return "ready"


def finish_online_pending_sync(target):
    ensure_online_score_state(target)
    target.online_sync_periods = []
    target.online_syncing = False


def cancel_online_sync_state(target):
    ensure_online_score_state(target)
    target.online_sync_pending = False
    target.online_syncing = False
    target.online_sync_wait = 0
    target.online_sync_force = False
    target.online_sync_post_allowed = True
    target.online_sync_periods = []


def schedule_online_action_state(target, action, wait=0):
    ensure_online_score_state(target)
    target.online_pending_action = action
    target.online_pending_wait = int(wait)


def pop_ready_online_action(target):
    ensure_online_score_state(target)
    action = getattr(target, "online_pending_action", "")
    if not action:
        return ""
    if getattr(target, "online_pending_wait", 0) > 0:
        target.online_pending_wait -= 1
        return "waiting"
    target.online_pending_action = ""
    return action
