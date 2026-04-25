import os
import sys
import unittest


TEST_DIR = os.path.dirname(__file__)
if TEST_DIR not in sys.path:
    sys.path.insert(0, TEST_DIR)

from test_rogue_baseline import new_game, rogue


class FixedRng:
    def __init__(self):
        self.choice_index = -1

    def rnd(self, n):
        return 0

    def roll(self, number, sides):
        return 4

    def spread(self, nm):
        return nm - nm // 20 + self.rnd(nm // 10)

    def randint(self, a, b):
        return a

    def randrange(self, n):
        return 0

    def random(self):
        return 0.0

    def choice(self, seq):
        return seq[self.choice_index]

    def shuffle(self, seq):
        pass


def two_room_floor(game):
    game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
    left = rogue.Room(1, 1, 8, 6)
    right = rogue.Room(20, 1, 8, 6)
    game.rooms = [left, right]
    for room in game.rooms:
        for y in range(room.y + 1, room.y + room.h - 1):
            for x in range(room.x + 1, room.x + room.w - 1):
                game.tm[y][x] = rogue.T_FLOOR
    game.p.x, game.p.y = 3, 3
    game.mons = []
    game.gitems = []
    game.traps = {}
    game.hidden_tiles = {}
    game.update_fov()
    return left, right


class WanderingMonsterTests(unittest.TestCase):
    def test_rogue_544_spread_matches_misc_c_formula(self):
        rng = rogue.RogueRng(FixedRng())
        self.assertEqual(rng.spread(70), 67)

    def test_rogue_544_wanderer_spawns_outside_player_room_and_runs(self):
        game = new_game(seed=100)
        player_room, other_room = two_room_floor(game)
        original_rng = rogue.RNG
        rogue.RNG = FixedRng()
        try:
            self.assertTrue(game.spawn_wanderer())
        finally:
            rogue.RNG = original_rng

        self.assertEqual(len(game.mons), 1)
        monster = game.mons[0]
        self.assertTrue(monster.running)
        self.assertIsNot(game.room_containing(monster.x, monster.y), player_room)
        self.assertIs(game.room_containing(monster.x, monster.y), other_room)

    def test_rogue_544_rollwand_creates_wanderer_after_fourth_roll(self):
        game = new_game(seed=101)
        two_room_floor(game)
        game.fuses.extinguish("swander")
        game.daemons.start("rollwand", rogue.rogue_daemons.BEFORE)
        game.wander_between = 3
        original_rng = rogue.RNG
        rogue.RNG = FixedRng()
        try:
            game.end_turn()
        finally:
            rogue.RNG = original_rng

        self.assertEqual(len(game.mons), 1)
        self.assertTrue(game.mons[0].running)
        self.assertGreater(game.fuses.remaining("swander"), 0)
        self.assertEqual(game.wander_between, 0)

    def test_rogue_544_swander_fuse_starts_rollwand_before_daemon(self):
        # Rogue 5.4.4 main.c:fuse(swander, WANDERTIME, BEFORE);
        # daemons.c:swander() starts rollwand as a BEFORE daemon.
        game = new_game(seed=102)
        two_room_floor(game)
        game.fuses.extinguish("swander")
        game.fuses.fuse("swander", 1, rogue.rogue_daemons.BEFORE)

        game.end_turn()

        self.assertTrue(game.daemons.running("rollwand", rogue.rogue_daemons.BEFORE))
        self.assertEqual(len(game.mons), 0)

    def test_rogue_544_rollwand_daemon_reschedules_swander_fuse_after_spawn(self):
        # Rogue 5.4.4 daemons.c:rollwand() kills rollwand and fuses swander after wanderer().
        game = new_game(seed=103)
        two_room_floor(game)
        game.fuses.extinguish("swander")
        game.daemons.start("rollwand", rogue.rogue_daemons.BEFORE)
        game.wander_between = 3
        original_rng = rogue.RNG
        rogue.RNG = FixedRng()
        try:
            game.end_turn()
        finally:
            rogue.RNG = original_rng

        self.assertEqual(len(game.mons), 1)
        self.assertFalse(game.daemons.running("rollwand", rogue.rogue_daemons.BEFORE))
        self.assertGreater(game.fuses.remaining("swander"), 0)


if __name__ == "__main__":
    unittest.main()
