import os
import unittest

from tests.test_rogue_baseline import rogue
from pyxel_rogue import rogue_title


class TitleAssetsModuleTest(unittest.TestCase):
    def test_title_constants_describe_assets_timing_and_layout(self):
        self.assertTrue(rogue_title.FONT_PATH.endswith(os.path.join("assets", "umplus_j10r.bdf")))
        self.assertEqual(
            rogue_title.LOGO_TOTAL_FRAMES,
            rogue_title.LOGO_BGM_DELAY_FRAMES
            + rogue_title.LOGO_FADE_FRAMES
            + rogue_title.LOGO_HOLD_FRAMES
            + rogue_title.LOGO_FADE_FRAMES,
        )
        self.assertEqual(rogue_title.TITLE_MENU_X, rogue_title.TITLE_LOGO_RIGHT_X - rogue_title.TITLE_MENU_W + 28)
        self.assertEqual(len(rogue_title.TITLE_BGM_MMLS), 3)

    def test_title_background_paths_exist(self):
        self.assertTrue(os.path.exists(rogue_title.TITLE_BG_PATH))
        self.assertTrue(os.path.exists(rogue_title.TITLE_BG_NYANDOR_PATH))

    def test_load_title_background_keeps_loaded_image(self):
        class CheckingImage:
            def __init__(self, w, h):
                self.w = w
                self.h = h
                self.load_calls = []

            def load(self, x, y, path):
                if not os.path.exists(path):
                    raise FileNotFoundError(path)
                self.load_calls.append((x, y, path))

        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_TITLE
        old_image = rogue.pyxel.Image
        try:
            rogue.pyxel.Image = CheckingImage
            game.load_title_background()
        finally:
            rogue.pyxel.Image = old_image

        self.assertIsNotNone(game.title_bg)
        self.assertEqual(game.title_bg.load_calls, [(0, 0, rogue.variant_title_background_path())])


if __name__ == "__main__":
    unittest.main()
