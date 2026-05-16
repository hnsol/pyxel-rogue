import tempfile
import unittest
from pathlib import Path

from tools import generate_wiki


class GenerateWikiTests(unittest.TestCase):
    def test_monster_prob_matrix_uses_rogue_544_depth_window(self):
        matrix = generate_wiki.monster_prob_matrix()

        self.assertEqual(set(matrix), set(range(1, 27)))
        for probs in matrix.values():
            self.assertAlmostEqual(sum(probs.values()), 1.0)

        self.assertAlmostEqual(matrix[1]["K"], 0.2)
        self.assertAlmostEqual(matrix[1]["H"], 0.2)
        self.assertAlmostEqual(matrix[26]["U"], 0.1)
        self.assertAlmostEqual(matrix[26]["D"], 0.18)

    def test_average_damage_expr(self):
        self.assertEqual(generate_wiki.average_damage_expr("4x4"), 10.0)
        self.assertEqual(generate_wiki.average_damage_expr("1x8/1x8/2x6"), 16.0)
        self.assertEqual(generate_wiki.average_damage_expr("0x0/0x0"), 0.0)

    def test_generate_includes_synced_game_tables(self):
        ja = generate_wiki.generate("ja")
        en = generate_wiki.generate("en")

        self.assertIn("# 攻略ガイド", ja)
        self.assertIn("## はじめての探索", ja)
        self.assertIn("Beginner-Guide-ja.svg", ja)
        self.assertNotIn("A空押し", ja)
        self.assertLess(ja.index("## はじめての探索"), ja.index("## フロア別モンスター出現率"))
        self.assertLess(ja.index("## 警告"), ja.index("> [!WARNING]"))
        self.assertLess(ja.index("ここから先はネタバレです"), ja.index("## フロア別モンスター出現率"))
        self.assertIn("> [!WARNING]", ja)
        self.assertIn("## フロア別モンスター出現率", ja)
        self.assertIn("Monster-Appearance-ja.svg", ja)
        self.assertIn("## ドロップ期待値表", ja)
        self.assertNotIn("| 階 | 上位候補 | 名前 |", ja)
        self.assertNotIn("### 各階", ja)
        self.assertNotIn("### 到達時累計", ja)
        self.assertIn("食糧消費補正", ja)
        self.assertIn("大きな剣", ja)
        self.assertIn("light: 10-19", en)
        self.assertIn("# Game Guide", en)
        self.assertIn("## First Exploration", en)
        self.assertIn("Beginner-Guide-en.svg", en)
        self.assertIn("## Warning", en)
        self.assertIn("Spoiler Warning", en)
        self.assertIn("## Monster Appearance by Floor", en)

    def test_beginner_card_uses_correct_control_copy(self):
        ja = generate_wiki.beginner_guide_svg("ja")

        self.assertIn("Select の Log", ja)
        self.assertIn("長い通路をラクに進む", ja)
        self.assertNotIn("ログで覚える", ja)
        self.assertNotIn("敵から逃げる万能", ja)
        self.assertNotIn("A空押し", ja)
        self.assertNotIn('fill="#191816"', ja)
        self.assertIn('height="680"', ja)
        self.assertIn('y="184" width="408" height="410"', ja)

    def test_throwing_weapons_are_sorted_by_thrown_damage(self):
        ja = generate_wiki.weapon_section("ja")

        self.assertLess(ja.index("| 投擲 | 投げ矢 |"), ja.index("| 投擲 | 短剣 |"))
        self.assertLess(ja.index("| 投擲 | 短剣 |"), ja.index("| 投擲 | 槍 |"))
        self.assertLess(ja.index("| 投擲 | 槍 |"), ja.index("| 投擲 | 手裏剣 |"))

    def test_write_wiki_files_creates_expected_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            generate_wiki.write_wiki(Path(tmp))

            self.assertTrue((Path(tmp) / "Game-Guide-ja.md").exists())
            self.assertTrue((Path(tmp) / "Game-Guide-en.md").exists())
            self.assertTrue((Path(tmp) / "Beginner-Guide-ja.svg").exists())
            self.assertTrue((Path(tmp) / "Monster-Appearance-ja.svg").exists())
            self.assertTrue((Path(tmp) / "Drop-Rate-Reference-ja.svg").exists())
            self.assertIn("攻略情報", (Path(tmp) / "_Sidebar.md").read_text(encoding="utf-8"))
            self.assertIn("Game Guide", (Path(tmp) / "Home.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
