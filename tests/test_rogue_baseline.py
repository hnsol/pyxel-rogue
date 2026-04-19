import importlib
import os
import random
import sys
import types
import unittest


class SequenceRng:
    def __init__(self, values=None):
        self.values = list(values or [])
        self.calls = []

    def rnd(self, n):
        self.calls.append(n)
        if not self.values:
            return 0
        return self.values.pop(0)

    def shuffle(self, seq):
        pass


def install_pyxel_mock():
    pyxel = types.ModuleType("pyxel")
    pyxel._held = set()
    pyxel._pressed = set()
    pyxel.btn = lambda k: k in pyxel._held
    pyxel.btnp = lambda k: k in pyxel._pressed
    pyxel.set_input = lambda held=(), pressed=(): (
        pyxel._held.clear(),
        pyxel._held.update(held),
        pyxel._pressed.clear(),
        pyxel._pressed.update(pressed),
    )
    pyxel.init = lambda *a, **kw: None
    pyxel.run = lambda *a, **kw: None
    pyxel.cls = lambda *a, **kw: None
    pyxel.text = lambda *a, **kw: None
    pyxel.rect = lambda *a, **kw: None
    pyxel.rectb = lambda *a, **kw: None
    pyxel.__file__ = os.path.join(os.getcwd(), "pyxel", "__init__.py")
    for i, key in enumerate([
        "KEY_UP", "KEY_DOWN", "KEY_LEFT", "KEY_RIGHT",
        "KEY_H", "KEY_J", "KEY_K", "KEY_L",
        "KEY_Y", "KEY_U", "KEY_B", "KEY_N",
        "KEY_Z", "KEY_X", "KEY_C", "KEY_S",
        "KEY_I", "KEY_6",
        "KEY_ESCAPE", "KEY_RETURN", "KEY_TAB", "KEY_PERIOD",
        "KEY_QUESTION", "KEY_SLASH", "KEY_R",
        "KEY_SHIFT", "KEY_LSHIFT", "KEY_RSHIFT",
        "KEY_CTRL", "KEY_LCTRL", "KEY_RCTRL",
        "GAMEPAD1_BUTTON_A", "GAMEPAD1_BUTTON_B",
        "GAMEPAD1_BUTTON_X", "GAMEPAD1_BUTTON_Y",
        "GAMEPAD1_BUTTON_LEFTSHOULDER", "GAMEPAD1_BUTTON_RIGHTSHOULDER",
        "GAMEPAD1_BUTTON_BACK", "GAMEPAD1_BUTTON_START",
        "GAMEPAD1_BUTTON_DPAD_UP", "GAMEPAD1_BUTTON_DPAD_DOWN",
        "GAMEPAD1_BUTTON_DPAD_LEFT", "GAMEPAD1_BUTTON_DPAD_RIGHT",
    ]):
        setattr(pyxel, key, i)

    class MockFont:
        def __init__(self, *a, **kw):
            pass

        def text_width(self, s):
            return len(str(s)) * 6

    pyxel.Font = MockFont
    sys.modules["pyxel"] = pyxel


install_pyxel_mock()
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
rogue = importlib.import_module("rogue")


def new_game(seed=1, lang=rogue.LANG_EN):
    rogue.pyxel.set_input()
    random.seed(seed)
    game = rogue.Game.__new__(rogue.Game)
    game.lang = lang
    game.new_game()
    return game


def set_open_floor(game):
    game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
    for y in range(rogue.PLAY_Y_MIN, rogue.PLAY_Y_MAX + 1):
        for x in range(rogue.MAP_W):
            game.tm[y][x] = rogue.T_FLOOR
    game.rooms = [rogue.Room(0, rogue.PLAY_Y_MIN, rogue.MAP_W, rogue.PLAY_H)]
    game.mons = []
    game.gitems = []
    game.traps = {}
    game.hidden_tiles = {}
    game.p.x = rogue.MAP_W // 2
    game.p.y = rogue.MAP_H // 2
    game.update_fov()


def monster_at(x, y, sym="H", name="hobgoblin", hp=10, level=1, armor=5,
               damage="1x8", exp=3, flags=""):
    return rogue.Monster(x, y, sym, name, hp, level, armor, damage, exp, flags)


def reachable_tiles(tm, start):
    seen = set()
    stack = [start]
    while stack:
        x, y = stack.pop()
        if (x, y) in seen:
            continue
        if not (0 <= x < rogue.MAP_W and 0 <= y < rogue.MAP_H):
            continue
        if tm[y][x] not in rogue.WALKABLE:
            continue
        seen.add((x, y))
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            stack.append((x + dx, y + dy))
    return seen


