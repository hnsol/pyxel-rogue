import unittest

from pyxel_rogue import rogue_variant
from pyxel_rogue.rogue_difficulty import DIFF_NORMAL
from pyxel_rogue.rogue_lang import LANG_EN, LANG_JA


class VariantModuleTest(unittest.TestCase):
    def test_normalize_variant_accepts_cat_aliases_only_for_nyandor(self):
        self.assertEqual(rogue_variant.normalize_variant("cat"), rogue_variant.VARIANT_NYANDOR)
        self.assertEqual(rogue_variant.normalize_variant("nyander"), rogue_variant.VARIANT_NYANDOR)
        self.assertEqual(rogue_variant.normalize_variant("unknown"), rogue_variant.VARIANT_ROGUE)

    def test_nyandor_variant_fixes_difficulty_and_scoreboard_key(self):
        self.assertEqual(rogue_variant.variant_fixed_difficulty(rogue_variant.VARIANT_NYANDOR), DIFF_NORMAL)
        self.assertIsNone(rogue_variant.variant_fixed_difficulty(rogue_variant.VARIANT_ROGUE))
        self.assertEqual(rogue_variant.variant_scoreboard_key(rogue_variant.VARIANT_NYANDOR), rogue_variant.VARIANT_NYANDOR)
        self.assertIsNone(rogue_variant.variant_scoreboard_key(rogue_variant.VARIANT_ROGUE))

    def test_variant_labels_are_language_aware(self):
        self.assertEqual(rogue_variant.variant_window_title(rogue_variant.VARIANT_ROGUE), "Pyxel Rogue")
        self.assertIn("CAT RECOVERY ORDER", rogue_variant.variant_mission_brief_lines(LANG_EN))
        self.assertIn("ねこを回収せよ", rogue_variant.variant_mission_brief_lines(LANG_JA))


if __name__ == "__main__":
    unittest.main()
