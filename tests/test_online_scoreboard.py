from datetime import datetime, timezone
import unittest

from pyxel_rogue.rogue_lang import LANG_EN, LANG_JA
from pyxel_rogue.rogue_online_scoreboard import (
    SCOREBOARD_PERIOD_ORDER,
    cycle_scoreboard_period,
    format_utc_minute,
    format_utc_short_minute,
    format_score_line_for_board,
    is_current_result_score,
    mark_current_score_line,
    online_result_lines,
    sync_post_after_display,
    online_sync_box_lines,
    online_sync_hint_line,
    score_guest_local_best_row,
    score_killer_name,
    score_period_tab_label,
    scoreboard_entry_rows,
    scoreboard_title,
    scoreboard_period_end,
    scoreboard_period_ends_line,
    scoreboard_period_key,
    scoreboard_period_label,
)
from pyxel_rogue.rogue_scores import (
    SCOREBOARD_PERIOD_LOCAL,
    SCOREBOARD_PERIOD_SEASON,
    SCOREBOARD_PERIOD_WEEKLY,
)


class OnlineScoreboardModuleTest(unittest.TestCase):
    def test_period_order_starts_with_local_and_cycle_wraps(self):
        self.assertEqual(
            SCOREBOARD_PERIOD_ORDER,
            (SCOREBOARD_PERIOD_LOCAL, SCOREBOARD_PERIOD_WEEKLY, SCOREBOARD_PERIOD_SEASON),
        )
        self.assertEqual(cycle_scoreboard_period(SCOREBOARD_PERIOD_LOCAL, 1), SCOREBOARD_PERIOD_WEEKLY)
        self.assertEqual(cycle_scoreboard_period(SCOREBOARD_PERIOD_LOCAL, -1), SCOREBOARD_PERIOD_SEASON)
        self.assertEqual(cycle_scoreboard_period("bad", 1), SCOREBOARD_PERIOD_WEEKLY)

    def test_period_key_and_label_cover_local_week_and_season(self):
        self.assertEqual(scoreboard_period_key(SCOREBOARD_PERIOD_LOCAL, "2026-04-30T20:47:15Z"), "")
        self.assertEqual(scoreboard_period_key(SCOREBOARD_PERIOD_WEEKLY, "2026-04-30T20:47:15Z"), "2026-W18")
        self.assertEqual(scoreboard_period_key(SCOREBOARD_PERIOD_SEASON, "2026-04-30T20:47:15Z"), "2026-Spring")
        self.assertEqual(scoreboard_period_label(SCOREBOARD_PERIOD_LOCAL, LANG_JA), "ローカル")

    def test_utc_formatters_keep_bad_values_visible(self):
        self.assertEqual(format_utc_minute("2026-05-03T03:45:12Z"), "UTC 2026-05-03 03:45")
        self.assertEqual(format_utc_short_minute("2026-05-03T03:45:12Z"), "05-03 03:45")
        self.assertEqual(format_utc_minute("bad"), "bad")
        self.assertEqual(format_utc_short_minute(""), "-")

    def test_period_end_returns_next_utc_boundary(self):
        self.assertEqual(
            scoreboard_period_end(SCOREBOARD_PERIOD_WEEKLY, "2026-04-30T20:47:15Z"),
            datetime(2026, 5, 4, tzinfo=timezone.utc),
        )
        self.assertEqual(
            scoreboard_period_end(SCOREBOARD_PERIOD_SEASON, "2026-04-30T20:47:15Z"),
            datetime(2026, 6, 1, tzinfo=timezone.utc),
        )
        self.assertIsNone(scoreboard_period_end(SCOREBOARD_PERIOD_LOCAL, "2026-04-30T20:47:15Z"))

    def test_period_end_lines_are_language_aware(self):
        self.assertEqual(
            scoreboard_period_ends_line(SCOREBOARD_PERIOD_WEEKLY, LANG_EN, "2026-04-30T20:47:15Z"),
            "This Week ends in 3d 03h 12m at UTC 2026-05-03 23:59",
        )
        self.assertEqual(
            scoreboard_period_ends_line(SCOREBOARD_PERIOD_SEASON, LANG_JA, "2026-04-30T20:47:15Z"),
            "今季の集計終了まで 4w 3d 03h 12m / UTC 2026-05-31 23:59",
        )

    def test_sync_hint_line_uses_profile_timestamps_and_local_fallback(self):
        self.assertEqual(online_sync_hint_line({"local_only": True}, LANG_EN), "Guest scores are not sent")
        self.assertEqual(online_sync_hint_line({"local_only": False}, LANG_EN), "")
        self.assertEqual(
            online_sync_hint_line(
                {
                    "local_only": False,
                    "last_sync_at": "2026-05-03T03:45:12Z",
                    "next_sync_at": "2026-05-04T03:45:12Z",
                },
                LANG_EN,
            ),
            "Posted UTC 05-03 03:45 / POST after 05-03 04:45",
        )

    def test_sync_post_after_display_caps_stale_local_next_sync_to_current_policy(self):
        self.assertEqual(
            sync_post_after_display("2026-05-03T03:45:12Z", "2026-05-04T03:45:12Z"),
            "2026-05-03T04:45:12Z",
        )
        self.assertEqual(
            sync_post_after_display("2026-05-03T03:45:12Z", "2026-05-03T04:15:12Z"),
            "2026-05-03T04:15:12Z",
        )

    def test_result_lines_split_translated_messages_for_scoreboard_box(self):
        self.assertEqual(
            online_result_lines("Ranking refreshed. POST once per hour.", LANG_EN),
            ["Ranking refreshed.", "POST once per hour."],
        )
        self.assertEqual(
            online_result_lines("Ranking refreshed. POST once per hour.", LANG_JA),
            ["ランキング更新。", "POSTは1時間に1回。"],
        )
        self.assertEqual(online_result_lines("one two three four", LANG_EN, limit=9), ["one two", "three"])

    def test_sync_box_lines_distinguish_post_and_refresh_waiting_states(self):
        self.assertEqual(online_sync_box_lines(True, LANG_EN), ["Syncing scores...", "Please wait."])
        self.assertEqual(online_sync_box_lines(False, LANG_EN), ["Refreshing ranking...", "Please wait."])
        self.assertEqual(online_sync_box_lines(False, LANG_JA), ["ランキング更新中...", "お待ちください。"])

    def test_scoreboard_labels_are_language_and_period_specific(self):
        self.assertEqual(score_period_tab_label(SCOREBOARD_PERIOD_LOCAL, LANG_EN), "Local")
        self.assertEqual(score_period_tab_label(SCOREBOARD_PERIOD_WEEKLY, LANG_JA), "今週")
        self.assertEqual(scoreboard_title(SCOREBOARD_PERIOD_LOCAL, LANG_JA), "冒険の記録")
        self.assertEqual(scoreboard_title(SCOREBOARD_PERIOD_SEASON, LANG_EN), "Season Legends")
        self.assertEqual(scoreboard_title("unexpected", LANG_EN), "My Rogue Chronicle")

    def test_current_score_matching_prefers_stable_score_id_then_fallback_fields(self):
        current = {"score_id": "abc", "timestamp": "T1", "player_name": "ACE", "score": 100}
        self.assertTrue(is_current_result_score({"score_id": "abc"}, current))
        self.assertFalse(is_current_result_score({"score_id": "xyz", "timestamp": "T1", "player_name": "ACE", "score": 100}, current))
        self.assertTrue(
            is_current_result_score(
                {"timestamp": "T1", "player_name": "ace", "score": 100},
                {"timestamp": "T1", "player_name": "ACE", "score": 100},
            )
        )
        self.assertFalse(is_current_result_score({"timestamp": "T1", "player_name": "ACE", "score": 99}, current))

    def test_mark_current_score_line_keeps_score_alignment_when_possible(self):
        self.assertEqual(mark_current_score_line(" 1   100 ACE"), ">1   100 ACE")
        self.assertEqual(mark_current_score_line("ACE"), ">ACE")

    def test_score_line_formatter_keeps_japanese_winner_and_nyandor_wording(self):
        self.assertEqual(
            format_score_line_for_board(1, {"score": 9999, "player_name": "ace", "result_flags": "winner", "level": 26}, LANG_JA),
            " 1  9999 ace: 運命の洞窟より生きて帰りたる勇者",
        )
        nyandor_entry = {"score": 555, "player_name": "cat", "result_flags": "winner", "level": 5, "variant": "nyandor"}
        self.assertEqual(format_score_line_for_board(1, nyandor_entry, LANG_JA), " 1   555 cat: ニャンダーのねこを連れ帰りし者")
        self.assertEqual(format_score_line_for_board(1, nyandor_entry, LANG_EN), " 1   555 cat: returned with the Nyandor cat.")
        self.assertEqual(
            format_score_line_for_board(2, {"score": 222, "player_name": "bob", "result_flags": "killed", "level": 5, "killer": "orc"}, LANG_JA),
            " 2   222 bob: 5階で欲ばり鬼に倒された。",
        )
        self.assertEqual(
            format_score_line_for_board(3, {"score": 111, "player_name": "ann", "result_flags": "killed_with_amulet", "level": 7, "killer": "fire"}, LANG_JA),
            " 3   111 ann: アミュレット所持中、7階で炎に倒された。",
        )

    def test_score_killer_name_translates_japanese_monsters_bolts_and_special_causes(self):
        self.assertEqual(score_killer_name(LANG_JA, "hobgoblin"), "小鬼")
        self.assertEqual(score_killer_name(LANG_JA, "fire"), "炎")
        self.assertEqual(score_killer_name(LANG_JA, "starvation"), "飢え")
        self.assertEqual(score_killer_name(LANG_EN, "orc"), "orc")

    def test_scoreboard_entry_rows_mark_current_local_and_remote_player_rows(self):
        scores = [
            {"score_id": "cur", "score": 200, "player_name": "ace", "result_flags": "quit", "level": 3},
            {"score_id": "old", "score": 100, "player_name": "bob", "result_flags": "killed", "level": 2},
        ]
        local_rows = scoreboard_entry_rows(
            scores,
            SCOREBOARD_PERIOD_LOCAL,
            LANG_EN,
            current_player_name="ace",
            current_entry={"score_id": "cur"},
        )
        self.assertEqual(local_rows[0].line[0], ">")
        self.assertTrue(local_rows[0].highlight)
        self.assertFalse(local_rows[1].highlight)

        weekly_rows = scoreboard_entry_rows(scores, SCOREBOARD_PERIOD_WEEKLY, LANG_EN, current_player_name="ace")
        self.assertTrue(weekly_rows[0].highlight)
        self.assertFalse(weekly_rows[1].highlight)

    def test_guest_local_best_row_uses_separator_prefix_for_remote_periods_only(self):
        entry = {"score": 321, "player_name": "guest", "result_flags": "quit", "level": 4}
        row = score_guest_local_best_row(entry, SCOREBOARD_PERIOD_WEEKLY, LANG_EN)
        self.assertIsNotNone(row)
        self.assertTrue(row.line.startswith("--"))
        self.assertTrue(row.highlight)
        self.assertIsNone(score_guest_local_best_row(entry, SCOREBOARD_PERIOD_LOCAL, LANG_EN))
        self.assertIsNone(score_guest_local_best_row(None, SCOREBOARD_PERIOD_WEEKLY, LANG_EN))


if __name__ == "__main__":
    unittest.main()
