from datetime import datetime, timezone
from types import SimpleNamespace
import unittest

from pyxel_rogue.rogue_online_state import (
    ONLINE_SCORE_STATE_DEFAULTS,
    ONLINE_SCORE_SYNC_PERIODS,
    advance_online_pending_sync,
    begin_online_period_score_request,
    cancel_online_sync_state,
    ensure_online_score_state,
    finish_online_pending_sync,
    online_sync_due,
    pop_ready_online_action,
    schedule_online_action_state,
)
from pyxel_rogue.rogue_scores import SCOREBOARD_PERIOD_LOCAL, SCOREBOARD_PERIOD_SEASON, SCOREBOARD_PERIOD_WEEKLY


class OnlineStateModuleTest(unittest.TestCase):
    def test_state_defaults_are_named_in_one_table(self):
        self.assertIn("online_score_cache", ONLINE_SCORE_STATE_DEFAULTS)
        self.assertIn("online_sync_post_allowed", ONLINE_SCORE_STATE_DEFAULTS)
        self.assertIn("online_pending_wait", ONLINE_SCORE_STATE_DEFAULTS)

    def test_ensure_online_score_state_fills_missing_values_without_overwriting_existing(self):
        state = SimpleNamespace(online_sync_wait=3, online_sync_result="busy")

        ensure_online_score_state(state)

        self.assertEqual(state.online_sync_wait, 3)
        self.assertEqual(state.online_sync_result, "busy")
        self.assertEqual(state.online_score_cache, {})
        self.assertEqual(state.online_score_loaded, set())
        self.assertEqual(state.online_sync_post_allowed, True)
        self.assertEqual(state.online_pending_action, "")

    def test_mutable_defaults_are_not_shared_between_states(self):
        left = SimpleNamespace()
        right = SimpleNamespace()

        ensure_online_score_state(left)
        ensure_online_score_state(right)
        left.online_score_cache["local"] = [1]
        left.online_score_loaded.add("weekly")
        left.online_sync_periods.append("season")

        self.assertEqual(right.online_score_cache, {})
        self.assertEqual(right.online_score_loaded, set())
        self.assertEqual(right.online_sync_periods, [])

    def test_online_sync_due_uses_next_sync_at_in_utc(self):
        now = datetime(2026, 5, 14, 0, 0, tzinfo=timezone.utc)

        self.assertTrue(online_sync_due({}, now))
        self.assertTrue(online_sync_due({"next_sync_at": "bad"}, now))
        self.assertTrue(online_sync_due({"next_sync_at": "2026-05-13T23:59:00Z"}, now))
        self.assertFalse(online_sync_due({"next_sync_at": "2026-05-14T00:01:00Z"}, now))
        self.assertTrue(online_sync_due({"next_sync_at": "2026-05-14T00:00:00"}, now))

    def test_begin_online_period_score_request_sets_sync_state_and_force_reload_periods(self):
        state = SimpleNamespace(online_score_loaded={SCOREBOARD_PERIOD_LOCAL, SCOREBOARD_PERIOD_WEEKLY, SCOREBOARD_PERIOD_SEASON})

        begin_online_period_score_request(state, post_allowed=False, force=True)

        self.assertEqual(ONLINE_SCORE_SYNC_PERIODS, (SCOREBOARD_PERIOD_WEEKLY, SCOREBOARD_PERIOD_SEASON))
        self.assertEqual(state.online_score_loaded, {SCOREBOARD_PERIOD_LOCAL})
        self.assertTrue(state.online_sync_pending)
        self.assertTrue(state.online_syncing)
        self.assertEqual(state.online_sync_wait, 1)
        self.assertTrue(state.online_sync_force)
        self.assertFalse(state.online_sync_post_allowed)
        self.assertEqual(state.online_sync_periods, [SCOREBOARD_PERIOD_WEEKLY, SCOREBOARD_PERIOD_SEASON])
        self.assertEqual(state.online_sync_status, "loading scoreboard...")
        self.assertEqual(state.online_sync_result, "")

    def test_advance_online_pending_sync_waits_then_marks_ready_and_finish_clears_syncing(self):
        waiting = SimpleNamespace(online_sync_pending=True, online_sync_wait=1)
        self.assertEqual(advance_online_pending_sync(waiting), "waiting")
        self.assertEqual(waiting.online_sync_wait, 0)
        self.assertTrue(waiting.online_sync_pending)

        ready = SimpleNamespace(
            online_sync_pending=True,
            online_sync_wait=0,
            online_syncing=False,
            online_sync_force=True,
            online_sync_periods=[SCOREBOARD_PERIOD_WEEKLY],
        )
        self.assertEqual(advance_online_pending_sync(ready), "ready")
        self.assertFalse(ready.online_sync_pending)
        self.assertTrue(ready.online_syncing)
        self.assertFalse(ready.online_sync_force)

        finish_online_pending_sync(ready)
        self.assertFalse(ready.online_syncing)
        self.assertEqual(ready.online_sync_periods, [])

    def test_advance_online_pending_sync_returns_idle_without_pending_state(self):
        state = SimpleNamespace(online_sync_pending=False, online_sync_wait=0)
        self.assertEqual(advance_online_pending_sync(state), "idle")

    def test_cancel_online_sync_state_clears_pending_and_restores_post_allowed(self):
        state = SimpleNamespace(
            online_sync_pending=True,
            online_syncing=True,
            online_sync_wait=2,
            online_sync_force=True,
            online_sync_post_allowed=False,
            online_sync_periods=[SCOREBOARD_PERIOD_WEEKLY],
        )

        cancel_online_sync_state(state)

        self.assertFalse(state.online_sync_pending)
        self.assertFalse(state.online_syncing)
        self.assertEqual(state.online_sync_wait, 0)
        self.assertFalse(state.online_sync_force)
        self.assertTrue(state.online_sync_post_allowed)
        self.assertEqual(state.online_sync_periods, [])

    def test_scheduled_online_action_waits_then_returns_ready_action_once(self):
        state = SimpleNamespace()

        schedule_online_action_state(state, "check_user", wait=1)
        self.assertEqual(state.online_pending_action, "check_user")
        self.assertEqual(state.online_pending_wait, 1)
        self.assertEqual(pop_ready_online_action(state), "waiting")
        self.assertEqual(state.online_pending_wait, 0)
        self.assertEqual(state.online_pending_action, "check_user")
        self.assertEqual(pop_ready_online_action(state), "check_user")
        self.assertEqual(state.online_pending_action, "")
        self.assertEqual(pop_ready_online_action(state), "")


if __name__ == "__main__":
    unittest.main()