class RogueBaselineTest(unittest.TestCase):
    def assert_in_rogue_544_play_area(self, x, y):
        # Rogue 5.4.4 move.c: do_move() permits x=0..NUMCOLS-1 and y=1..NUMLINES-2.
        self.assertGreaterEqual(x, 0)
        self.assertLess(x, rogue.MAP_W)
        self.assertGreaterEqual(y, rogue.PLAY_Y_MIN)
        self.assertLessEqual(y, rogue.PLAY_Y_MAX)

    def test_rogue_544_screen_and_play_area_constants(self):
        # Rogue 5.4.4 rogue.h: NUMLINES=24, NUMCOLS=80, STATLINE=NUMLINES-1.
        # move.c: do_move() rejects y <= 0 and y >= NUMLINES - 1.
        self.assertEqual(rogue.MAP_W, 80)
        self.assertEqual(rogue.MAP_H, 24)
        self.assertEqual(rogue.STATLINE, 23)
        self.assertEqual((rogue.PLAY_Y_MIN, rogue.PLAY_Y_MAX), (1, 22))
        self.assertEqual(rogue.PLAY_H, 22)

    def test_rogue_544_room_sectors_use_numcols_and_numlines_thirds(self):
        # Rogue 5.4.4 rooms.c: bsze.x = NUMCOLS / 3; bsze.y = NUMLINES / 3.
        self.assertEqual((rogue.GRID_C, rogue.GRID_R), (3, 3))
        self.assertEqual((rogue.SEC_W, rogue.SEC_H), (80 // 3, 24 // 3))

        random.seed(2)
        _tm, rooms = rogue.DGen.gen(depth=1)
        sectors = [(room.cx // rogue.SEC_W, room.cy // rogue.SEC_H) for room in rooms]
        self.assertEqual(
            sectors,
            [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2)],
        )

    def test_rogue_544_generated_terrain_stays_in_play_area(self):
        terrain = {rogue.T_FLOOR, rogue.T_HWALL, rogue.T_VWALL, rogue.T_DOOR, rogue.T_CORR, rogue.T_STAIR, rogue.T_TRAP}
        for seed in range(30):
            random.seed(seed)
            tm, _rooms = rogue.DGen.gen(depth=20)
            for y, row in enumerate(tm):
                for x, tile in enumerate(row):
                    if tile in terrain:
                        self.assert_in_rogue_544_play_area(x, y)

    def test_rogue_544_level_entities_do_not_spawn_on_message_or_status_lines(self):
        for seed in range(30):
            game = new_game(seed=seed)
            self.assert_in_rogue_544_play_area(game.p.x, game.p.y)
            stairs = [
                (x, y)
                for y, row in enumerate(game.tm)
                for x, tile in enumerate(row)
                if tile == rogue.T_STAIR
            ]
            self.assertEqual(len(stairs), 1)
            for x, y in stairs:
                self.assert_in_rogue_544_play_area(x, y)
            for item in game.gitems:
                self.assert_in_rogue_544_play_area(item.x, item.y)
            for monster in game.mons:
                self.assert_in_rogue_544_play_area(monster.x, monster.y)
            for x, y in game.traps:
                self.assert_in_rogue_544_play_area(x, y)

    def test_rogue_544_stick_table_materials_and_names_audit(self):
        # Rogue 5.4.4 rogue.h:WS_*, extern.c:ws_info[], init.c:metal[]/wood[].
        import rogue_sticks

        self.assertEqual(rogue.CAT_STICK, "stick")
        self.assertEqual([s.name for s in rogue_sticks.STICKS], [
            "light", "invisibility", "lightning", "fire", "cold", "polymorph",
            "magic missile", "haste monster", "slow monster", "drain life",
            "nothing", "teleport away", "teleport to", "cancellation",
        ])
        self.assertEqual([s.prob for s in rogue_sticks.STICKS], [12, 6, 3, 3, 3, 15, 10, 10, 11, 9, 1, 6, 6, 5])
        self.assertEqual(rogue_sticks.METALS[:4], ["aluminum", "beryllium", "bone", "brass"])
        self.assertEqual(rogue_sticks.WOODS[:4], ["avocado wood", "balsa", "bamboo", "banyan"])

        ident = rogue.IdentTable()
        ident.wtypes[rogue_sticks.WS_LIGHT] = "wand"
        ident.wmades[rogue_sticks.WS_LIGHT] = "copper"
        stick = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_LIGHT, charges=12)
        self.assertEqual(ident.name(stick), "copper wand")
        ident.wk[rogue_sticks.WS_LIGHT] = True
        self.assertEqual(ident.name(stick), "wand of light [12 charges](copper)")

    def test_rogue_544_stick_generation_charges_and_fix_stick(self):
        # Rogue 5.4.4 things.c:new_thing() stick case and sticks.c:fix_stick().
        import rogue_sticks

        old_pick = rogue_sticks.pick_stick_kind
        try:
            rogue_sticks.pick_stick_kind = lambda rng: rogue_sticks.WS_LIGHT
            stick = rogue_sticks.make_stick(SequenceRng([4]))
            self.assertEqual(stick.kind, rogue_sticks.WS_LIGHT)
            self.assertEqual(stick.charges, 14)

            rogue_sticks.pick_stick_kind = lambda rng: rogue_sticks.WS_FIRE
            stick = rogue_sticks.make_stick(SequenceRng([2]))
            self.assertEqual(stick.charges, 5)
        finally:
            rogue_sticks.pick_stick_kind = old_pick

        self.assertEqual(rogue_sticks.stick_damage("staff"), ("2x3", "1x1"))
        self.assertEqual(rogue_sticks.stick_damage("wand"), ("1x1", "1x1"))

    def test_rogue_544_zap_light_consumes_charge_identifies_and_lights_room(self):
        # Rogue 5.4.4 sticks.c:do_zap() WS_LIGHT marks known, lights the room, then decrements charges.
        import rogue_sticks

        game = new_game(seed=201)
        dark = rogue.Room(5, 5, 8, 6, flags={rogue.ROOM_DARK})
        game.rooms = [dark]
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        rogue.DGen._room(game.tm, dark)
        game.p.x, game.p.y = 7, 7
        game.update_fov()
        stick = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_LIGHT, charges=1)
        game.p.inv.append(stick)

        game.zap_stick(stick, 1, 0)

        self.assertEqual(stick.charges, 0)
        self.assertTrue(game.ident.wk[rogue_sticks.WS_LIGHT])
        self.assertNotIn(rogue.ROOM_DARK, dark.flags)
        self.assertIn("the room is lit", game.msgs)

    def test_rogue_544_zap_invisibility_and_cancellation_monster_flags(self):
        # Rogue 5.4.4 sticks.c:do_zap() WS_INVIS sets ISINVIS; WS_CANCEL sets ISCANC and clears ISINVIS/CANHUH.
        import rogue_sticks

        game = new_game(seed=202)
        set_open_floor(game)
        medusa = monster_at(game.p.x + 2, game.p.y, sym="M", name="medusa", flags="confuse")
        game.mons = [medusa]

        invis = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_INVIS, charges=1)
        game.zap_stick(invis, 1, 0)

        self.assertEqual(invis.charges, 0)
        self.assertIn("invis", medusa.flags)
        self.assertFalse(medusa.running)

        cancel = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_CANCEL, charges=1)
        game.zap_stick(cancel, 1, 0)

        self.assertEqual(cancel.charges, 0)
        self.assertIn("cancel", medusa.flags)
        self.assertNotIn("invis", medusa.flags)
        self.assertNotIn("confuse", medusa.flags)

    def test_rogue_544_zap_polymorph_replaces_monster_type_with_rnd_26(self):
        # Rogue 5.4.4 sticks.c:do_zap() WS_POLYMORPH calls new_monster(tp, rnd(26)+'A', pos).
        import rogue_sticks

        game = new_game(seed=203)
        set_open_floor(game)
        monster = monster_at(game.p.x + 2, game.p.y, sym="H", name="hobgoblin")
        game.mons = [monster]
        old_rnd = rogue.RNG.rnd
        try:
            calls = []

            def fake_rnd(n):
                calls.append(n)
                return 3

            rogue.RNG.rnd = fake_rnd
            stick = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_POLYMORPH, charges=1)
            game.zap_stick(stick, 1, 0)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(calls[0], 26)
        self.assertEqual(stick.charges, 0)
        self.assertEqual((monster.sym, monster.name), ("D", "dragon"))
        self.assertEqual((monster.x, monster.y), (game.p.x + 2, game.p.y))
        self.assertFalse(monster.running)

    def test_rogue_544_zap_teleport_away_and_teleport_to_relocate_target(self):
        # Rogue 5.4.4 sticks.c:do_zap() WS_TELAWAY uses find_floor(!hero); WS_TELTO uses hero+delta.
        import rogue_sticks

        game = new_game(seed=204)
        set_open_floor(game)
        monster = monster_at(game.p.x + 3, game.p.y, sym="H", name="hobgoblin")
        game.mons = [monster]
        old_choice = rogue.RNG.choice
        try:
            rogue.RNG.choice = lambda seq: (game.p.x + 5, game.p.y + 4)
            away = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_TELAWAY, charges=1)
            game.zap_stick(away, 1, 0)
        finally:
            rogue.RNG.choice = old_choice

        self.assertEqual(away.charges, 0)
        self.assertEqual((monster.x, monster.y), (game.p.x + 5, game.p.y + 4))
        self.assertTrue(monster.running)

        monster.x, monster.y = game.p.x + 3, game.p.y
        monster.running = False
        to = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_TELTO, charges=1)
        game.zap_stick(to, 1, 0)

        self.assertEqual(to.charges, 0)
        self.assertEqual((monster.x, monster.y), (game.p.x + 1, game.p.y))
        self.assertTrue(monster.running)

    def test_rogue_544_monster_haste_and_slow_control_move_monst_frequency(self):
        # Rogue 5.4.4 chase.c:move_monst() checks ISSLOW/t_turn, then ISHASTE, then flips t_turn.
        game = new_game(seed=205)
        set_open_floor(game)
        monster = monster_at(game.p.x + 4, game.p.y)
        monster.running = True
        calls = []
        old_do_chase = game.do_chase
        try:
            game.do_chase = lambda m: calls.append((m.x, m.y)) or 0

            monster.flags.add("haste")
            game.m_turn(monster)
            self.assertEqual(len(calls), 2)
            self.assertFalse(monster.turn)

            calls.clear()
            monster.flags.discard("haste")
            monster.flags.add("slow")
            monster.turn = True
            game.m_turn(monster)
            game.m_turn(monster)
            game.m_turn(monster)
        finally:
            game.do_chase = old_do_chase

        self.assertEqual(len(calls), 2)
        self.assertFalse(monster.turn)

    def test_rogue_544_zap_haste_and_slow_monster_toggle_speed_flags(self):
        # Rogue 5.4.4 sticks.c:do_zap() WS_HASTE_M/WS_SLOW_M toggle ISHASTE/ISSLOW and runto().
        import rogue_sticks

        game = new_game(seed=205)
        set_open_floor(game)
        monster = monster_at(game.p.x + 2, game.p.y)
        monster.flags.add("slow")
        game.mons = [monster]

        haste = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_HASTE_M, charges=1)
        game.zap_stick(haste, 1, 0)

        self.assertEqual(haste.charges, 0)
        self.assertNotIn("slow", monster.flags)
        self.assertNotIn("haste", monster.flags)
        self.assertTrue(monster.running)

        haste = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_HASTE_M, charges=1)
        game.zap_stick(haste, 1, 0)

        self.assertIn("haste", monster.flags)
        self.assertNotIn("slow", monster.flags)

        slow = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_SLOW_M, charges=1)
        game.zap_stick(slow, 1, 0)

        self.assertEqual(slow.charges, 0)
        self.assertNotIn("haste", monster.flags)
        self.assertNotIn("slow", monster.flags)
        self.assertTrue(monster.turn)

        slow = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_SLOW_M, charges=1)
        game.zap_stick(slow, 1, 0)

        self.assertIn("slow", monster.flags)
        self.assertNotIn("haste", monster.flags)
        self.assertTrue(monster.turn)

    def test_rogue_544_cancelled_medusa_does_not_confuse_on_wake_monster(self):
        # Rogue 5.4.4 monsters.c:wake_monster() gates Medusa gaze with !ISCANC.
        game = new_game(seed=206)
        set_open_floor(game)
        medusa = monster_at(game.p.x + 1, game.p.y, "M", "medusa", flags="confuse")
        medusa.running = True
        medusa.flags.add("cancel")
        game.mons = [medusa]
        old_save = game.save_vs_magic
        try:
            game.save_vs_magic = lambda: False
            game.wake_monster(medusa)
        finally:
            game.save_vs_magic = old_save

        self.assertEqual(game.p.confused, 0)
        self.assertFalse(medusa.found)

    def test_rogue_544_cancelled_monsters_do_not_use_special_attack_or_regen(self):
        # Rogue 5.4.4 fight.c:attack() special switch is gated by !ISCANC; regen uses the same cancelled state.
        game = new_game(seed=207)
        set_open_floor(game)
        ice = monster_at(game.p.x + 1, game.p.y, "I", "ice monster", 10, 20, 100, "0x0", 5, "freeze,cancel")
        game.m_attack(ice)
        self.assertEqual(game.p.no_command, 0)

        troll = monster_at(game.p.x + 4, game.p.y, "T", "troll", hp=10, level=6, armor=4, damage="1x8", exp=120, flags="regen,cancel")
        troll.max_hp = 20
        troll.running = True
        old_random = rogue.RNG.random
        try:
            rogue.RNG.random = lambda: 0
            game.do_chase = lambda m: 0
            game.m_turn(troll)
        finally:
            rogue.RNG.random = old_random

        self.assertEqual(troll.hp, 10)

    def test_rogue_544_ring_table_and_stones_audit(self):
        # Rogue 5.4.4 extern.c:ring_info[], init.c:stones[] / init_stones().
        import rogue_rings

        self.assertEqual(rogue.CAT_RING, "ring")
        self.assertEqual([r.name for r in rogue_rings.RINGS], [
            "protection", "add strength", "sustain strength", "searching",
            "see invisible", "adornment", "aggravate monster", "dexterity",
            "increase damage", "regeneration", "slow digestion", "teleportation",
            "stealth", "maintain armor",
        ])
        self.assertEqual([r.prob for r in rogue_rings.RINGS], [9, 9, 5, 10, 10, 1, 10, 8, 8, 4, 9, 5, 7, 5])
        self.assertEqual(rogue_rings.STONES[:4], ["agate", "alexandrite", "amethyst", "carnelian"])
        self.assertEqual(rogue_rings.STONES[-2:], ["taaffeite", "zircon"])

        ident = rogue.IdentTable()
        ring = rogue.Item(rogue.CAT_RING, rogue_rings.R_PROTECT, ench=2)
        self.assertEqual(ident.name(ring), f"{ident.rstones[rogue_rings.R_PROTECT]} ring")
        ident.rk[rogue_rings.R_PROTECT] = True
        self.assertEqual(ident.name(ring), "ring of protection [+2]")

    def test_rogue_544_ring_generation_bonuses_and_curses(self):
        # Rogue 5.4.4 things.c:new_thing() ring case.
        import rogue_rings

        old_pick = rogue_rings.pick_ring_kind
        try:
            rogue_rings.pick_ring_kind = lambda rng: rogue_rings.R_PROTECT
            ring = rogue_rings.make_ring(SequenceRng([0]))
            self.assertEqual(ring.ench, -1)
            self.assertTrue(ring.cursed)

            ring = rogue_rings.make_ring(SequenceRng([2]))
            self.assertEqual(ring.ench, 2)
            self.assertFalse(ring.cursed)

            rogue_rings.pick_ring_kind = lambda rng: rogue_rings.R_TELEPORT
            ring = rogue_rings.make_ring(SequenceRng())
            self.assertTrue(ring.cursed)
        finally:
            rogue_rings.pick_ring_kind = old_pick

    def test_rogue_544_ring_slots_effects_and_cursed_remove(self):
        # Rogue 5.4.4 rings.c:ring_on/ring_off and things.c:dropcheck().
        import rogue_rings

        player = rogue.Player()
        add_str = rogue.Item(rogue.CAT_RING, rogue_rings.R_ADDSTR, ench=2)
        prot = rogue.Item(rogue.CAT_RING, rogue_rings.R_PROTECT, ench=1)
        player.arm = rogue.Item(rogue.CAT_ARM, 0, ench=1)
        player.recalc_ac()

        self.assertTrue(rogue_rings.put_on_ring(player, add_str, rogue_rings.LEFT))
        self.assertEqual(player.st, 18)
        self.assertEqual(player.max_st, 18)
        self.assertTrue(rogue_rings.put_on_ring(player, prot, rogue_rings.RIGHT))
        player.recalc_ac()
        self.assertEqual(player.ac, 6)

        add_str.cursed = True
        self.assertFalse(rogue_rings.remove_ring(player, add_str))
        self.assertIs(player.ring_l, add_str)
        add_str.cursed = False
        self.assertTrue(rogue_rings.remove_ring(player, add_str))
        self.assertEqual(player.st, 16)
        self.assertEqual(player.max_st, 16)
        self.assertIsNone(player.ring_l)

    def test_rogue_544_remove_curse_uncurses_equipped_rings(self):
        # Rogue 5.4.4 scrolls.c:S_REMOVE uncurses cur_ring[LEFT/RIGHT].
        import rogue_rings

        game = new_game(seed=10)
        scroll = rogue.Item(rogue.CAT_SCR, next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "remove curse"))
        ring = rogue.Item(rogue.CAT_RING, rogue_rings.R_TELEPORT, cursed=True)
        game.p.inv.extend([scroll, ring])
        game.put_on_ring(ring)

        game.use_scr(scroll)

        self.assertFalse(ring.cursed)

    def test_rogue_544_ring_food_consumption(self):
        # Rogue 5.4.4 rings.c:ring_eat() uses table and negative rnd gates.
        import rogue_rings

        regen = rogue.Item(rogue.CAT_RING, rogue_rings.R_REGEN)
        digest = rogue.Item(rogue.CAT_RING, rogue_rings.R_DIGEST)
        search = rogue.Item(rogue.CAT_RING, rogue_rings.R_SEARCH)
        self.assertEqual(rogue_rings.ring_eat(regen, SequenceRng()), 2)
        self.assertEqual(rogue_rings.ring_eat(digest, SequenceRng([0])), -1)
        self.assertEqual(rogue_rings.ring_eat(digest, SequenceRng([1])), 0)
        self.assertEqual(rogue_rings.ring_eat(search, SequenceRng([0])), 1)
        self.assertEqual(rogue_rings.ring_eat(search, SequenceRng([1])), 0)

        player = rogue.Player()
        player.ring_l = regen
        player.ring_r = digest
        player.food = 100
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 0
            player.hunger()
            self.assertEqual(player.food, 98)
        finally:
            rogue.RNG.rnd = old_rnd

        player.food = 0
        player.hp = 10
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 0
            player.hunger()
            self.assertEqual(player.food, -1)
        finally:
            rogue.RNG.rnd = old_rnd

    def test_rogue_544_ring_damage_hit_and_regeneration_effects(self):
        import rogue_rings

        game = new_game(seed=9)
        set_open_floor(game)
        dex = rogue.Item(rogue.CAT_RING, rogue_rings.R_ADDHIT, ench=2)
        dam = rogue.Item(rogue.CAT_RING, rogue_rings.R_ADDDAM, ench=3)
        game.p.ring_l = dex
        game.p.ring_r = dam

        damage, hplus, dplus = game.player_weapon_profile(game.p.wpn, thrown=False)
        self.assertEqual((damage, hplus, dplus), ("2d4", 3, 4))

        game.p.wpn = next(it for it in game.p.inv if it.cat == rogue.CAT_WPN and it.kind == 2)
        thrown = rogue.Item(rogue.CAT_WPN, 3, hit_plus=0, dam_plus=0)
        damage, hplus, dplus = game.player_weapon_profile(thrown, thrown=True)
        self.assertEqual((damage, hplus, dplus), ("2d3", 1, 0))

        game.p.hp = 1
        game.p.max_hp = 10
        game.p.ring_l = rogue.Item(rogue.CAT_RING, rogue_rings.R_REGEN)
        old_randint = rogue.RNG.randint
        try:
            rogue.RNG.randint = lambda a, b: a
            game.p.heal_tick()
            self.assertEqual(game.p.hp, 2)
        finally:
            rogue.RNG.randint = old_randint

    def test_rogue_544_ring_searching_auto_searches_after_turn_without_extra_turn(self):
        # Rogue 5.4.4 command.c: after a turn, each R_SEARCH ring calls search().
        import rogue_rings

        game = new_game(seed=204)
        set_open_floor(game)
        game.p.ring_l = rogue.Item(rogue.CAT_RING, rogue_rings.R_SEARCH)
        px, py = game.p.x, game.p.y
        game.hidden_tiles[(px + 1, py)] = rogue.T_DOOR
        game.tm[py][px + 1] = rogue.T_VWALL
        old_randrange = rogue.random.randrange
        try:
            rogue.random.randrange = lambda n: 0
            game.end_turn()
        finally:
            rogue.random.randrange = old_randrange

        self.assertEqual(game.turn, 1)
        self.assertEqual(game.tm[py][px + 1], rogue.T_DOOR)
        self.assertIn("You found something!", game.msgs)

    def test_rogue_544_ring_teleportation_rolls_after_turn(self):
        # Rogue 5.4.4 command.c: R_TELEPORT teleports on rnd(50) == 0 after a turn.
        import rogue_rings

        game = new_game(seed=205)
        set_open_floor(game)
        game.p.ring_l = rogue.Item(rogue.CAT_RING, rogue_rings.R_TELEPORT)
        old_pos = (game.p.x, game.p.y)
        old_randrange = rogue.random.randrange
        old_choice = rogue.random.choice
        try:
            rogue.random.randrange = lambda n: 0
            rogue.random.choice = lambda seq: seq[0]
            game.end_turn()
        finally:
            rogue.random.randrange = old_randrange
            rogue.random.choice = old_choice

        self.assertEqual(game.turn, 1)
        self.assertNotEqual((game.p.x, game.p.y), old_pos)

    def test_rogue_544_ring_see_invisible_reveals_phantom_in_view(self):
        # Rogue 5.4.4 rings.c:ring_on() calls invis_on(); display honors CANSEE.
        import rogue_rings

        game = new_game(seed=206)
        set_open_floor(game)
        phantom = monster_at(game.p.x + 1, game.p.y, "P", "phantom", flags="invis")
        game.mons = [phantom]
        game.visible.add((phantom.x, phantom.y))

        self.assertFalse(game.can_see_monster(phantom))
        game.p.ring_l = rogue.Item(rogue.CAT_RING, rogue_rings.R_SEEINVIS)
        self.assertTrue(game.can_see_monster(phantom))

    def test_rogue_544_ring_aggravate_and_stealth_affect_monster_running(self):
        # Rogue 5.4.4 rings.c:ring_on() aggravates; monsters.c:wake_monster checks R_STEALTH.
        import rogue_rings

        game = new_game(seed=207)
        set_open_floor(game)
        first = monster_at(game.p.x + 1, game.p.y)
        second = monster_at(game.p.x + 2, game.p.y)
        game.mons = [first, second]

        game.put_on_ring(rogue.Item(rogue.CAT_RING, rogue_rings.R_AGGR))
        self.assertTrue(first.running)
        self.assertTrue(second.running)
        self.assertFalse(game.ident.rk[rogue_rings.R_AGGR])

        game = new_game(seed=208)
        set_open_floor(game)
        monster = monster_at(game.p.x + 1, game.p.y)
        game.mons = [monster]
        game.p.ring_l = rogue.Item(rogue.CAT_RING, rogue_rings.R_STEALTH)
        old_randrange = rogue.random.randrange
        try:
            rogue.random.randrange = lambda n: 1
            game.wake_monster(monster)
        finally:
            rogue.random.randrange = old_randrange
        self.assertFalse(monster.running)

    def test_rogue_544_ring_sustain_strength_blocks_poison_strength_loss(self):
        # Rogue 5.4.4 fight.c/move.c/potions.c check R_SUSTSTR before chg_str(-1).
        import rogue_rings

        game = new_game(seed=209)
        set_open_floor(game)
        game.p.ring_l = rogue.Item(rogue.CAT_RING, rogue_rings.R_SUSTSTR)
        game.p.st = 10
        snake = monster_at(game.p.x + 1, game.p.y, "R", "rattlesnake", 10, 20, 100, "0x0", 5, "poison")
        old_randrange = rogue.random.randrange
        try:
            rogue.random.randrange = lambda n: 19
            game.m_attack(snake)
        finally:
            rogue.random.randrange = old_randrange
        self.assertEqual(game.p.st, 10)

        poison = next(i for i, spec in enumerate(rogue.POTIONS) if spec["name"] == "poison")
        potion = rogue.Item(rogue.CAT_POT, poison)
        game.p.inv.append(potion)
        game.use_pot(potion)
        self.assertEqual(game.p.st, 10)
        self.assertIn("you feel momentarily sick", game.msgs)

        dart_x, dart_y = game.p.x, game.p.y
        game.traps[(dart_x, dart_y)] = 5
        old_randrange = rogue.random.randrange
        try:
            rogue.random.randrange = lambda n: 19
            game.trigger_trap(dart_x, dart_y)
        finally:
            rogue.random.randrange = old_randrange
        self.assertEqual(game.p.st, 10)

    def test_rogue_544_ring_maintain_armor_blocks_rust_and_adornment_stays_unidentified(self):
        # Rogue 5.4.4 move.c:rust_armor() checks R_SUSTARM; R_NOP has no wear-time effect.
        import rogue_rings

        game = new_game(seed=210)
        armor = rogue.Item(rogue.CAT_ARM, 1, ench=0)
        game.p.arm = armor
        game.p.ring_l = rogue.Item(rogue.CAT_RING, rogue_rings.R_SUSTARM)
        game.p.recalc_ac()

        game.rust_armor()

        self.assertEqual(armor.ench, 0)
        self.assertIn("the rust vanishes instantly", game.msgs)

        game = new_game(seed=211)
        adornment = rogue.Item(rogue.CAT_RING, rogue_rings.R_NOP)
        game.p.inv.append(adornment)
        game.put_on_ring(adornment)

        self.assertFalse(game.ident.rk[rogue_rings.R_NOP])

    def test_full_map_layout_baseline(self):
        self.assertEqual((rogue.SCR_W, rogue.SCR_H), (576, 360))
        self.assertEqual((rogue.ZV_COLS, rogue.ZV_ROWS), (rogue.MAP_W, rogue.PLAY_H))
        self.assertEqual((rogue.ZV_PX_W, rogue.ZV_PX_H), (480, 264))
        self.assertEqual(rogue.HUD_W, 78)
        self.assertEqual(rogue.MSG_LINES, 7)
        self.assertEqual(rogue.AUX_ACTIONS, ["Inventory", "Help", "Search", "Trap", "Pickup", "Language"])

        game = new_game(seed=5)
        game.cam_x = 99
        game.cam_y = 99
        game.update_cam()
        self.assertEqual((game.cam_x, game.cam_y), (0, rogue.PLAY_Y_MIN))

    def test_hud_equipment_names_are_short_for_compact_16_10_layout(self):
        game = new_game(seed=5)

        sword = rogue.Item(rogue.CAT_WPN, 5, hit_plus=1, dam_plus=1)
        plate = rogue.Item(rogue.CAT_ARM, 7, ench=2)
        self.assertEqual(rogue.TextCatalog.hud_item_kind(rogue.LANG_EN, rogue.CAT_WPN, "two-handed sword"), "2H sw")
        self.assertEqual(rogue.TextCatalog.hud_item_kind(rogue.LANG_JA, rogue.CAT_WPN, "two-handed sword"), "両手剣")
        self.assertEqual(rogue.TextCatalog.hud_item_kind(rogue.LANG_EN, rogue.CAT_ARM, "plate mail"), "plate")
        self.assertEqual(rogue.TextCatalog.hud_item_kind(rogue.LANG_JA, rogue.CAT_ARM, "plate mail"), "鋼鉄")
        self.assertEqual(game.hud_equip_name(sword), "+1,+1 2H sw")
        self.assertEqual(game.hud_equip_name(plate), "+2 plate")

        game.lang = rogue.LANG_JA
        self.assertEqual(game.hud_equip_name(sword), "+1,+1 両手剣")
        self.assertEqual(game.hud_equip_name(plate), "+2 鋼鉄")

    def test_compact_hud_draw_text_stays_inside_screen(self):
        game = new_game(seed=5)
        game.p.wpn = rogue.Item(rogue.CAT_WPN, 5, hit_plus=1, dam_plus=1)
        game.p.arm = rogue.Item(rogue.CAT_ARM, 7, ench=2)
        drawn = []
        game.txt = lambda x, y, s, c: drawn.append((x, y, str(s)))

        game.draw_title()
        game.draw_stat()

        for x, _y, text in drawn:
            self.assertLessEqual(x + len(text) * 6, rogue.SCR_W)

    def test_rogue2_official_message_reference_data_is_checked_in(self):
        ref_dir = os.path.join(ROOT, "vendor", "rogue2_official_messages")
        expected = ["COPYING", "README.md", "mesg_E", "mesg_J"]
        for name in expected:
            self.assertTrue(os.path.exists(os.path.join(ref_dir, name)), name)

        with open(os.path.join(ref_dir, "README.md"), encoding="utf-8") as f:
            readme = f.read()
        self.assertIn("https://github.com/suzukiiichiro/Rogue2.Official", readme)
        self.assertIn("334315ea068e7ae8605ff9be5d6e04b0658cd330", readme)
        self.assertIn("reference only", readme)

        with open(os.path.join(ref_dir, "COPYING"), encoding="utf-8") as f:
            self.assertIn("使用許諾書", f.read())
        with open(os.path.join(ref_dir, "mesg_E"), encoding="utf-8") as f:
            self.assertIn('"Message English version"', f.read())
        with open(os.path.join(ref_dir, "mesg_J"), encoding="utf-8") as f:
            self.assertIn('"Message Japanese version', f.read())

    def test_module_loads_and_new_game_emits_welcome(self):
        game = new_game(seed=7)
        self.assertEqual(game.p.depth, 1)
        self.assertEqual(game.st, rogue.ST_PLAY)
        self.assertEqual(game.msgs[-1], "Welcome to the Dungeons of Doom!")

    def test_initial_inventory_baseline(self):
        inv, weapon, armor = rogue.start_inv()
        self.assertEqual(len(inv), 5)
        self.assertIs(weapon, inv[0])
        self.assertIs(armor, inv[1])
        self.assertEqual(weapon.cat, rogue.CAT_WPN)
        self.assertEqual(weapon.data["name"], "mace")
        self.assertEqual(weapon.hit_plus, 1)
        self.assertEqual(weapon.dam_plus, 1)
        self.assertEqual(inv[2].data["name"], "arrow")
        self.assertEqual(inv[2].hit_plus, 0)
        self.assertEqual(inv[2].dam_plus, 0)
        self.assertEqual(inv[2].qty, 25)
        self.assertEqual(inv[3].data["name"], "short bow")
        self.assertEqual(inv[3].hit_plus, 1)
        self.assertEqual(inv[3].dam_plus, 0)
        self.assertEqual(armor.cat, rogue.CAT_ARM)
        self.assertEqual(armor.data["name"], "leather armor")
        self.assertEqual(armor.ench, 1)

    def test_v5_item_names_plural_food_and_armor_protection(self):
        game = new_game(seed=8)
        food = rogue.Item(rogue.CAT_FOOD, 0, qty=2)
        self.assertEqual(game.item_name(food), "2 food rations")

        armor = rogue.Item(rogue.CAT_ARM, 1, ench=1)
        self.assertEqual(game.item_name(armor), "+1 ring mail [protection 4]")

        game.p.arm = armor
        self.assertEqual(game.item_name(armor), "+1 ring mail [protection 4] (being worn)")
        self.assertEqual(game.equip_name(armor), "+1 ring mail [protection 4]")

    def test_rogue_544_monster_table_audit_guards_named_fields(self):
        specs = {m.sym: m for m in rogue.BESTIARY}
        self.assertEqual(
            (specs["H"].name, specs["H"].level, specs["H"].armor, specs["H"].damage, specs["H"].exp),
            ("hobgoblin", 1, 5, "1x8", 3),
        )
        self.assertEqual(
            (specs["I"].name, specs["I"].level, specs["I"].armor, specs["I"].damage, specs["I"].exp),
            ("ice monster", 1, 9, "0x0", 5),
        )
        self.assertEqual(
            (specs["C"].name, specs["C"].level, specs["C"].armor, specs["C"].damage, specs["C"].exp),
            ("centaur", 4, 4, "1x2/1x5/1x5", 17),
        )

    def test_rogue_544_weapon_table_audit_guards_init_dam_values(self):
        self.assertEqual(rogue.WEAPONS[0]["damage"], "2d4")
        self.assertEqual(rogue.WEAPONS[0]["hurl_damage"], "1d3")
        self.assertEqual(rogue.WEAPONS[3]["damage"], "1d1")
        self.assertEqual(rogue.WEAPONS[3]["hurl_damage"], "2d3")
        self.assertEqual(rogue.WEAPONS[3]["launcher"], 2)
        self.assertTrue(rogue.WEAPONS[3]["missile"])

    def test_rogue_544_swing_thresholds_guard_combat_balance(self):
        game = new_game(seed=8)

        def hits(attacker_level, defender_armor, hit_plus=0):
            old_randrange = rogue.random.randrange
            try:
                total = 0
                for result in range(20):
                    rogue.random.randrange = lambda n, result=result: result
                    total += int(game.swing_hits(attacker_level, defender_armor, hit_plus))
                return total
            finally:
                rogue.random.randrange = old_randrange

        self.assertEqual(hits(attacker_level=1, defender_armor=3), 4)
        self.assertEqual(hits(attacker_level=1, defender_armor=7), 8)
        self.assertEqual(hits(attacker_level=1, defender_armor=5, hit_plus=1), 7)

    def test_rogue_544_damage_expr_parser_handles_monster_attacks(self):
        old_randrange = rogue.RNG.randrange
        try:
            rogue.RNG.randrange = lambda n: n - 1
            self.assertEqual(rogue.roll_damage_expr("1x8"), 8)
            self.assertEqual(rogue.roll_damage_expr("1x2/1x5/1x5"), 12)
            self.assertEqual(rogue.roll_damage_expr("0x0"), 0)
        finally:
            rogue.RNG.randrange = old_randrange

    def test_weapon_names_use_rogue_54_hit_and_damage_pluses(self):
        ident = rogue.IdentTable()
        mace = rogue.Item(rogue.CAT_WPN, 0, hit_plus=1, dam_plus=1)
        bow = rogue.Item(rogue.CAT_WPN, 2, hit_plus=1, dam_plus=0)
        arrows = rogue.Item(rogue.CAT_WPN, 3, hit_plus=0, dam_plus=0, qty=25)
        self.assertEqual(ident.name(mace, rogue.LANG_EN), "+1,+1 mace")
        self.assertEqual(ident.name(bow, rogue.LANG_EN), "+1,+0 short bow")
        self.assertEqual(ident.name(arrows, rogue.LANG_EN), "25 +0,+0 arrows")

        game = new_game(seed=7)
        self.assertEqual(game.item_name(game.p.wpn), "+1,+1 mace (weapon in hand)")

    def test_melee_combat_messages_omit_damage_numbers_for_v5_style(self):
        game = new_game(seed=9)
        set_open_floor(game)
        monster = monster_at(game.p.x + 1, game.p.y, hp=20, armor=100, exp=0)
        game.mons = [monster]

        game.p_attack(monster)

        self.assertTrue(any("you hit the hobgoblin" in m.lower() for m in game.msgs))
        self.assertFalse(any("(" in m and "dmg" not in m.lower() for m in game.msgs))

        game.msgs = []
        monster.armor = -100
        game.p_attack(monster)
        self.assertTrue(any("you miss the hobgoblin" in m.lower() for m in game.msgs))

    def test_dungeon_stair_is_reachable(self):
        random.seed(11)
        tm, rooms = rogue.DGen.gen(depth=1)
        start = (rooms[0].cx, rooms[0].cy)
        seen = reachable_tiles(tm, start)
        stairs = [
            (x, y)
            for y, row in enumerate(tm)
            for x, tile in enumerate(row)
            if tile == rogue.T_STAIR
        ]
        self.assertEqual(stairs, [])

        game = new_game(seed=11)
        start = (game.p.x, game.p.y)
        seen = reachable_tiles(game.tm, start)
        stairs = [
            (x, y)
            for y, row in enumerate(game.tm)
            for x, tile in enumerate(row)
            if tile == rogue.T_STAIR
        ]
        self.assertEqual(len(stairs), 1)
        self.assertIn(stairs[0], seen)

    def test_v5_dungeon_generation_can_create_dark_and_maze_rooms(self):
        dark_seen = False
        maze_seen = False
        for seed in range(400):
            random.seed(seed)
            _tm, rooms = rogue.DGen.gen(depth=20)
            dark_seen = dark_seen or any(getattr(room, "is_dark", False) for room in rooms)
            maze_seen = maze_seen or any(getattr(room, "is_maze", False) for room in rooms)
            if dark_seen and maze_seen:
                break

        self.assertTrue(dark_seen)
        self.assertTrue(maze_seen)

    def test_rogue544_rooms_keep_fixed_sector_order(self):
        random.seed(2)
        _tm, rooms = rogue.DGen.gen(depth=1)

        sectors = [(room.cx // rogue.SEC_W, room.cy // rogue.SEC_H) for room in rooms]

        self.assertEqual(
            sectors,
            [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2)],
        )

    def test_rogue544_passage_graph_uses_spanning_tree_plus_extra_edges(self):
        random.seed(8)
        edges = rogue.DGen._passage_edges()

        self.assertGreaterEqual(len(edges), rogue.GRID_C * rogue.GRID_R - 1)
        self.assertLessEqual(len(edges), rogue.GRID_C * rogue.GRID_R - 1 + 4)
        self.assertEqual(len(edges), len(set(tuple(sorted(edge)) for edge in edges)))
        self.assertNotEqual(len(edges), 12)

        seen = {0}
        changed = True
        while changed:
            changed = False
            for a, b in edges:
                if a in seen and b not in seen:
                    seen.add(b)
                    changed = True
                elif b in seen and a not in seen:
                    seen.add(a)
                    changed = True
        self.assertEqual(seen, set(range(rogue.GRID_C * rogue.GRID_R)))

    def test_rogue544_generated_gone_rooms_are_single_passage_points(self):
        random.seed(0)
        _tm, rooms = rogue.DGen.gen(depth=1)
        gone_rooms = [room for room in rooms if room.is_gone]

        self.assertTrue(gone_rooms)
        self.assertTrue(all((room.w, room.h) == (1, 1) for room in gone_rooms))

    def test_dark_room_visibility_stays_local_until_lit(self):
        game = new_game(seed=12)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        dark = rogue.Room(5, 5, 8, 6, flags={rogue.ROOM_DARK})
        game.rooms = [dark]
        rogue.DGen._room(game.tm, dark)
        game.p.x, game.p.y = 7, 7

        game.update_fov()

        self.assertIn((7, 7), game.visible)
        self.assertIn((8, 7), game.visible)
        self.assertNotIn((11, 9), game.visible)

    def test_gone_rooms_connect_as_passage_without_wall_doors(self):
        gone = rogue.Room(2, 2, 8, 5, flags={rogue.ROOM_GONE})
        normal = rogue.Room(18, 2, 8, 5)
        tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        rogue.DGen._room(tm, gone)
        rogue.DGen._room(tm, normal)

        rogue.DGen._conn(tm, gone, normal, True)

        self.assertEqual(tm[gone.cy][gone.x + gone.w - 1], rogue.T_CORR)
        self.assertNotEqual(tm[gone.cy][gone.x + gone.w - 1], rogue.T_DOOR)

    def test_gone_room_visibility_behaves_like_corridor(self):
        game = new_game(seed=13)
        gone = rogue.Room(5, 5, 8, 6, flags={rogue.ROOM_GONE})
        game.rooms = [gone]
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        game.tm[7][7] = rogue.T_CORR
        game.p.x, game.p.y = 7, 7

        game.update_fov()

        self.assertIn((7, 7), game.visible)
        self.assertNotIn((11, 9), game.visible)

    def test_room_passage_does_not_turn_along_horizontal_wall_row(self):
        top = rogue.Room(18, 2, 8, 5)
        bottom = rogue.Room(18, 14, 8, 5)
        tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        rogue.DGen._room(tm, top)
        rogue.DGen._room(tm, bottom)
        old_randint = rogue.random.randint
        try:
            rogue.random.randint = lambda a, b: a
            rogue.DGen._conn(tm, top, bottom, False)
        finally:
            rogue.random.randint = old_randint

        wall_adjacent_y = top.y + top.h
        doorway_x = next(x for x in range(top.x, top.x + top.w) if tm[wall_adjacent_y][x] == rogue.T_CORR)
        wall_hugging = [
            x for x in range(rogue.MAP_W)
            if x != doorway_x and tm[wall_adjacent_y][x] == rogue.T_CORR
        ]
        self.assertEqual(wall_hugging, [])

    def test_rogue_544_amulet_spawns_on_depth_26(self):
        game = new_game(seed=260)
        game.p.depth = 25

        game.descend()

        amulets = [item for item in game.gitems if item.cat == rogue.CAT_AMULET]
        self.assertEqual(game.p.depth, 26)
        self.assertEqual(len(amulets), 1)
        self.assertEqual(amulets[0].data["name"], "Amulet of Yendor")

    def test_amulet_pickup_allows_depth_1_stair_victory(self):
        game = new_game(seed=261)
        set_open_floor(game)
        amulet = rogue.Item(rogue.CAT_AMULET, 0)
        amulet.x, amulet.y = game.p.x, game.p.y
        game.gitems = [amulet]

        game.do_pickup()

        self.assertTrue(game.p.has_amulet)
        self.assertIn(amulet, game.p.inv)

        game.p.depth = 1
        game.tm[game.p.y][game.p.x] = rogue.T_STAIR
        game.do_action()

        self.assertEqual(game.st, rogue.ST_WIN)
        self.assertIn("You escaped with the Amulet of Yendor!", game.msgs)

    def test_ident_table_names_in_both_languages(self):
        random.seed(3)
        ident = rogue.IdentTable()
        items = [
            rogue.Item(rogue.CAT_POT, 0),
            rogue.Item(rogue.CAT_SCR, 0),
            rogue.Item(rogue.CAT_FOOD, 1),
            rogue.Item(rogue.CAT_WPN, 0, ench=1),
            rogue.Item(rogue.CAT_ARM, 0, ench=1),
        ]
        for item in items:
            self.assertTrue(ident.name(item, rogue.LANG_EN))
            self.assertTrue(ident.name(item, rogue.LANG_JA))

    def test_language_switch_changes_text_not_generated_state(self):
        en = new_game(seed=23, lang=rogue.LANG_EN)
        ja = new_game(seed=23, lang=rogue.LANG_JA)
        self.assertNotEqual(en.msgs[-1], ja.msgs[-1])
        self.assertEqual((en.p.x, en.p.y, en.p.depth), (ja.p.x, ja.p.y, ja.p.depth))
        self.assertEqual(len(en.rooms), len(ja.rooms))
        self.assertEqual(len(en.mons), len(ja.mons))
        self.assertEqual(len(en.gitems), len(ja.gitems))

    def test_assist_language_toggle_changes_display_layer_only(self):
        game = new_game(seed=24, lang=rogue.LANG_EN)
        before = (
            game.turn,
            game.p.x,
            game.p.y,
            len(game.p.inv),
            len(game.mons),
            len(game.gitems),
            tuple(game.ident.pk),
            tuple(game.ident.sk),
        )

        game.st = rogue.ST_AUX
        game.acur = rogue.AUX_ACTIONS.index("Language")
        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_A},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_A},
        )
        game.update()
        self.assertEqual(game.lang, rogue.LANG_JA)
        self.assertEqual(game.ident.lang, rogue.LANG_JA)
        self.assertEqual(game.st, rogue.ST_PLAY)
        self.assertIn("言語: 日本語。", game.msgs)
        self.assertEqual(
            before,
            (
                game.turn,
                game.p.x,
                game.p.y,
                len(game.p.inv),
                len(game.mons),
                len(game.gitems),
                tuple(game.ident.pk),
                tuple(game.ident.sk),
            ),
        )
        self.assertEqual(rogue.TextCatalog.menu(game.lang, "Language"), "言語")

        rogue.pyxel.set_input()
        game.st = rogue.ST_AUX
        game.acur = rogue.AUX_ACTIONS.index("Language")
        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_A},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_A},
        )
        game.update()
        self.assertEqual(game.lang, rogue.LANG_EN)
        self.assertEqual(game.ident.lang, rogue.LANG_EN)
        self.assertIn("Language: English.", game.msgs)

    def test_baseline_hunger_heal_and_pickup(self):
        game = new_game(seed=31)
        game.p.food = rogue.MORETIME * 2
        game.end_turn()
        self.assertEqual(game.p.state, "hungry")
        self.assertIn("You feel hungry.", game.msgs)

        game.p.hp = 10
        game.p.quiet = 19
        game.p.food = rogue.HUNGERTIME
        game.p.heal_tick()
        self.assertEqual(game.p.hp, 11)
        self.assertEqual(game.p.quiet, 0)

        gold = rogue.Item(rogue.CAT_GOLD, 0)
        gold.qty = 42
        gold.x = game.p.x
        gold.y = game.p.y
        game.gitems.append(gold)
        game.do_pickup()
        self.assertEqual(game.p.gold, 42)
        self.assertNotIn(gold, game.gitems)
        self.assertIn("42 gold pieces", game.msgs)

    def test_manual_pickup_and_stairs_spend_a_turn(self):
        game = new_game(seed=310)
        set_open_floor(game)
        item = rogue.Item(rogue.CAT_FOOD, 0)
        item.x, item.y = game.p.x, game.p.y
        game.gitems = [item]

        game.do_action()

        self.assertEqual(game.turn, 1)
        self.assertNotIn(item, game.gitems)
        self.assertTrue(any(i.cat == rogue.CAT_FOOD and i.kind == 0 and i.qty == 2 for i in game.p.inv))

        game = new_game(seed=311)
        set_open_floor(game)
        game.tm[game.p.y][game.p.x] = rogue.T_STAIR
        old_depth = game.p.depth

        game.do_action()

        self.assertEqual(game.turn, 1)
        self.assertEqual(game.p.depth, old_depth + 1)

    def test_auto_pickup_can_be_toggled_and_manual_pickup_still_works(self):
        game = new_game(seed=32)
        game.mons = []
        x, y = game.p.x + 1, game.p.y
        if not game.walkable(x, y):
            x, y = game.p.x - 1, game.p.y
        dx, dy = x - game.p.x, y - game.p.y
        item = rogue.Item(rogue.CAT_FOOD, 0)
        item.x, item.y = x, y
        game.gitems = [item]
        self.assertTrue(game.auto_pickup)

        game.try_move(dx, dy)
        self.assertTrue(any(i.cat == rogue.CAT_FOOD and i.kind == 0 and i.qty == 2 for i in game.p.inv))
        self.assertNotIn(item, game.gitems)
        self.assertTrue(item.picked_up)

        game = new_game(seed=32)
        game.mons = []
        x, y = game.p.x + 1, game.p.y
        if not game.walkable(x, y):
            x, y = game.p.x - 1, game.p.y
        dx, dy = x - game.p.x, y - game.p.y
        item = rogue.Item(rogue.CAT_FOOD, 0)
        item.x, item.y = x, y
        game.gitems = [item]
        game.auto_pickup = False
        game.try_move(dx, dy)
        self.assertNotIn(item, game.p.inv)
        self.assertIn(item, game.gitems)
        game.do_pickup()
        self.assertTrue(any(i.cat == rogue.CAT_FOOD and i.kind == 0 and i.qty == 2 for i in game.p.inv))
        self.assertNotIn(item, game.gitems)

    def test_pickup_pack_full_and_scare_monster_dust(self):
        game = new_game(seed=33)
        game.gitems = []
        game.p.inv = [rogue.Item(rogue.CAT_FOOD, 0) for _ in range(rogue.INV_MAX)]
        item = rogue.Item(rogue.CAT_FOOD, 1)
        item.x, item.y = game.p.x, game.p.y
        game.gitems.append(item)
        game.do_pickup()
        self.assertIn(item, game.gitems)
        self.assertIn("pack too full", game.msgs)

        game.p.inv = []
        scare_kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "scare monster")
        scroll = rogue.Item(rogue.CAT_SCR, scare_kind)
        scroll.picked_up = True
        scroll.x, scroll.y = game.p.x, game.p.y
        game.gitems = [scroll]
        game.do_pickup()
        self.assertNotIn(scroll, game.gitems)
        self.assertNotIn(scroll, game.p.inv)
        self.assertIn("the scroll turns to dust as you pick it up", game.msgs)

    def test_explored_items_remain_drawn_but_monsters_do_not(self):
        game = new_game(seed=34)
        calls = []
        game.txt = lambda x, y, s, c: calls.append(str(s))
        game.visible = set()
        game.explored = {(game.p.x, game.p.y)}
        item = rogue.Item(rogue.CAT_POT, 0)
        item.x, item.y = game.p.x, game.p.y
        game.gitems = [item]
        game.mons = [monster_at(game.p.x, game.p.y, "Z", "zombie", 1, 2, 8, "1x8", 6)]
        game.draw_zoom()
        self.assertIn(item.sym, calls)
        self.assertNotIn("Z", calls)

    def test_dark_room_explored_floor_is_not_drawn_after_leaving_lamp_area(self):
        # Rogue 5.4.4 misc.c:erase_lamp()/rooms.c:leave_room() erase dark room FLOOR.
        game = new_game(seed=341)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        dark = rogue.Room(5, 5, 8, 6, flags={rogue.ROOM_DARK})
        game.rooms = [dark]
        rogue.DGen._room(game.tm, dark)
        game.visible = set()
        game.explored = {(7, 7)}
        game.p.x, game.p.y = 20, 20
        calls = []
        game.txt = lambda x, y, s, c: calls.append(str(s))

        game.draw_zoom()

        self.assertNotIn(".", calls)

    def test_hud_title_includes_build_revision_stamp(self):
        game = new_game(seed=342)
        calls = []
        game.txt = lambda x, y, s, c: calls.append(str(s))

        game.draw_title()

        self.assertIn("Rogue V5", calls)
        self.assertIn(rogue.UI_BUILD, calls)
        self.assertRegex(rogue.UI_BUILD, r"^\d{10}$")
        self.assertEqual(rogue.UI_BUILD, "2604191530")

    def test_hp_damage_bar_persists_for_current_turn_instead_of_frame_timer(self):
        game = new_game(seed=343)
        game.txt = lambda *args: None
        rects = []
        old_rect = rogue.pyxel.rect
        try:
            rogue.pyxel.rect = lambda *args: rects.append(args)
            game.p.max_hp = 20
            game.p.hp = 20
            game.draw_stat()
            game.p.hp = 12
            rects.clear()

            game.draw_stat()
            first_count = len(rects)
            rects.clear()
            game.draw_stat()
            second_count = len(rects)

            self.assertEqual(first_count, second_count)
            self.assertEqual(game.hp_damage_turn, game.turn)
            self.assertEqual(game.hp_damage_from, 20)
            game.turn += 1
            rects.clear()
            game.draw_stat()
            self.assertEqual(len(rects), 2)
        finally:
            rogue.pyxel.rect = old_rect

    def test_inventory_overlay_and_hud_show_v5_exp_and_trimmed_mode_labels(self):
        game = new_game(seed=35)
        calls = []
        game.txt = lambda x, y, s, c: calls.append(str(s))
        game.draw_stat()
        game.draw_inventory()
        self.assertTrue(any("Lv 1 Exp 0" in c for c in calls))
        self.assertFalse(any("Exp 0/10" in c for c in calls))
        self.assertFalse(any("Exp:   0/10" in c for c in calls))
        self.assertTrue(any(c.startswith("Arm ") for c in calls))
        self.assertFalse(any(c.startswith("Armor:") for c in calls))
        self.assertFalse(any("Food normal" in c for c in calls))
        self.assertFalse(any("Diag OFF" in c for c in calls))
        self.assertFalse(any("Pickup ON" in c for c in calls))
        self.assertFalse(any("Lang EN" in c for c in calls))

        game.diag_assist = True
        game.auto_pickup = False
        calls.clear()
        game.draw_stat()
        self.assertTrue(any("Diag ON" in c for c in calls))
        self.assertTrue(any("Pickup OFF" in c for c in calls))

    def test_inventory_overlay_lists_pack_without_status_or_equipment_sections(self):
        game = new_game(seed=35)
        game.p.inv = [
            rogue.Item(rogue.CAT_SCR, 0),
            rogue.Item(rogue.CAT_WPN, 5),
        ] + [rogue.Item(rogue.CAT_FOOD, 0) for _ in range(rogue.INV_MAX - 2)]
        calls = []
        game.txt = lambda x, y, s, c: calls.append((x, y, str(s), c))

        game.draw_inventory()

        text = [s for _, _, s, _ in calls]
        self.assertIn("=== Inventory ===", text)
        self.assertNotIn("-- Equip --", text)
        self.assertFalse(any(s.startswith(("Depth", "Turn", "HP ", "Lv ", "Str ", "Arm ", "Gold", "Food")) for s in text))

        inv_lines = [c for c in calls if len(c[2]) >= 3 and c[2][1:3] == ") "]
        self.assertTrue(any(s.startswith("a) scroll ") and len(s) > 18 for _, _, s, _ in inv_lines))
        self.assertTrue(any(s.startswith("b) ") and "two-handed sword" in s for _, _, s, _ in inv_lines))
        self.assertTrue(any(s.startswith("z)") for _, _, s, _ in inv_lines))
        self.assertEqual({x for x, _, _, _ in inv_lines}, {38})
        first_item = next(c for c in inv_lines if c[2].startswith("a)"))
        last_item = next(c for c in inv_lines if c[2].startswith("z)"))
        self.assertEqual(first_item[1] - calls[0][1], 15)
        self.assertLessEqual(last_item[1], 275)

    def test_hud_equipment_omits_inventory_worn_annotations(self):
        game = new_game(seed=36)
        calls = []
        game.txt = lambda x, y, s, c: calls.append(str(s))

        game.draw_stat()

        equip_lines = [c for c in calls if c.startswith("W ") or c.startswith("A ")]
        self.assertTrue(equip_lines)
        self.assertFalse(any("(weapon in hand)" in c for c in equip_lines))
        self.assertFalse(any("(being worn)" in c for c in equip_lines))
        self.assertFalse(any("[" in c for c in equip_lines))

    def test_status_inventory_lists_all_pack_slots(self):
        game = new_game(seed=37)
        game.p.inv = [rogue.Item(rogue.CAT_FOOD, 0) for _ in range(rogue.INV_MAX)]
        calls = []
        game.txt = lambda x, y, s, c: calls.append(str(s))

        game.draw_inventory()

        self.assertTrue(any(c.startswith("a)") for c in calls))
        self.assertTrue(any(c.startswith("z)") for c in calls))

    def test_message_log_uses_seven_rows_with_latest_highlighted(self):
        game = new_game(seed=35)
        calls = []
        game.txt = lambda x, y, s, c: calls.append((str(s), c))
        game.msgs = ["hidden", "one", "two", "three", "four", "five", "six", "latest"]

        game.draw_msgs()

        self.assertEqual(rogue.MSG_LINES, 7)
        self.assertEqual([text for text, _ in calls], ["one", "two", "three", "four", "five", "six", "latest"])
        self.assertEqual([color for _, color in calls], [5, 5, 5, 5, 5, 5, 7])

    def test_death_screen_draws_tombstone_by_default(self):
        game = new_game(seed=35)
        calls = []
        game.txt = lambda x, y, s, c: calls.append(str(s))
        game.p.gold = 123
        game.death_cause = "killed by a hobgoblin"

        game.draw_dead()

        self.assertTrue(game.options["tombstone"])
        self.assertIn("      /    REST    \\", calls)
        self.assertIn("    |  killed by a  |", calls)
        self.assertTrue(any("hobgoblin" in c for c in calls))
        self.assertTrue(any("123 Au" in c for c in calls))

    def test_dpad_cardinal_waits_one_frame_so_second_axis_makes_one_diagonal_turn(self):
        game = new_game(seed=36)
        set_open_floor(game)
        px, py = game.p.x, game.p.y
        rogue.pyxel.set_input(
            held={rogue.pyxel.KEY_LEFT},
            pressed={rogue.pyxel.KEY_LEFT},
        )
        game.update()
        self.assertEqual((game.p.x, game.p.y, game.turn), (px, py, 0))
        self.assertEqual(game.dir_pending, (-1, 0))

        rogue.pyxel.set_input(
            held={rogue.pyxel.KEY_LEFT, rogue.pyxel.KEY_UP},
            pressed={rogue.pyxel.KEY_UP},
        )
        game.update()
        self.assertEqual((game.p.x, game.p.y, game.turn), (px - 1, py - 1, 1))
        self.assertIsNone(game.dir_pending)
        rogue.pyxel.set_input()

    def test_dpad_cardinal_tap_moves_on_next_frame_if_no_second_axis_arrives(self):
        game = new_game(seed=361)
        set_open_floor(game)
        px, py = game.p.x, game.p.y
        rogue.pyxel.set_input(
            held={rogue.pyxel.KEY_UP},
            pressed={rogue.pyxel.KEY_UP},
        )
        game.update()
        self.assertEqual((game.p.x, game.p.y, game.turn), (px, py, 0))

        rogue.pyxel.set_input()
        game.update()
        self.assertEqual((game.p.x, game.p.y, game.turn), (px, py - 1, 1))
        self.assertIsNone(game.dir_pending)

    def test_extra_gamepad_buttons_have_no_play_shortcuts(self):
        for button in (
            rogue.pyxel.GAMEPAD1_BUTTON_X,
            rogue.pyxel.GAMEPAD1_BUTTON_Y,
            rogue.pyxel.GAMEPAD1_BUTTON_LEFTSHOULDER,
            rogue.pyxel.GAMEPAD1_BUTTON_RIGHTSHOULDER,
        ):
            with self.subTest(button=button):
                game = new_game(seed=36)
                set_open_floor(game)
                start = (game.p.x, game.p.y, game.st, game.turn)
                rogue.pyxel.set_input(held={button}, pressed={button})
                game.update()
                self.assertEqual((game.p.x, game.p.y, game.st, game.turn), start)

    def test_keyboard_inventory_help_and_vi_diagonals_remain_supported(self):
        game = new_game(seed=36)
        rogue.pyxel.set_input(held={rogue.pyxel.KEY_I}, pressed={rogue.pyxel.KEY_I})
        game.update()
        self.assertEqual(game.st, rogue.ST_INVENTORY)

        game = new_game(seed=36)
        rogue.pyxel.set_input(
            held={rogue.pyxel.KEY_QUESTION},
            pressed={rogue.pyxel.KEY_QUESTION},
        )
        game.update()
        self.assertEqual(game.st, rogue.ST_HELP)

        for key, direction in (
            (rogue.pyxel.KEY_Y, (-1, -1)),
            (rogue.pyxel.KEY_U, (1, -1)),
            (rogue.pyxel.KEY_B, (-1, 1)),
            (rogue.pyxel.KEY_N, (1, 1)),
        ):
            with self.subTest(key=key):
                game = new_game(seed=36)
                set_open_floor(game)
                px, py = game.p.x, game.p.y
                rogue.pyxel.set_input(held={key}, pressed={key})
                game.update()
                self.assertEqual((game.p.x, game.p.y), (px + direction[0], py + direction[1]))

    def test_throw_records_non_blocking_animation_path(self):
        game = new_game(seed=37)
        game.mons = []
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        game.p.x, game.p.y = 2, 2
        for x in range(2, 7):
            game.tm[2][x] = rogue.T_FLOOR
        item = rogue.Item(rogue.CAT_WPN, 4)
        game.p.inv = [item]
        game.throw(item, 1, 0)
        self.assertIsNotNone(game.throw_anim)
        self.assertEqual(game.throw_anim["path"], [(3, 2), (4, 2), (5, 2), (6, 2)])
        self.assertEqual((game.gitems[-1].x, game.gitems[-1].y), (6, 2))

    def test_melee_damage_uses_weapon_damage_plus_and_strength(self):
        game = new_game(seed=38)
        game.p.wpn = rogue.Item(rogue.CAT_WPN, 0, hit_plus=0, dam_plus=1)
        monster = monster_at(game.p.x + 1, game.p.y, hp=20, armor=100, exp=0)
        old_randrange = rogue.RNG.randrange
        try:
            rogue.RNG.randrange = lambda n: n - 1
            game.p_attack(monster)
        finally:
            rogue.RNG.randrange = old_randrange
        self.assertEqual(monster.hp, 10)

    def test_enchant_weapon_increments_one_weapon_plus(self):
        game = new_game(seed=39)
        weapon = rogue.Item(rogue.CAT_WPN, 0, hit_plus=0, dam_plus=0, cursed=True)
        scroll = rogue.Item(rogue.CAT_SCR, 1)
        game.p.wpn = weapon
        game.p.inv = [weapon, scroll]
        old_randrange = rogue.random.randrange
        try:
            rogue.random.randrange = lambda n: 0
            game.use_scr(scroll)
        finally:
            rogue.random.randrange = old_randrange
        self.assertFalse(weapon.cursed)
        self.assertEqual((weapon.hit_plus, weapon.dam_plus), (1, 0))

    def test_extra_healing_reports_recovery_even_without_max_hp_increase(self):
        game = new_game(seed=390)
        extra_healing = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "extra healing")
        potion = rogue.Item(rogue.CAT_POT, extra_healing)
        game.p.inv.append(potion)
        game.p.hp = game.p.max_hp - 5
        old_randrange = rogue.RNG.randrange
        try:
            rogue.RNG.randrange = lambda n: 0
            game.use_pot(potion)
        finally:
            rogue.RNG.randrange = old_randrange

        self.assertEqual(game.p.hp, game.p.max_hp - 4)
        self.assertIn("You feel much better. (+1)", game.msgs)

    def test_random_weapon_generation_changes_hit_plus_only(self):
        old_random = rogue.random.random
        old_randint = rogue.random.randint
        old_randrange = rogue.random.randrange
        seq = iter([9, 2])
        try:
            rogue.random.random = lambda: 0.80
            rogue.random.randint = lambda a, b: a
            rogue.random.randrange = lambda n: next(seq)
            item = rogue.make_item(depth=10)
        finally:
            rogue.random.random = old_random
            rogue.random.randint = old_randint
            rogue.random.randrange = old_randrange
        self.assertEqual(item.cat, rogue.CAT_WPN)
        self.assertTrue(item.cursed)
        self.assertEqual(item.hit_plus, -3)
        self.assertEqual(item.dam_plus, 0)

    def test_arrow_with_bow_uses_hurl_damage_and_bow_pluses(self):
        game = new_game(seed=40)
        bow = rogue.Item(rogue.CAT_WPN, 2, hit_plus=2, dam_plus=3)
        arrow = rogue.Item(rogue.CAT_WPN, 3, hit_plus=1, dam_plus=4)
        game.p.wpn = bow
        monster = monster_at(game.p.x + 1, game.p.y, hp=30, armor=100, exp=0)
        old_randrange = rogue.RNG.randrange
        try:
            rogue.RNG.randrange = lambda n: n - 1
            hit, dmg = game.roll_player_attack(monster, arrow, thrown=True)
        finally:
            rogue.RNG.randrange = old_randrange
        self.assertTrue(hit)
        self.assertEqual(dmg, 14)

    def test_missed_thrown_weapon_falls_without_damage(self):
        game = new_game(seed=40)
        set_open_floor(game)
        arrow = rogue.Item(rogue.CAT_WPN, 3, hit_plus=0, dam_plus=0)
        monster = monster_at(game.p.x + 2, game.p.y, hp=8, armor=0, exp=0)
        game.p.inv = [arrow]
        game.mons = [monster]
        old_randrange = rogue.random.randrange
        try:
            rogue.random.randrange = lambda n: 0
            game.throw(arrow, 1, 0)
        finally:
            rogue.random.randrange = old_randrange
        self.assertEqual(monster.hp, 8)
        self.assertIn(arrow, game.gitems)

    def test_baseline_combat_message_uses_catalog(self):
        game = new_game(seed=41, lang=rogue.LANG_JA)
        monster = monster_at(game.p.x + 1, game.p.y, hp=1, armor=100, exp=5)
        game.p_attack(monster)
        self.assertFalse(monster.alive)
        self.assertIn("小鬼を倒した。 (5 exp)", game.msgs)

    def test_dash_starts_when_direction_is_held_before_b(self):
        game = new_game(seed=42)
        set_open_floor(game)
        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT},
        )
        game.update()
        self.assertFalse(game.dashing)

        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT, rogue.pyxel.GAMEPAD1_BUTTON_B},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_B},
        )
        game.update()
        self.assertTrue(game.dashing)
        self.assertEqual(game.dash_d, (1, 0))

    def test_dash_starts_when_b_is_held_before_direction(self):
        game = new_game(seed=43)
        set_open_floor(game)
        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_B},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_B},
        )
        game.update()
        self.assertFalse(game.dashing)

        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_B, rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT},
        )
        game.update()
        self.assertTrue(game.dashing)
        self.assertEqual(game.dash_d, (1, 0))

    def test_dash_respects_diagonal_assist_held_direction_rules(self):
        game = new_game(seed=44)
        set_open_floor(game)
        game.diag_assist = True
        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_B, rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_B, rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT},
        )
        game.update()
        self.assertFalse(game.dashing)

        rogue.pyxel.set_input()
        game = new_game(seed=45)
        set_open_floor(game)
        game.diag_assist = True
        rogue.pyxel.set_input(
            held={
                rogue.pyxel.GAMEPAD1_BUTTON_B,
                rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT,
                rogue.pyxel.GAMEPAD1_BUTTON_DPAD_UP,
            },
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_B, rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT},
        )
        game.update()
        self.assertTrue(game.dashing)
        self.assertEqual(game.dash_d, (1, -1))

    def test_diag_assist_does_not_block_menu_vertical_navigation(self):
        game = new_game(seed=47)
        game.diag_assist = True

        game.open_menu()
        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_DOWN},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_DOWN},
        )
        game.update()
        self.assertEqual(game.mcur, 1)

        game.st = rogue.ST_ITEM
        game.fitems = [rogue.Item(rogue.CAT_FOOD, 0), rogue.Item(rogue.CAT_FOOD, 0)]
        game.icur = 0
        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_DOWN},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_DOWN},
        )
        game.update()
        self.assertEqual(game.icur, 1)

        game.open_aux()
        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_DOWN},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_DOWN},
        )
        game.update()
        self.assertEqual(game.acur, 1)

    def test_diagonal_attack_is_blocked_through_door_corner(self):
        game = new_game(seed=48)
        set_open_floor(game)
        game.tm[5][5] = rogue.T_DOOR
        game.tm[4][5] = rogue.T_HWALL
        game.p.x, game.p.y = 5, 5
        monster = monster_at(6, 4, hp=10, armor=100, exp=5)
        game.mons = [monster]
        attacked = []
        game.p_attack = lambda m: attacked.append(m)

        self.assertFalse(game.try_move(1, -1))
        self.assertEqual(attacked, [])
        self.assertEqual(game.turn, 0)

    def test_monster_diagonal_attack_is_blocked_through_door_corner(self):
        game = new_game(seed=49)
        set_open_floor(game)
        game.tm[5][5] = rogue.T_DOOR
        game.tm[4][5] = rogue.T_HWALL
        game.p.x, game.p.y = 6, 4
        monster = monster_at(5, 5, "B", "bat", 10, 1, 100, "1x2", 5, "erratic")
        game.mons = [monster]
        game.visible = {(5, 5), (6, 4)}
        attacked = []
        game.m_attack = lambda m: attacked.append(m)
        old_random = rogue.random.random
        old_choice = rogue.random.choice
        try:
            choices = iter([1, -1])
            rogue.random.random = lambda: 0
            rogue.random.choice = lambda seq: next(choices)
            game.m_turn(monster)
        finally:
            rogue.random.random = old_random
            rogue.random.choice = old_choice

        self.assertEqual(attacked, [])
        self.assertEqual((monster.x, monster.y), (5, 5))

    def test_running_monster_routes_around_blocked_door_diagonal(self):
        game = new_game(seed=490)
        set_open_floor(game)
        game.tm[5][5] = rogue.T_DOOR
        game.tm[4][5] = rogue.T_HWALL
        game.p.x, game.p.y = 5, 5
        monster = monster_at(6, 4, hp=10, armor=100, exp=5)
        monster.running = True
        game.mons = [monster]
        attacked = []
        game.m_attack = lambda m: attacked.append(m)

        game.m_turn(monster)

        self.assertEqual(attacked, [])
        self.assertEqual((monster.x, monster.y), (6, 5))

    def test_monster_in_other_room_heads_for_exit_before_hero(self):
        game = new_game(seed=491)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        left = rogue.Room(1, 1, 5, 5)
        right = rogue.Room(10, 1, 5, 5)
        game.rooms = [left, right]
        rogue.DGen._room(game.tm, left)
        rogue.DGen._room(game.tm, right)
        game.tm[3][5] = rogue.T_DOOR
        game.tm[3][10] = rogue.T_DOOR
        for x in range(6, 10):
            game.tm[3][x] = rogue.T_CORR
        game.p.x, game.p.y = 12, 3
        monster = monster_at(3, 3, hp=10, armor=100, exp=5)
        monster.running = True
        game.mons = [monster]

        game.m_turn(monster)

        self.assertEqual((monster.x, monster.y), (4, 3))

    def test_diagonal_attack_works_when_orthogonal_tiles_are_open(self):
        game = new_game(seed=50)
        set_open_floor(game)
        game.p.x, game.p.y = 5, 5
        monster = monster_at(6, 4, hp=10, armor=100, exp=5)
        game.mons = [monster]
        attacked = []
        game.p_attack = lambda m: attacked.append(m)

        self.assertTrue(game.try_move(1, -1))
        self.assertEqual(attacked, [monster])
        self.assertEqual(game.turn, 1)

    def test_monster_does_not_move_until_running(self):
        game = new_game(seed=501)
        set_open_floor(game)
        game.p.x, game.p.y = 5, 5
        monster = monster_at(7, 5, hp=10, armor=100, exp=5)
        game.mons = [monster]

        game.m_turn(monster)

        self.assertFalse(monster.running)
        self.assertEqual((monster.x, monster.y), (7, 5))

    def test_visible_mean_monster_can_wake_and_run(self):
        game = new_game(seed=502)
        set_open_floor(game)
        monster = monster_at(game.p.x + 2, game.p.y, hp=10, armor=100, exp=5)
        game.mons = [monster]
        game.visible.add((monster.x, monster.y))
        old_randrange = rogue.random.randrange
        try:
            rogue.random.randrange = lambda n: 1
            game.wake_visible_monsters()
        finally:
            rogue.random.randrange = old_randrange

        self.assertTrue(monster.running)

    def test_ice_monster_freezes_on_every_hit(self):
        game = new_game(seed=503)
        set_open_floor(game)
        game.p.ac = 0
        game.p.hp = 99
        monster = monster_at(game.p.x + 1, game.p.y, "I", "ice monster", 10, 20, 100, "0x0", 5, "freeze")

        game.m_attack(monster)

        self.assertGreaterEqual(game.p.no_command, 2)
        self.assertIn("you are frozen", game.msgs)

    def test_rattlesnake_poison_strength_depends_on_save(self):
        game = new_game(seed=504)
        set_open_floor(game)
        game.p.ac = 0
        game.p.hp = 99
        game.p.st = 10
        monster = monster_at(game.p.x + 1, game.p.y, "R", "rattlesnake", 10, 20, 100, "1x6", 5, "poison")

        game.save_vs_poison = lambda: False
        game.m_attack(monster)
        self.assertEqual(game.p.st, 9)

        game.save_vs_poison = lambda: True
        game.m_attack(monster)
        self.assertEqual(game.p.st, 9)

    def test_flying_monster_gets_extra_chase_move_at_distance(self):
        game = new_game(seed=505)
        set_open_floor(game)
        game.p.x, game.p.y = 5, 5
        monster = monster_at(9, 5, "K", "kestrel", 10, 1, 100, "1x4", 5, "fly")
        monster.running = True
        game.mons = [monster]

        game.m_turn(monster)

        self.assertEqual((monster.x, monster.y), (7, 5))

    def test_monster_chase_avoids_scare_monster_scroll_on_floor(self):
        game = new_game(seed=507)
        set_open_floor(game)
        game.p.x, game.p.y = 5, 5
        scare_kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "scare monster")
        scroll = rogue.Item(rogue.CAT_SCR, scare_kind)
        scroll.x, scroll.y = 6, 5
        game.gitems = [scroll]
        monster = monster_at(7, 5, hp=10, armor=100, exp=5)
        monster.running = True
        game.mons = [monster]

        game.m_turn(monster)

        self.assertNotEqual((monster.x, monster.y), (6, 5))

    def test_held_monster_skips_turn_and_counts_down(self):
        game = new_game(seed=506)
        set_open_floor(game)
        game.p.x, game.p.y = 5, 5
        monster = monster_at(7, 5, hp=10, armor=100, exp=5)
        monster.running = True
        monster.held = 2
        game.mons = [monster]

        game.m_turn(monster)

        self.assertEqual(monster.held, 1)
        self.assertEqual((monster.x, monster.y), (7, 5))

    def test_wait_select_shortcuts_and_empty_action_search(self):
        game = new_game(seed=46)
        set_open_floor(game)
        searched = []
        game.do_search = lambda front_only=False: searched.append(front_only)
        waited = []
        game.do_wait = lambda: waited.append(True)

        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_A, rogue.pyxel.GAMEPAD1_BUTTON_B},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_A},
        )
        game.update()
        self.assertEqual(waited, [True])
        self.assertEqual(searched, [])

        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_BACK, rogue.pyxel.GAMEPAD1_BUTTON_A},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_A},
        )
        game.update()
        self.assertEqual(searched, [False])
        self.assertEqual(game.st, rogue.ST_PLAY)

        rogue.pyxel.set_input()
        game = new_game(seed=47)
        set_open_floor(game)
        game.do_search = lambda front_only=False: searched.append(front_only)
        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_A},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_A},
        )
        game.update()
        self.assertEqual(searched[-1], True)

    def test_select_a_searches_and_select_b_prompts_throw_direction_before_item_selection(self):
        game = new_game(seed=48)
        set_open_floor(game)
        searched = []
        game.do_search = lambda front_only=False: searched.append(front_only)

        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_BACK, rogue.pyxel.GAMEPAD1_BUTTON_A},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_A},
        )
        game.update()
        self.assertEqual(searched, [False])
        self.assertEqual(game.st, rogue.ST_PLAY)

        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_BACK, rogue.pyxel.GAMEPAD1_BUTTON_B},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_B},
        )
        game.update()
        self.assertEqual(game.st, rogue.ST_DIR)
        self.assertEqual(game.cact, "Throw")
        self.assertEqual(game.dact, "Throw")

        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT},
        )
        game.update()
        self.assertEqual(game.st, rogue.ST_ITEM)
        self.assertEqual(game.throw_dir, (1, 0))
        self.assertEqual(game.fitems, game.p.inv)

    def test_cardinal_move_does_not_linger_into_second_step(self):
        game = new_game(seed=49)
        set_open_floor(game)
        start = (game.p.x, game.p.y)

        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT},
        )
        game.update()
        self.assertEqual((game.p.x, game.p.y), start)

        rogue.pyxel.set_input()
        game.update()
        self.assertEqual((game.p.x, game.p.y), (start[0] + 1, start[1]))

        rogue.pyxel.set_input()
        game.update()

        self.assertEqual((game.p.x, game.p.y), (start[0] + 1, start[1]))

    def test_diag_assist_move_does_not_linger_into_second_step(self):
        game = new_game(seed=50)
        set_open_floor(game)
        game.diag_assist = True
        start = (game.p.x, game.p.y)

        rogue.pyxel.set_input(
            held={
                rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT,
                rogue.pyxel.GAMEPAD1_BUTTON_DPAD_DOWN,
            },
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT},
        )
        game.update()
        self.assertEqual((game.p.x, game.p.y), (start[0] + 1, start[1] + 1))

        rogue.pyxel.set_input()
        game.update()

        self.assertEqual((game.p.x, game.p.y), (start[0] + 1, start[1] + 1))

    def test_quick_throw_cancel_returns_to_play_after_direction_first_flow(self):
        game = new_game(seed=48)
        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_BACK, rogue.pyxel.GAMEPAD1_BUTTON_B},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_B},
        )
        game.update()

        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT},
        )
        game.update()

        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_B},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_B},
        )
        game.update()
        self.assertEqual(game.st, rogue.ST_PLAY)
        self.assertIsNone(game.throw_dir)

    def test_select_direction_inspects_visible_trap_without_spending_turn(self):
        game = new_game(seed=51)
        set_open_floor(game)
        x, y = game.p.x + 1, game.p.y
        game.tm[y][x] = rogue.T_TRAP
        game.traps[(x, y)] = 1

        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_BACK, rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT},
        )
        game.update()

        self.assertEqual(game.turn, 0)
        self.assertEqual(game.st, rogue.ST_PLAY)
        self.assertIn("You have found arrow trap.", game.msgs)

    def test_trap_inspect_reports_no_trap_and_does_not_reveal_hidden_traps(self):
        game = new_game(seed=52)
        set_open_floor(game)
        x, y = game.p.x + 1, game.p.y
        game.traps[(x, y)] = 2

        game.inspect_trap(1, 0)

        self.assertEqual(game.turn, 0)
        self.assertEqual(game.tm[y][x], rogue.T_FLOOR)
        self.assertIn("no trap there", game.msgs)

    def test_aux_trap_enters_direction_prompt_and_inspects_trap(self):
        game = new_game(seed=53)
        set_open_floor(game)
        x, y = game.p.x + 1, game.p.y
        game.tm[y][x] = rogue.T_TRAP
        game.traps[(x, y)] = 3
        game.open_aux()
        game.acur = rogue.AUX_ACTIONS.index("Trap")

        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_A},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_A},
        )
        game.update()
        self.assertEqual(game.st, rogue.ST_DIR)
        self.assertEqual(game.dact, "Trap")

        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT},
        )
        game.update()
        self.assertEqual(game.st, rogue.ST_PLAY)
        self.assertEqual(game.turn, 0)
        self.assertIn("You have found bear trap.", game.msgs)

    def test_keyboard_caret_enters_trap_direction_prompt(self):
        game = new_game(seed=54)
        set_open_floor(game)
        x, y = game.p.x + 1, game.p.y
        game.tm[y][x] = rogue.T_TRAP
        game.traps[(x, y)] = 4

        rogue.pyxel.set_input(
            held={rogue.pyxel.KEY_SHIFT, rogue.pyxel.KEY_6},
            pressed={rogue.pyxel.KEY_6},
        )
        game.update()
        self.assertEqual(game.st, rogue.ST_DIR)
        self.assertEqual(game.dact, "Trap")

        rogue.pyxel.set_input(
            held={rogue.pyxel.KEY_RIGHT},
            pressed={rogue.pyxel.KEY_RIGHT},
        )
        game.update()
        self.assertEqual(game.turn, 0)
        self.assertIn("You have found teleport trap.", game.msgs)

    def test_rogue54_rnd_and_trap_spawn_frequency_shape(self):
        self.assertEqual(rogue.rnd(0), 0)
        game = new_game(seed=55)
        set_open_floor(game)
        game.p.depth = 1
        old_randrange = rogue.random.randrange
        old_shuffle = rogue.random.shuffle
        try:
            rogue.random.randrange = lambda n: n - 1
            game._spawn_traps()
            self.assertEqual(game.traps, {})

            rogue.random.randrange = lambda n: 0
            rogue.random.shuffle = lambda seq: None
            game._spawn_traps()
            self.assertEqual(len(game.traps), 1)
            self.assertEqual(next(iter(game.traps.values())), 0)
        finally:
            rogue.random.randrange = old_randrange
            rogue.random.shuffle = old_shuffle

    def test_secret_door_and_passage_generation_uses_rogue54_depth_gate(self):
        game = new_game(seed=56)
        set_open_floor(game)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        game.tm[5][4] = rogue.T_FLOOR
        game.tm[5][5] = rogue.T_DOOR
        game.tm[5][6] = rogue.T_CORR
        game.tm[6][6] = rogue.T_CORR
        game.p.depth = 1
        old_randrange = rogue.random.randrange
        try:
            rogue.random.randrange = lambda n: 0
            game._hide_secret_features()
            self.assertEqual(game.hidden_tiles, {})

            game.p.depth = 2
            game._hide_secret_features()
            self.assertEqual(game.hidden_tiles[(5, 5)], rogue.T_DOOR)
            self.assertEqual(game.hidden_tiles[(6, 5)], rogue.T_CORR)
            self.assertEqual(game.tm[5][5], rogue.T_VWALL)
            self.assertEqual(game.tm[5][6], rogue.T_VOID)
        finally:
            rogue.random.randrange = old_randrange

    def test_search_reveals_hidden_door_passage_and_trap_with_rogue54_rates(self):
        game = new_game(seed=57)
        set_open_floor(game)
        px, py = game.p.x, game.p.y
        game.hidden_tiles[(px + 1, py)] = rogue.T_DOOR
        game.tm[py][px + 1] = rogue.T_VWALL
        game.hidden_tiles[(px, py + 1)] = rogue.T_CORR
        game.tm[py + 1][px] = rogue.T_VOID
        game.traps[(px - 1, py)] = 1
        game.tm[py][px - 1] = rogue.T_FLOOR
        old_randrange = rogue.random.randrange
        try:
            rogue.random.randrange = lambda n: 0
            game.do_search()
        finally:
            rogue.random.randrange = old_randrange

        self.assertEqual(game.tm[py][px + 1], rogue.T_DOOR)
        self.assertEqual(game.tm[py + 1][px], rogue.T_CORR)
        self.assertEqual(game.tm[py][px - 1], rogue.T_TRAP)
        self.assertEqual(game.turn, 1)
        self.assertIn("You found something!", game.msgs)

    def test_search_failure_keeps_hidden_features_hidden(self):
        game = new_game(seed=58)
        set_open_floor(game)
        px, py = game.p.x, game.p.y
        game.hidden_tiles[(px + 1, py)] = rogue.T_DOOR
        game.tm[py][px + 1] = rogue.T_VWALL
        game.traps[(px - 1, py)] = 1
        old_randrange = rogue.random.randrange
        try:
            rogue.random.randrange = lambda n: n - 1
            game.do_search()
        finally:
            rogue.random.randrange = old_randrange

        self.assertEqual(game.tm[py][px + 1], rogue.T_VWALL)
        self.assertEqual(game.tm[py][px - 1], rogue.T_FLOOR)
        self.assertIn("You find nothing.", game.msgs)

    def test_stepping_on_hidden_bear_trap_reveals_it_and_spends_turn(self):
        game = new_game(seed=59)
        set_open_floor(game)
        x, y = game.p.x + 1, game.p.y
        game.traps[(x, y)] = 3
        game.try_move(1, 0)

        self.assertEqual((game.p.x, game.p.y), (x, y))
        self.assertEqual(game.tm[y][x], rogue.T_TRAP)
        self.assertGreater(game.p.stuck, 0)
        self.assertEqual(game.turn, 1)
        self.assertIn("you are caught in a bear trap", game.msgs)

    def test_poison_save_uses_rogue54_level_scaled_threshold(self):
        game = new_game(seed=60)
        game.p.level = 4
        old_randrange = rogue.random.randrange
        try:
            rogue.random.randrange = lambda n: 8
            self.assertTrue(game.save_vs_poison())
            rogue.random.randrange = lambda n: 9
            self.assertFalse(game.save_vs_poison())
        finally:
            rogue.random.randrange = old_randrange


if __name__ == "__main__":
    unittest.main()
