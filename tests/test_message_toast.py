import unittest

from pyxel_rogue import rogue_layout, rogue_message_toast
from pyxel_rogue.rogue_map import MAP_W, PLAY_Y_MIN


class MessageToastModuleTest(unittest.TestCase):
    def test_home_block_clamps_player_position_to_visible_grid(self):
        self.assertEqual(
            rogue_message_toast.msg_toast_home_block(-20, PLAY_Y_MIN - 10),
            (0, 0),
        )
        self.assertEqual(
            rogue_message_toast.msg_toast_home_block(MAP_W + 20, PLAY_Y_MIN + 99),
            (2, 2),
        )

    def test_pick_block_follows_last_intent_and_avoids_current_home(self):
        self.assertEqual(rogue_message_toast.pick_msg_toast_block((1, 1), (1, 0)), (2, 1))
        self.assertEqual(rogue_message_toast.pick_msg_toast_block((1, 1), (0, -1)), (1, 0))
        self.assertEqual(
            rogue_message_toast.pick_msg_toast_block((1, 1), (1, 0), avoid=((2, 1),)),
            (1, 2),
        )

    def test_block_origin_uses_grid_edges_and_screen_offsets(self):
        self.assertEqual(
            rogue_message_toast.msg_toast_block_origin((1, 2), 2),
            (
                rogue_layout.ZV_X
                + rogue_layout.MSG_TOAST_GRID_COL_EDGES[1] * rogue_layout.TILE_W
                + rogue_layout.FONT_ASCII_W,
                rogue_layout.ZV_Y + rogue_layout.MSG_TOAST_GRID_ROW_EDGES[2] * rogue_layout.TILE_H + 2,
            ),
        )


if __name__ == "__main__":
    unittest.main()
