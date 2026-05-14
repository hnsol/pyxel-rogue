import unittest

from pyxel_rogue import rogue_palettes


class PaletteHelpersModuleTest(unittest.TestCase):
    def test_every_palette_theme_defines_required_roles(self):
        for palette_id in rogue_palettes.PALETTE_IDS:
            theme = rogue_palettes.palette_theme(palette_id)
            self.assertEqual(rogue_palettes.PALETTE_COLOR_LIMIT, len(theme.colors))
            self.assertTrue(set(rogue_palettes.REQUIRED_PALETTE_ROLES).issubset(theme.roles))
            self.assertTrue(set(rogue_palettes.REQUIRED_MONSTER_ROLES).issubset(theme.monster_roles))

    def test_monster_color_uses_overrides_then_role_mapping_then_text_fallback(self):
        self.assertEqual(
            rogue_palettes.palette_monster_color(rogue_palettes.PALETTE_FLEXOKI_DARK, "P"),
            2,
        )
        self.assertEqual(
            rogue_palettes.palette_monster_color(rogue_palettes.PALETTE_FLEXOKI_LIGHT, "B"),
            rogue_palettes.FLEXOKI_LIGHT_MONSTER_ROLES[rogue_palettes.MONSTER_BEAST],
        )
        self.assertEqual(
            rogue_palettes.palette_monster_color(rogue_palettes.PALETTE_FLEXOKI_DARK, "?"),
            rogue_palettes.BASE_ROLES[rogue_palettes.ROLE_TEXT],
        )


if __name__ == "__main__":
    unittest.main()
