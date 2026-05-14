from types import SimpleNamespace
import unittest

from pyxel_rogue import rogue_hud
from pyxel_rogue.rogue_items import CAT_ARM, CAT_WPN
from pyxel_rogue.rogue_lang import LANG_EN, LANG_JA
from pyxel_rogue.rogue_palettes import ROLE_FLAG_OFF, ROLE_FLAG_ON, ROLE_STATUS_BAD, ROLE_STATUS_BUFF, ROLE_STATUS_MIND


def item(cat, **kw):
    base = {
        "cat": cat,
        "data": {"name": "mace" if cat == CAT_WPN else "plate mail"},
        "stackable": False,
        "qty": 1,
        "known": True,
        "hit_plus": 0,
        "dam_plus": 0,
        "ench": 0,
    }
    base.update(kw)
    return SimpleNamespace(**base)


def player(**kw):
    base = {
        "state": "normal",
        "confused": 0,
        "blind": 0,
        "haste": 0,
        "hallucinating": 0,
        "levitating": 0,
    }
    base.update(kw)
    return SimpleNamespace(**base)


class HudModuleTest(unittest.TestCase):
    def test_known_equipment_names_include_relevant_bonuses(self):
        self.assertEqual(
            rogue_hud.hud_equip_name(item(CAT_WPN, hit_plus=1, dam_plus=-1), LANG_EN, str),
            "+1,-1 mace",
        )
        self.assertEqual(
            rogue_hud.hud_equip_name(item(CAT_ARM, ench=2), LANG_EN, str),
            "+2 plate",
        )

    def test_unknown_equipment_hides_bonuses_but_keeps_kind(self):
        self.assertEqual(
            rogue_hud.hud_equip_name(item(CAT_WPN, known=False, hit_plus=2, dam_plus=3), LANG_EN, str),
            "mace",
        )
        self.assertEqual(rogue_hud.hud_weapon_bonus(item(CAT_WPN, known=False)), "?,?")
        self.assertEqual(rogue_hud.hud_armor_bonus(item(CAT_ARM, known=False)), "?")

    def test_empty_slot_labels_follow_language(self):
        self.assertEqual(rogue_hud.hud_weapon_empty_name(LANG_EN), "bare hands")
        self.assertEqual(rogue_hud.hud_armor_empty_name(LANG_JA), "防具なし")

    def test_condition_chips_keep_status_order_and_roles(self):
        p = player(state="faint", confused=3, haste=4, levitating=5)

        self.assertEqual(
            rogue_hud.hud_condition_chips(p, LANG_EN, True),
            [
                ("Faint", ROLE_STATUS_BAD),
                ("Confuse", ROLE_STATUS_MIND),
                ("Haste", ROLE_STATUS_BUFF),
                ("Levit", ROLE_STATUS_BUFF),
            ],
        )
        self.assertEqual(rogue_hud.hud_condition_chips(p, LANG_EN, False), [])

    def test_mode_chips_report_autopickup_and_diagonal_assist_flags(self):
        self.assertEqual(
            rogue_hud.hud_mode_chips(auto_pickup=True, diag_assist=False),
            (("P", ROLE_FLAG_ON), ("X", ROLE_FLAG_OFF)),
        )


if __name__ == "__main__":
    unittest.main()
