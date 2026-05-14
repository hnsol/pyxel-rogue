import unittest

from pyxel_rogue.rogue_lang import LANG_EN, LANG_JA
from pyxel_rogue.rogue_online_text import online_text


class OnlineTextModuleTest(unittest.TestCase):
    def test_online_text_reads_language_specific_entries(self):
        self.assertEqual(online_text(LANG_EN, "score_tab_weekly"), "This Week")
        self.assertEqual(online_text(LANG_JA, "score_tab_weekly"), "今週")

    def test_online_text_falls_back_to_english_then_key(self):
        self.assertEqual(online_text("bad-lang", "register_title"), "Online Sync")
        self.assertEqual(online_text(LANG_JA, "unknown-online-key"), "unknown-online-key")


if __name__ == "__main__":
    unittest.main()
