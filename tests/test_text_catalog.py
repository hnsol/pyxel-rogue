import contextlib
import io
import unittest

from pyxel_rogue.rogue_items import CAT_WPN
from pyxel_rogue.rogue_lang import LANG_EN, LANG_JA
from pyxel_rogue.rogue_text import TextCatalog


class TextCatalogModuleTest(unittest.TestCase):
    def test_message_catalog_reads_english_and_japanese_entries(self):
        self.assertEqual(TextCatalog.msg(LANG_EN, "info.inventory"), "Inventory")
        self.assertEqual(TextCatalog.msg(LANG_JA, "info.inventory"), "持ちもの")

    def test_terms_support_hud_item_names_and_monster_names(self):
        self.assertEqual(TextCatalog.hud_item_kind(LANG_EN, CAT_WPN, "two-handed sword"), "2H sw")
        self.assertEqual(TextCatalog.monster(LANG_JA, "aquator"), "水ごけの怪物")

    def test_missing_japanese_message_falls_back_to_english_then_marker(self):
        self.assertEqual(TextCatalog.msg("bad-lang", "info.settings"), "Settings")
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(TextCatalog.msg(LANG_EN, "missing.test.catalog.key"), "[missing:missing.test.catalog.key]")


if __name__ == "__main__":
    unittest.main()
