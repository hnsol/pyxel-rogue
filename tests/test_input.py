import unittest

from pyxel_rogue import rogue_input


class TestRogueInput(unittest.TestCase):
    def test_cardinal_press_is_buffered_for_one_frame(self):
        direction, pending = rogue_input.direction_press(
            held={"right"},
            pressed={"right"},
            pending=None,
            diag_assist=False,
        )
        self.assertIsNone(direction)
        self.assertEqual(pending, (1, 0))

        direction, pending = rogue_input.direction_press(
            held=set(),
            pressed=set(),
            pending=pending,
            diag_assist=False,
        )
        self.assertEqual(direction, (1, 0))
        self.assertIsNone(pending)

    def test_diagonal_assist_accepts_only_chorded_directions(self):
        direction, pending = rogue_input.direction_press(
            held={"start", "right"},
            pressed={"right"},
            pending=None,
            diag_assist=True,
        )
        self.assertIsNone(direction)
        self.assertIsNone(pending)

        direction, pending = rogue_input.direction_press(
            held={"start", "right", "down"},
            pressed={"right"},
            pending=None,
            diag_assist=True,
        )
        self.assertEqual(direction, (1, 1))
        self.assertIsNone(pending)

    def test_vi_diagonals_are_immediate(self):
        direction, pending = rogue_input.direction_press(
            held={"u"},
            pressed={"u"},
            pending=(1, 0),
            diag_assist=False,
        )
        self.assertEqual(direction, (1, -1))
        self.assertIsNone(pending)

    def test_held_direction_respects_diag_assist(self):
        self.assertIsNone(rogue_input.held_direction({"right"}, diag_assist=True))
        self.assertEqual(
            rogue_input.held_direction({"right", "down"}, diag_assist=True),
            (1, 1),
        )
        self.assertEqual(rogue_input.held_direction({"right"}, diag_assist=False), (1, 0))

    def test_select_direction_requires_back_and_pressed_direction(self):
        self.assertIsNone(
            rogue_input.select_direction(
                held={"back", "right"},
                pressed=set(),
                back_held=True,
            )
        )
        self.assertEqual(
            rogue_input.select_direction(
                held={"back", "right"},
                pressed={"right"},
                back_held=True,
            ),
            (1, 0),
        )
        self.assertIsNone(
            rogue_input.select_direction(
                held={"right"},
                pressed={"right"},
                back_held=False,
            )
        )

    def test_count_digit_ignores_shift_and_ctrl(self):
        self.assertEqual(rogue_input.count_digit({"3"}, shifted=False, controlled=False), 3)
        self.assertIsNone(rogue_input.count_digit({"3"}, shifted=True, controlled=False))
        self.assertIsNone(rogue_input.count_digit({"3"}, shifted=False, controlled=True))

    def test_repeat_state_records_previous_command_and_resets_on_abort(self):
        state = rogue_input.RepeatState()

        state.record("search")
        state.remember_dir((1, 0))
        state.record(("item", "Throw"))
        state.remember_item("dart")

        self.assertEqual(state.previous_command, "search")
        self.assertEqual(state.previous_dir, (1, 0))
        self.assertEqual(state.command, ("item", "Throw"))
        self.assertEqual(state.item, "dart")

        state.reset()

        self.assertEqual(state.command, "search")
        self.assertEqual(state.direction, (1, 0))
        self.assertIsNone(state.item)

    def test_repeat_state_ignores_records_while_repeating(self):
        state = rogue_input.RepeatState(command="search", active=True)

        state.record("wait")
        state.remember_dir((0, 1))
        state.remember_item("food")

        self.assertEqual(state.command, "search")
        self.assertIsNone(state.direction)
        self.assertIsNone(state.item)

    def test_count_input_state_accumulates_caps_and_records_repeat(self):
        state = rogue_input.CountInputState()

        for digit in (2, 5, 6):
            state.start_prefix(digit)

        self.assertEqual(state.prefix_value, 255)
        self.assertFalse(state.record_counted("move", True, (1, 0)))
        self.assertFalse(state.prefix_active)
        self.assertEqual(state.repeat_command, "move")
        self.assertEqual(state.repeat_remaining, 254)
        self.assertEqual(state.repeat_dir, (1, 0))

    def test_count_input_state_clears_non_countable_prefix(self):
        state = rogue_input.CountInputState()

        state.start_prefix(3)

        self.assertTrue(state.record_counted("version", False))
        self.assertFalse(state.prefix_active)
        self.assertEqual(state.prefix_value, 0)
        self.assertIsNone(state.repeat_command)

    def test_count_input_state_schedules_counted_again(self):
        state = rogue_input.CountInputState()

        state.start_prefix(4)

        self.assertEqual(state.take_prefix(), 4)
        state.start_repeat("again", 4)
        self.assertEqual(state.repeat_command, "again")
        self.assertEqual(state.repeat_remaining, 3)

    def test_tap_button_state_emits_short_release_tap(self):
        state = rogue_input.TapButtonState()

        state.update(True, tap_frames=6)
        state.update(False, tap_frames=6)

        self.assertTrue(state.tap)
        self.assertFalse(state.used)
        self.assertEqual(state.frames, 0)

    def test_tap_button_state_suppresses_used_and_long_release(self):
        used = rogue_input.TapButtonState()
        used.update(True, tap_frames=6)
        used.mark_used()
        used.update(False, tap_frames=6)
        self.assertFalse(used.tap)

        long = rogue_input.TapButtonState()
        for _ in range(7):
            long.update(True, tap_frames=6)
        long.update(False, tap_frames=6)
        self.assertFalse(long.tap)

    def test_dash_state_start_stop_and_release_guard(self):
        state = rogue_input.DashState()

        self.assertTrue(state.can_start(run_held=True, restart_dir_pressed=False))
        state.start((1, 0))
        self.assertTrue(state.active)
        self.assertEqual(state.direction, (1, 0))
        self.assertEqual(state.timer, 0)
        self.assertEqual(state.steps, 0)

        state.stop(restart_guard=True)
        self.assertFalse(state.active)
        self.assertTrue(state.restart_guard)
        self.assertFalse(state.can_start(run_held=True, restart_dir_pressed=False))
        self.assertTrue(state.can_start(run_held=True, restart_dir_pressed=True))

        state.update_release(run_held=False)
        self.assertFalse(state.restart_guard)

    def test_dash_state_tick_reports_due_steps(self):
        state = rogue_input.DashState(active=True, direction=(1, 0))

        self.assertFalse(state.tick(interval=3))
        self.assertEqual(state.timer, 1)
        self.assertFalse(state.tick(interval=3))
        self.assertEqual(state.timer, 2)
        self.assertTrue(state.tick(interval=3))
        self.assertEqual(state.timer, 0)

    def test_dash_state_records_completed_step_and_continuation(self):
        state = rogue_input.DashState(active=True, direction=(1, 0))

        state.finish_step(continues=True)
        self.assertTrue(state.active)
        self.assertEqual(state.steps, 1)
        self.assertFalse(state.restart_guard)

        state.finish_step(continues=False)
        self.assertFalse(state.active)
        self.assertEqual(state.steps, 2)
        self.assertTrue(state.restart_guard)


if __name__ == "__main__":
    unittest.main()
