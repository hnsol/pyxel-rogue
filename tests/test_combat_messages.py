import os
import sys
import unittest


TESTS_DIR = os.path.dirname(__file__)
if TESTS_DIR not in sys.path:
    sys.path.insert(0, TESTS_DIR)

from test_rogue_baseline import new_game, set_open_floor, monster_at, rogue


class ForcedRnd:
    def __init__(self, value):
        self.value = value

    def __enter__(self):
        self.old_rnd = rogue.RNG.rnd
        rogue.RNG.rnd = lambda n: self.value

    def __exit__(self, exc_type, exc, tb):
        rogue.RNG.rnd = self.old_rnd


class CombatMessageTests(unittest.TestCase):
    def test_player_hit_message_uses_fight_c_variants(self):
        game = new_game(seed=101)
        with ForcedRnd(2):
            msg = game.player_hit_message("the hobgoblin")
        self.assertEqual(msg, "You have injured the hobgoblin")

    def test_player_miss_message_uses_fight_c_variants(self):
        game = new_game(seed=102)
        with ForcedRnd(1):
            msg = game.player_miss_message("the hobgoblin")
        self.assertEqual(msg, "You swing and miss the hobgoblin")

    def test_monster_hit_message_uses_fight_c_variants(self):
        game = new_game(seed=103)
        with ForcedRnd(3):
            msg = game.monster_hit_message("The hobgoblin")
        self.assertEqual(msg, "The hobgoblin swings and hits you")

    def test_monster_miss_message_uses_fight_c_variants(self):
        game = new_game(seed=104)
        with ForcedRnd(2):
            msg = game.monster_miss_message("The hobgoblin")
        self.assertEqual(msg, "The hobgoblin barely misses you")

    def test_defeated_message_omits_exp_but_awards_exp(self):
        game = new_game(seed=105)
        set_open_floor(game)
        monster = monster_at(game.p.x + 1, game.p.y, hp=2, armor=100, exp=3)
        game.mons = [monster]
        game.roll_player_attack = lambda m, weap=None, thrown=False: (True, 2)

        with ForcedRnd(1):
            game.p_attack(monster)

        self.assertFalse(monster.alive)
        self.assertEqual(game.p.exp, 3)
        self.assertIn("Defeated the hobgoblin", game.msgs)
        self.assertFalse(any("exp" in msg.lower() for msg in game.msgs))

    def test_japanese_combat_message_keys_are_available(self):
        game = new_game(seed=106, lang=rogue.LANG_JA)
        with ForcedRnd(0):
            msg = game.player_hit_message("小鬼")
        self.assertNotIn("[missing:", msg)
        self.assertIn("小鬼", msg)

    def test_thrown_weapon_messages_omit_damage(self):
        game = new_game(seed=107)
        set_open_floor(game)
        arrow = rogue.Item(rogue.CAT_WPN, 3, hit_plus=0, dam_plus=0)
        monster = monster_at(game.p.x + 2, game.p.y, hp=8, armor=100, exp=0)
        game.p.inv = [arrow]
        game.mons = [monster]
        game.roll_player_attack = lambda m, weap=None, thrown=False: (True, 1)

        game.throw(arrow, 1, 0)

        for _ in range(len(game.throw_anim["path"]) * game.throw_anim["delay"]):
            rogue.pyxel.set_input()
            game.update()

        self.assertTrue(any("hits the hobgoblin" in msg for msg in game.msgs))
        self.assertFalse(any("(1)" in msg or "damage" in msg.lower() for msg in game.msgs))

    def test_thrown_miss_messages_omit_damage(self):
        game = new_game(seed=108)
        set_open_floor(game)
        arrow = rogue.Item(rogue.CAT_WPN, 3, hit_plus=0, dam_plus=0)
        monster = monster_at(game.p.x + 2, game.p.y, hp=8, armor=0, exp=0)
        game.p.inv = [arrow]
        game.mons = [monster]
        game.roll_player_attack = lambda m, weap=None, thrown=False: (False, 0)

        game.throw(arrow, 1, 0)

        for _ in range(len(game.throw_anim["path"]) * game.throw_anim["delay"]):
            rogue.pyxel.set_input()
            game.update()

        self.assertTrue(any("misses the hobgoblin" in msg for msg in game.msgs))
        self.assertFalse(any("(" in msg for msg in game.msgs))


if __name__ == "__main__":
    unittest.main()
