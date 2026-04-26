import importlib
import os
import random
import subprocess
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
    pyxel.init_calls = []
    pyxel.init = lambda *a, **kw: pyxel.init_calls.append((a, kw))
    pyxel.run = lambda *a, **kw: None
    pyxel.cls = lambda *a, **kw: None
    pyxel.text = lambda *a, **kw: None
    pyxel.rect = lambda *a, **kw: None
    pyxel.rectb = lambda *a, **kw: None
    pyxel.__file__ = os.path.join(os.getcwd(), "pyxel", "__init__.py")
    for i, key in enumerate([
        "KEY_NONE", "KEY_UP", "KEY_DOWN", "KEY_LEFT", "KEY_RIGHT",
        "KEY_H", "KEY_J", "KEY_K", "KEY_L",
        "KEY_Y", "KEY_U", "KEY_B", "KEY_N",
        "KEY_Z", "KEY_X", "KEY_C", "KEY_S",
        "KEY_Q", "KEY_W", "KEY_E", "KEY_T", "KEY_P",
        "KEY_I", "KEY_6", "KEY_SPACE",
        "KEY_ESCAPE", "KEY_RETURN", "KEY_TAB", "KEY_BACKSPACE",
        "KEY_PERIOD", "KEY_COMMA", "KEY_MINUS",
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
    def test_palette_tables_are_split_without_changing_defaults(self):
        import rogue_palettes

        self.assertEqual(rogue.DEFAULT_PALETTE, rogue_palettes.PALETTE_GBC_HIGH_CONTRAST)
        self.assertEqual(
            rogue.PALETTE_IDS,
            (
                rogue_palettes.PALETTE_GBC,
                rogue_palettes.PALETTE_GBC_HIGH_CONTRAST,
                rogue_palettes.PALETTE_FLEXOKI_LIGHT,
            ),
        )
        self.assertEqual(rogue.PALETTE_LABELS[rogue.DEFAULT_PALETTE], "GBC High Contrast")
        self.assertEqual(set(rogue.PALETTES), set(rogue.PALETTE_IDS))
        self.assertTrue(all(len(colors) == 32 for colors in rogue.PALETTES.values()))

    def test_map_tables_are_split_without_changing_play_area(self):
        import rogue_map

        self.assertEqual((rogue.MAP_W, rogue.MAP_H), (rogue_map.MAP_W, rogue_map.MAP_H))
        self.assertEqual((rogue.PLAY_Y_MIN, rogue.PLAY_Y_MAX), (rogue_map.PLAY_Y_MIN, rogue_map.PLAY_Y_MAX))
        self.assertEqual(rogue.PLAY_H, rogue_map.PLAY_H)
        self.assertEqual(rogue.TILE_CH, rogue_map.TILE_CH)
        self.assertEqual(rogue.WALKABLE, rogue_map.WALKABLE)
        self.assertEqual((rogue.ROOM_DARK, rogue.ROOM_GONE, rogue.ROOM_MAZE), ("dark", "gone", "maze"))

    def test_item_category_tables_are_split_without_changing_symbols(self):
        import rogue_items

        self.assertEqual(
            (rogue.CAT_POT, rogue.CAT_SCR, rogue.CAT_FOOD, rogue.CAT_WPN, rogue.CAT_ARM),
            (rogue_items.CAT_POT, rogue_items.CAT_SCR, rogue_items.CAT_FOOD, rogue_items.CAT_WPN, rogue_items.CAT_ARM),
        )
        self.assertEqual((rogue.CAT_RING, rogue.CAT_STICK, rogue.CAT_GOLD, rogue.CAT_AMULET), ("ring", "stick", "gold", "amulet"))
        self.assertEqual(rogue.ISYM, rogue_items.ISYM)
        self.assertEqual(rogue.ICOL, rogue_items.ICOL)
        self.assertEqual(rogue.HALLU_THINGS, rogue_items.HALLU_THINGS)

    def test_ui_tables_are_split_without_changing_menu_actions(self):
        import rogue_ui

        self.assertEqual((rogue.ST_PLAY, rogue.ST_MENU, rogue.ST_ITEM, rogue.ST_DIR), (0, 1, 2, 3))
        self.assertEqual((rogue.ST_QUIT, rogue.ST_QUIT_CONFIRM, rogue.ST_SCORE), (10, 11, 12))
        self.assertEqual(rogue.CALL_PRESETS, rogue_ui.CALL_PRESETS)
        self.assertEqual(rogue.MENU_ACTIONS, rogue_ui.MENU_ACTIONS)
        self.assertEqual(rogue.AUX_ACTIONS, rogue_ui.AUX_ACTIONS)
        self.assertEqual((rogue.B_TAP_FRAMES, rogue.BACK_TAP_FRAMES), (8, 8))

    def test_layout_constants_are_split_without_changing_screen_geometry(self):
        import rogue_layout

        self.assertEqual((rogue.SCR_W, rogue.SCR_H), (576, 360))
        self.assertEqual((rogue.TILE_W, rogue.TILE_H), (6, 12))
        self.assertEqual((rogue.ZV_COLS, rogue.ZV_ROWS), (rogue.MAP_W, rogue.PLAY_H))
        self.assertEqual((rogue.ZV_PX_W, rogue.ZV_PX_H), (rogue_layout.ZV_PX_W, rogue_layout.ZV_PX_H))
        self.assertEqual((rogue.HUD_X, rogue.HUD_W), (rogue_layout.HUD_X, rogue_layout.HUD_W))
        self.assertEqual((rogue.MSG_LINES, rogue.MSG_COLS), (7, rogue_layout.MSG_COLS))

    def test_combat_message_keys_are_split_without_changing_order(self):
        import rogue_combat_text

        self.assertEqual(rogue.PLAYER_HIT_MESSAGE_KEYS, rogue_combat_text.PLAYER_HIT_MESSAGE_KEYS)
        self.assertEqual(rogue.PLAYER_MISS_MESSAGE_KEYS, rogue_combat_text.PLAYER_MISS_MESSAGE_KEYS)
        self.assertEqual(rogue.MONSTER_HIT_MESSAGE_KEYS, rogue_combat_text.MONSTER_HIT_MESSAGE_KEYS)
        self.assertEqual(rogue.MONSTER_MISS_MESSAGE_KEYS, rogue_combat_text.MONSTER_MISS_MESSAGE_KEYS)
        self.assertEqual(rogue.PLAYER_HIT_MESSAGE_KEYS[0], "fight.player_hit_excellent")

    def test_language_settings_are_split_without_changing_defaults(self):
        import rogue_lang

        self.assertEqual((rogue.LANG_EN, rogue.LANG_JA), (rogue_lang.LANG_EN, rogue_lang.LANG_JA))
        self.assertEqual(rogue.DEFAULT_LANG, rogue_lang.DEFAULT_LANG)
        self.assertEqual(rogue.Settings, rogue_lang.Settings)
        self.assertEqual(rogue.Settings(language="xx").language, rogue.LANG_EN)
        self.assertEqual(rogue.Settings(palette="unknown").palette, rogue.DEFAULT_PALETTE)

    def test_timing_constants_are_split_without_changing_values(self):
        import rogue_timing

        names = (
            "HUNGERTIME", "MORETIME", "STOMACHSIZE", "STARVETIME",
            "SEEDURATION", "HEALTIME", "MAX_TRAPS", "AMULET_LEVEL",
            "WANDERTIME", "BEARTIME", "SLEEPTIME", "BORE_LEVEL",
            "BOLT_LENGTH", "VS_MAGIC", "HUHDURATION",
        )
        self.assertEqual({name: getattr(rogue, name) for name in names}, {name: getattr(rogue_timing, name) for name in names})
        self.assertEqual((rogue.HUNGERTIME, rogue.SEEDURATION, rogue.WANDERTIME), (1300, 850, 70))

    def test_pyxel_escape_is_not_the_runtime_quit_key(self):
        rogue.pyxel.init_calls.clear()

        rogue.Game()

        self.assertEqual(rogue.pyxel.init_calls[-1][1].get("quit_key"), rogue.pyxel.KEY_NONE)

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

    def test_rogue_544_zap_light_lit_room_uses_room_message(self):
        # Rogue 5.4.4 sticks.c:WS_LIGHT uses the room-lit branch unless proom is ISGONE.
        import rogue_sticks

        game = new_game(seed=201)
        room = rogue.Room(5, 5, 8, 6)
        game.rooms = [room]
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        rogue.DGen._room(game.tm, room)
        game.p.x, game.p.y = 7, 7
        game.update_fov()
        stick = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_LIGHT, charges=1)

        game.zap_stick(stick, 1, 0)

        self.assertIn("the room is lit", game.msgs)
        self.assertNotIn("the corridor glows and then fades", game.msgs)

    def test_rogue_544_sticks_helper_light_uses_room_branch(self):
        # Rogue 5.4.4 sticks.c:WS_LIGHT uses corridor branch only for ISGONE/no room.
        import rogue_sticks

        self.assertTrue(rogue_sticks.light_uses_room_branch(True))
        self.assertFalse(rogue_sticks.light_uses_room_branch(False))

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

    def test_rogue_544_cancelled_xeroc_reveals_disguise_as_type(self):
        # Rogue 5.4.4 sticks.c:do_zap() WS_CANCEL sets t_disguise = t_type.
        import rogue_sticks

        game = new_game(seed=305)
        set_open_floor(game)
        xeroc = monster_at(game.p.x + 2, game.p.y, sym="X", name="xeroc")
        xeroc.disguise = "?"
        game.mons = [xeroc]

        cancel = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_CANCEL, charges=1)
        game.zap_stick(cancel, 1, 0)

        self.assertEqual(xeroc.disguise, "X")
        self.assertEqual(game.visible_monster_sym(xeroc), "X")

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
        self.assertTrue(game.ident.wk[rogue_sticks.WS_POLYMORPH])

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

    def test_rogue_544_sticks_helper_teleport_to_position(self):
        # Rogue 5.4.4 sticks.c:WS_TELTO sets new_pos to hero + delta.
        import rogue_sticks

        self.assertEqual(rogue_sticks.teleport_to_position((10, 7), (1, -1)), (11, 6))

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

    def test_rogue_544_zap_magic_missile_identifies_and_damages_unsaved_target(self):
        # Rogue 5.4.4 sticks.c:do_zap() WS_MISSILE sets known, save_throw(VS_MAGIC), then hit_monster with 1x4 +1.
        import rogue_sticks

        game = new_game(seed=207)
        set_open_floor(game)
        monster = monster_at(game.p.x + 2, game.p.y, hp=10)
        game.mons = [monster]
        game.monster_save_throw = lambda which, m: False
        old_roll = rogue.RNG.roll
        try:
            rogue.RNG.roll = lambda number, sides: 4
            stick = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_MISSILE, charges=1)
            game.zap_stick(stick, 1, 0)
        finally:
            rogue.RNG.roll = old_roll

        self.assertEqual(stick.charges, 0)
        self.assertTrue(game.ident.wk[rogue_sticks.WS_MISSILE])
        self.assertEqual(monster.hp, 3)
        self.assertTrue(monster.running)

    def test_rogue_544_magic_missile_adds_current_weapon_damage_plus(self):
        # Rogue 5.4.4 sticks.c:WS_MISSILE sets o_launch=cur_weapon->o_which, so roll_em() adds cur_weapon o_dplus.
        import rogue_sticks

        game = new_game(seed=229)
        set_open_floor(game)
        game.p.wpn = rogue.Item(rogue.CAT_WPN, 0, hit_plus=0, dam_plus=3)
        monster = monster_at(game.p.x + 2, game.p.y, hp=20)
        game.mons = [monster]
        game.monster_save_throw = lambda which, m: False
        old_roll = rogue.RNG.roll
        try:
            rogue.RNG.roll = lambda number, sides: 4
            stick = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_MISSILE, charges=1)
            game.zap_stick(stick, 1, 0)
        finally:
            rogue.RNG.roll = old_roll

        self.assertEqual(monster.hp, 11)

    def test_rogue_544_sticks_helper_magic_missile_damage(self):
        # Rogue 5.4.4 sticks.c:WS_MISSILE uses 1x4 + o_dplus + cur_weapon o_dplus + strength damage.
        import rogue_sticks

        self.assertEqual(rogue_sticks.magic_missile_damage(4, 3, 1), 9)
        self.assertEqual(rogue_sticks.magic_missile_damage(1, -5, 0), 0)

    def test_rogue_544_zap_magic_missile_saved_target_takes_no_damage(self):
        # Rogue 5.4.4 sticks.c:do_zap() WS_MISSILE vanishes if save_throw(VS_MAGIC) succeeds.
        import rogue_sticks

        game = new_game(seed=208)
        set_open_floor(game)
        monster = monster_at(game.p.x + 2, game.p.y, hp=10)
        game.mons = [monster]
        game.monster_save_throw = lambda which, m: True
        stick = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_MISSILE, charges=1)

        game.zap_stick(stick, 1, 0)

        self.assertEqual(stick.charges, 0)
        self.assertTrue(game.ident.wk[rogue_sticks.WS_MISSILE])
        self.assertEqual(monster.hp, 10)
        self.assertFalse(monster.running)
        self.assertIn("the missle vanishes with a puff of smoke", game.msgs)

    def test_rogue_544_zap_drain_halves_player_hp_and_spreads_damage(self):
        # Rogue 5.4.4 sticks.c:drain() halves current HP, then divides that HP among monsters in the room.
        import rogue_sticks

        game = new_game(seed=209)
        set_open_floor(game)
        game.p.hp = 16
        monster_a = monster_at(game.p.x + 2, game.p.y, hp=10)
        monster_b = monster_at(game.p.x + 3, game.p.y, hp=10)
        game.mons = [monster_a, monster_b]
        stick = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_DRAIN, charges=1)

        game.zap_stick(stick, 1, 0)

        self.assertEqual(stick.charges, 0)
        self.assertEqual(game.p.hp, 8)
        self.assertEqual(monster_a.hp, 6)
        self.assertEqual(monster_b.hp, 6)
        self.assertTrue(monster_a.running)
        self.assertTrue(monster_b.running)

    def test_rogue_544_zap_drain_in_passage_is_not_adjacent_only(self):
        # Rogue 5.4.4 sticks.c:drain() includes monsters in the same passage, not only adjacent monsters.
        import rogue_sticks

        game = new_game(seed=209)
        set_open_floor(game)
        game.p.hp = 12
        game.tm[game.p.y][game.p.x] = rogue.T_CORR
        monster = monster_at(game.p.x + 4, game.p.y, hp=10)
        game.tm[monster.y][monster.x] = rogue.T_CORR
        game.mons = [monster]
        stick = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_DRAIN, charges=1)

        game.zap_stick(stick, 1, 0)

        self.assertEqual(game.p.hp, 6)
        self.assertEqual(monster.hp, 4)

    def test_rogue_544_sticks_helper_drain_life_split(self):
        # Rogue 5.4.4 sticks.c:drain() halves HP first, then divides remaining HP by target count.
        import rogue_sticks

        self.assertEqual(rogue_sticks.drain_life_split(15, 2), (7, 3))
        self.assertEqual(rogue_sticks.drain_life_split(12, 0), (12, 0))

    def test_rogue_544_zap_drain_too_weak_does_not_consume_charge(self):
        # Rogue 5.4.4 sticks.c:do_zap() returns before charge decrement when HP is below 2.
        import rogue_sticks

        game = new_game(seed=210)
        set_open_floor(game)
        game.p.hp = 1
        stick = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_DRAIN, charges=1)

        game.zap_stick(stick, 1, 0)

        self.assertEqual(stick.charges, 1)
        self.assertIn("you are too weak to use it", game.msgs)

    def test_rogue_544_zap_bolt_hits_unsaved_monster_for_6x6_damage(self):
        # Rogue 5.4.4 sticks.c:do_zap() WS_ELECT/WS_FIRE/WS_COLD calls fire_bolt();
        # fire_bolt() uses a FLAME weapon with 6x6 damage and marks ws_info known.
        import rogue_sticks

        game = new_game(seed=218)
        set_open_floor(game)
        monster = monster_at(game.p.x + 2, game.p.y, hp=40)
        game.mons = [monster]
        game.monster_save_throw = lambda which, m: False
        old_roll = rogue.RNG.roll
        try:
            rogue.RNG.roll = lambda number, sides: 18
            stick = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_ELECT, charges=1)
            game.zap_stick(stick, 1, 0)
        finally:
            rogue.RNG.roll = old_roll

        self.assertEqual(stick.charges, 0)
        self.assertTrue(game.ident.wk[rogue_sticks.WS_ELECT])
        self.assertEqual(monster.hp, 22)
        self.assertTrue(monster.running)

    def test_rogue_544_zap_bolt_saved_monster_takes_no_damage(self):
        # Rogue 5.4.4 sticks.c:fire_bolt() leaves a saved monster unharmed and reports a miss.
        import rogue_sticks

        game = new_game(seed=219)
        set_open_floor(game)
        monster = monster_at(game.p.x + 2, game.p.y, hp=40)
        game.mons = [monster]
        game.monster_save_throw = lambda which, m: True
        stick = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_FIRE, charges=1)

        game.zap_stick(stick, 1, 0)

        self.assertEqual(stick.charges, 0)
        self.assertTrue(game.ident.wk[rogue_sticks.WS_FIRE])
        self.assertEqual(monster.hp, 40)
        self.assertTrue(monster.running)
        self.assertTrue(any("flame whizzes past" in msg for msg in game.msgs))

    def test_rogue_544_zap_bolt_bounces_from_wall_and_can_hit_hero(self):
        # Rogue 5.4.4 sticks.c:fire_bolt() reverses direction on walls and can hit the hero.
        import rogue_sticks

        game = new_game(seed=220)
        set_open_floor(game)
        game.p.hp = 30
        game.tm[game.p.y][game.p.x + 1] = rogue.T_VWALL
        game.save_vs_magic = lambda: False
        old_roll = rogue.RNG.roll
        try:
            rogue.RNG.roll = lambda number, sides: 12
            stick = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_COLD, charges=1)
            game.zap_stick(stick, 1, 0)
        finally:
            rogue.RNG.roll = old_roll

        self.assertEqual(stick.charges, 0)
        self.assertTrue(game.ident.wk[rogue_sticks.WS_COLD])
        self.assertEqual(game.p.hp, 18)
        self.assertIn("the ice bounces", game.msgs)
        self.assertIn("you are hit by the ice", game.msgs)

    def test_rogue_544_hero_bounced_bolt_death_cause_is_bolt(self):
        # Rogue 5.4.4 sticks.c:fire_bolt() calls death('b') when hero's own bolt kills him.
        import rogue_sticks

        game = new_game(seed=228)
        set_open_floor(game)
        game.p.hp = 10
        game.tm[game.p.y][game.p.x + 1] = rogue.T_VWALL
        game.save_vs_magic = lambda: False
        old_roll = rogue.RNG.roll
        try:
            rogue.RNG.roll = lambda number, sides: 12
            stick = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_COLD, charges=1)
            game.zap_stick(stick, 1, 0)
        finally:
            rogue.RNG.roll = old_roll

        self.assertLessEqual(game.p.hp, 0)
        self.assertEqual(game.death_cause, "killed by a bolt")

    def test_rogue_544_zap_fire_bounces_off_dragon_without_damage(self):
        # Rogue 5.4.4 sticks.c:fire_bolt() prints "the flame bounces" for Dragon and does not hit_monster().
        import rogue_sticks

        game = new_game(seed=221)
        set_open_floor(game)
        dragon = monster_at(game.p.x + 2, game.p.y, sym="D", name="dragon", hp=40)
        game.mons = [dragon]
        game.monster_save_throw = lambda which, m: False
        stick = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_FIRE, charges=1)

        game.zap_stick(stick, 1, 0)

        self.assertEqual(stick.charges, 0)
        self.assertTrue(game.ident.wk[rogue_sticks.WS_FIRE])
        self.assertEqual(dragon.hp, 40)
        self.assertFalse(dragon.running)
        self.assertIn("the flame bounces", game.msgs)

    def test_rogue_544_dragon_breaths_flame_from_line_within_bolt_length(self):
        # Rogue 5.4.4 chase.c:do_chase() Dragon calls fire_bolt() with rnd(DRAGONSHOT)==0.
        game = new_game(seed=222)
        set_open_floor(game)
        game.p.x, game.p.y = 10, 10
        game.p.hp = 30
        dragon = monster_at(game.p.x + rogue.BOLT_LENGTH, game.p.y, sym="D", name="dragon", flags="")
        dragon.running = True
        game.mons = [dragon]
        game.save_vs_magic = lambda: False
        old_rnd = rogue.RNG.rnd
        old_roll = rogue.RNG.roll
        try:
            calls = []
            rogue.RNG.rnd = lambda n: calls.append(n) or 0
            rogue.RNG.roll = lambda number, sides: 12
            game.do_chase(dragon)
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.RNG.roll = old_roll

        self.assertEqual(calls, [5])
        self.assertEqual(game.p.hp, 18)
        self.assertEqual((dragon.x, dragon.y), (game.p.x + rogue.BOLT_LENGTH, game.p.y))
        self.assertIn("you are hit by the flame", game.msgs)

    def test_rogue_544_cancelled_dragon_does_not_breathe_or_roll_dragonshot(self):
        # Rogue 5.4.4 chase.c:do_chase() gates Dragon breath with !ISCANC before rnd(DRAGONSHOT).
        game = new_game(seed=223)
        set_open_floor(game)
        game.p.x, game.p.y = 10, 10
        game.p.hp = 30
        dragon = monster_at(game.p.x + rogue.BOLT_LENGTH, game.p.y, sym="D", name="dragon", flags="cancel")
        game.mons = [dragon]
        old_rnd = rogue.RNG.rnd
        try:
            calls = []
            rogue.RNG.rnd = lambda n: calls.append(n) or 0
            self.assertFalse(game.try_dragon_breath(dragon))
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(calls, [])
        self.assertEqual(game.p.hp, 30)

    def test_rogue_544_dragon_breath_death_cause_is_dragon_not_flame(self):
        # Rogue 5.4.4 sticks.c:fire_bolt() calls death(moat(start)->t_type) for monster-started bolts.
        game = new_game(seed=224)
        set_open_floor(game)
        game.p.x, game.p.y = 10, 10
        game.p.hp = 10
        dragon = monster_at(game.p.x + rogue.BOLT_LENGTH, game.p.y, sym="D", name="dragon")
        dragon.running = True
        game.mons = [dragon]
        game.save_vs_magic = lambda: False
        old_rnd = rogue.RNG.rnd
        old_roll = rogue.RNG.roll
        try:
            rogue.RNG.rnd = lambda n: 0
            rogue.RNG.roll = lambda number, sides: 12
            game.do_chase(dragon)
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.RNG.roll = old_roll

        self.assertLessEqual(game.p.hp, 0)
        self.assertEqual(game.death_cause, "killed by a dragon")

    def test_rogue_544_fire_bolt_hits_hero_standing_on_door(self):
        # Rogue 5.4.4 sticks.c:fire_bolt() does not bounce from DOOR when hero is there.
        game = new_game(seed=225)
        set_open_floor(game)
        game.p.x, game.p.y = 10, 10
        game.tm[game.p.y][game.p.x] = rogue.T_DOOR
        game.p.hp = 30
        dragon = monster_at(game.p.x + 3, game.p.y, sym="D", name="dragon")
        game.mons = [dragon]
        game.save_vs_magic = lambda: False
        old_roll = rogue.RNG.roll
        try:
            rogue.RNG.roll = lambda number, sides: 12
            hit = game.fire_bolt_from(dragon.x, dragon.y, -1, 0, "flame")
        finally:
            rogue.RNG.roll = old_roll

        self.assertTrue(hit)
        self.assertEqual(game.p.hp, 18)
        self.assertIn("you are hit by the flame", game.msgs)

    def test_rogue_544_monster_started_bolt_miss_does_not_runto_target(self):
        # Rogue 5.4.4 sticks.c:fire_bolt() calls runto() on a monster miss only when start == &hero.
        game = new_game(seed=226)
        set_open_floor(game)
        game.p.x, game.p.y = 10, 10
        game.tm[10][9] = rogue.T_VWALL
        orc = monster_at(6, 10, sym="O", name="orc")
        game.mons = [orc]
        game.monster_save_throw = lambda which, monster: True

        hit = game.fire_bolt_from(7, 10, 1, 0, "flame")

        self.assertFalse(hit)
        self.assertFalse(orc.running)
        self.assertIn("the flame whizzes past the orc", game.msgs)

    def test_rogue_544_bolt_miss_silent_for_disguised_xeroc(self):
        # Rogue 5.4.4 sticks.c:fire_bolt() suppresses miss text unless ch != 'M' or t_disguise == 'M'.
        game = new_game(seed=227)
        set_open_floor(game)
        game.p.x, game.p.y = 10, 10
        xeroc = monster_at(12, 10, sym="X", name="xeroc")
        xeroc.disguise = "!"
        game.mons = [xeroc]
        game.monster_save_throw = lambda which, monster: True

        hit = game.fire_bolt(1, 0, "flame")

        self.assertFalse(hit)
        self.assertFalse(xeroc.running)
        self.assertNotIn("the flame whizzes past the xeroc", game.msgs)

    def test_rogue_544_sticks_helper_saved_monster_miss_feedback(self):
        # Rogue 5.4.4 sticks.c:fire_bolt() saved monster miss display/runto branch.
        import rogue_sticks

        self.assertEqual(rogue_sticks.saved_monster_miss_feedback(True, False), (True, True))
        self.assertEqual(rogue_sticks.saved_monster_miss_feedback(False, False), (False, True))
        self.assertEqual(rogue_sticks.saved_monster_miss_feedback(True, True), (False, False))

    def test_rogue_544_sticks_helper_bolt_death_cause(self):
        # Rogue 5.4.4 sticks.c:fire_bolt() uses death('b') for hero-started bolt deaths.
        import rogue_sticks

        self.assertEqual(rogue_sticks.bolt_death_cause(True, None), "bolt")
        self.assertEqual(rogue_sticks.bolt_death_cause(False, "dragon"), "dragon")

    def test_rogue_544_sticks_helper_bolt_bounce_door_hero_exception(self):
        # Rogue 5.4.4 sticks.c:fire_bolt() treats DOOR under hero as normal hit space.
        import rogue_sticks

        self.assertFalse(rogue_sticks.bolt_should_bounce(True, True))
        self.assertTrue(rogue_sticks.bolt_should_bounce(True, False))
        self.assertFalse(rogue_sticks.bolt_should_bounce(False, False))

    def test_rogue_544_sticks_helper_polymorph_identification(self):
        # Rogue 5.4.4 sticks.c:WS_POLYMORPH identifies only when see_monst(tp) is true after polymorph.
        import rogue_sticks

        self.assertTrue(rogue_sticks.polymorph_identifies(True, True))
        self.assertFalse(rogue_sticks.polymorph_identifies(True, False))
        self.assertFalse(rogue_sticks.polymorph_identifies(False, True))

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

    def test_rogue_544_ring_num_and_stick_charges_require_item_isknow(self):
        # Rogue 5.4.4 things.c:nameit() calls rings.c:ring_num() and
        # sticks.c:charge_str(), which hide details without ISKNOW.
        import rogue_rings
        import rogue_sticks

        ident = rogue.IdentTable()
        ring = rogue.Item(rogue.CAT_RING, rogue_rings.R_PROTECT, ench=2, known=False)
        ident.rk[rogue_rings.R_PROTECT] = True
        self.assertEqual(ident.name(ring), "ring of protection")
        ring.known = True
        self.assertEqual(ident.name(ring), "ring of protection [+2]")

        stick = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_LIGHT, charges=12, known=False)
        ident.wtypes[rogue_sticks.WS_LIGHT] = "wand"
        ident.wmades[rogue_sticks.WS_LIGHT] = "copper"
        ident.wk[rogue_sticks.WS_LIGHT] = True
        self.assertEqual(ident.name(stick), "wand of light(copper)")
        stick.known = True
        self.assertEqual(ident.name(stick), "wand of light [12 charges](copper)")

    def test_rogue_544_potion_table_order_and_probabilities(self):
        # Rogue 5.4.4 rogue.h:P_* / MAXPOTIONS and extern.c:pot_info[].
        self.assertEqual([p["name"] for p in rogue.POTIONS], [
            "confusion", "hallucination", "poison", "gain strength",
            "see invisible", "healing", "monster detection", "magic detection",
            "raise level", "extra healing", "haste self", "restore strength",
            "blindness", "levitation",
        ])
        self.assertEqual([p["prob"] for p in rogue.POTIONS],
                         [7, 8, 8, 13, 3, 13, 6, 6, 2, 5, 5, 13, 5, 6])

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

    def test_rogue_544_scroll_monster_confusion_sets_canhuh_until_hit(self):
        # Rogue 5.4.4 scrolls.c:S_CONFUSE sets CANHUH; fight.c:attack()
        # consumes it only after a hit and gives the monster ISHUH.
        game = new_game(seed=311)
        set_open_floor(game)
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "monster confusion")
        scroll = rogue.Item(rogue.CAT_SCR, kind)
        game.p.inv.append(scroll)
        monster = monster_at(game.p.x + 1, game.p.y, hp=20, armor=-100, exp=0)
        game.mons = [monster]

        game.use_scr(scroll)

        self.assertTrue(game.p.can_confuse_monster)
        self.assertNotIn(scroll, game.p.inv)
        self.assertIn("your hands begin to glow red", game.msgs)

        game.swing_hits = lambda at_lvl, op_arm, wplus: True
        game.p_attack(monster)

        self.assertFalse(game.p.can_confuse_monster)
        self.assertGreater(monster.confused, 0)
        self.assertIn("your hands stop glowing red", game.msgs)
        self.assertIn("the hobgoblin appears confused", game.msgs)

    def test_rogue_544_scroll_monster_confusion_survives_missed_attack(self):
        # Rogue 5.4.4 fight.c:attack() clears CANHUH inside the hit branch.
        game = new_game(seed=312)
        set_open_floor(game)
        game.p.can_confuse_monster = True
        monster = monster_at(game.p.x + 1, game.p.y, hp=20, armor=100, exp=0)

        game.swing_hits = lambda at_lvl, op_arm, wplus: False
        game.p_attack(monster)

        self.assertTrue(game.p.can_confuse_monster)
        self.assertEqual(monster.confused, 0)

    def test_rogue_544_scroll_food_detection_reveals_food_and_identifies_only_when_food_exists(self):
        # Rogue 5.4.4 scrolls.c:S_FDET shows lvl_obj FOOD and sets
        # scr_info[S_FDET].oi_know only if at least one food exists.
        game = new_game(seed=313)
        set_open_floor(game)
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "food detection")
        scroll = rogue.Item(rogue.CAT_SCR, kind)
        food = rogue.Item(rogue.CAT_FOOD, 0)
        potion = rogue.Item(rogue.CAT_POT, 0)
        food.x, food.y = game.p.x + 3, game.p.y
        potion.x, potion.y = game.p.x + 4, game.p.y
        game.p.inv.append(scroll)
        game.gitems = [food, potion]
        game.visible = set()
        game.explored = set()

        game.use_scr(scroll)

        self.assertTrue(game.ident.sk[kind])
        self.assertIn((food.x, food.y), game.visible)
        self.assertIn((food.x, food.y), game.explored)
        self.assertNotIn((potion.x, potion.y), game.visible)
        self.assertIn("Your nose tingles and you smell food.", game.msgs)

    def test_rogue_544_scroll_food_detection_without_food_does_not_identify(self):
        # Rogue 5.4.4 scrolls.c:S_FDET leaves scr_info unknown when no FOOD is present.
        game = new_game(seed=314)
        set_open_floor(game)
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "food detection")
        scroll = rogue.Item(rogue.CAT_SCR, kind)
        game.p.inv.append(scroll)
        game.gitems = []

        game.use_scr(scroll)

        self.assertFalse(game.ident.sk[kind])
        self.assertIn("your nose tingles", game.msgs)

    def test_rogue_544_scroll_protect_armor_marks_armor_protected_and_blocks_rust(self):
        # Rogue 5.4.4 scrolls.c:S_PROTECT sets ISPROT but does not set scr_info[].oi_know;
        # move.c:rust_armor() then prints the instant-vanish rust message and does not lower armor.
        game = new_game(seed=315)
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "protect armor")
        scroll = rogue.Item(rogue.CAT_SCR, kind)
        armor = rogue.Item(rogue.CAT_ARM, 1, ench=0)
        game.p.arm = armor
        game.p.inv.extend([armor, scroll])
        game.p.recalc_ac()

        game.use_scr(scroll)

        self.assertFalse(game.ident.sk[kind])
        self.assertTrue(armor.protected)
        self.assertIn("your armor is covered by a shimmering gold shield", game.msgs)

        game.rust_armor()

        self.assertEqual(armor.ench, 0)
        self.assertIn("the rust vanishes instantly", game.msgs)

    def test_rogue_544_scroll_protect_armor_without_armor_does_not_identify(self):
        # Rogue 5.4.4 scrolls.c:S_PROTECT has an armor-only effect.
        game = new_game(seed=316)
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "protect armor")
        scroll = rogue.Item(rogue.CAT_SCR, kind)
        game.p.arm = None
        game.p.inv.append(scroll)

        game.use_scr(scroll)

        self.assertFalse(game.ident.sk[kind])
        self.assertIn("you feel a strange sense of loss", game.msgs)

    def test_rogue_544_scrolls_helper_protect_armor_matches_s_protect(self):
        # Rogue 5.4.4 scrolls.c:S_PROTECT sets ISPROT on current armor.
        import rogue_scrolls

        armor = rogue.Item(rogue.CAT_ARM, 1)
        self.assertTrue(rogue_scrolls.protect_armor(armor))
        self.assertTrue(armor.protected)
        self.assertFalse(rogue_scrolls.protect_armor(None))

    def test_rogue_544_scrolls_helper_remove_curse_matches_s_remove(self):
        # Rogue 5.4.4 scrolls.c:S_REMOVE uncurses only equipped armor/weapon/rings.
        import rogue_scrolls

        cursed = [rogue.Item(rogue.CAT_WPN, 0, cursed=True) for _ in range(4)]
        rogue_scrolls.remove_curse_equipment(cursed)
        self.assertFalse(any(item.cursed for item in cursed))
        rogue_scrolls.remove_curse_equipment([None])

    def test_rogue_544_scrolls_helper_monster_confusion_matches_s_confuse(self):
        # Rogue 5.4.4 scrolls.c:S_CONFUSE sets player CANHUH.
        import rogue_scrolls

        player = rogue.Player()
        self.assertFalse(player.can_confuse_monster)
        rogue_scrolls.monster_confusion(player)
        self.assertTrue(player.can_confuse_monster)

    def test_rogue_544_scrolls_helper_sleep_adds_no_command(self):
        # Rogue 5.4.4 scrolls.c:S_SLEEP uses no_command += rnd(SLEEPTIME) + 4.
        import rogue_scrolls

        player = rogue.Player()
        player.no_command = 5
        self.assertEqual(rogue_scrolls.sleep_scroll(player, lambda n: 3, rogue.SLEEPTIME), 12)
        self.assertEqual(player.no_command, 12)

    def test_rogue_544_scrolls_helper_hold_monster_matches_s_hold(self):
        # Rogue 5.4.4 scrolls.c:S_HOLD clears ISRUN and sets ISHELD within two cells.
        import rogue_scrolls

        hero = rogue.Player()
        hero.x = 10
        hero.y = 10
        near = monster_at(12, 10)
        near.running = True
        far = monster_at(13, 10)
        far.running = True
        sleeping = monster_at(9, 10)
        sleeping.running = False

        self.assertEqual(rogue_scrolls.hold_monsters(hero, [near, far, sleeping], lambda n: 7), 1)
        self.assertFalse(near.running)
        self.assertEqual(near.held, 7)
        self.assertTrue(far.running)
        self.assertEqual(sleeping.held, 0)

    def test_rogue_544_scrolls_helper_create_monster_pick_matches_s_create(self):
        # Rogue 5.4.4 scrolls.c:S_CREATE chooses candidate squares with rnd(++i) == 0.
        import rogue_scrolls

        hero = rogue.Player()
        hero.x = 10
        hero.y = 10
        calls = []
        candidates = [(9, 9), (10, 9), (11, 9)]
        pick = rogue_scrolls.choose_create_monster_pos(hero, candidates, lambda n: calls.append(n) or 0)

        self.assertEqual(calls, [1, 2, 3])
        self.assertEqual(pick, (11, 9))

    def test_rogue_544_scrolls_helper_food_detection_finds_food_positions(self):
        # Rogue 5.4.4 scrolls.c:S_FDET marks FOOD objects on the level.
        import rogue_scrolls

        food = rogue.Item(rogue.CAT_FOOD, 0)
        food.x, food.y = 3, 4
        potion = rogue.Item(rogue.CAT_POT, 0)
        potion.x, potion.y = 5, 6

        self.assertEqual(rogue_scrolls.food_detection_positions([food, potion], rogue.CAT_FOOD), [(3, 4)])
        self.assertEqual(rogue_scrolls.food_detection_positions([potion], rogue.CAT_FOOD), [])

    def test_rogue_544_scrolls_helper_magic_mapping_targets_hidden_and_traps(self):
        # Rogue 5.4.4 scrolls.c:S_MAP reveals hidden features and traps.
        import rogue_scrolls

        hidden = {(3, 4): rogue.T_DOOR, (5, 6): rogue.T_CORR}
        traps = {(7, 8): 1}

        self.assertEqual(
            rogue_scrolls.magic_mapping_targets(hidden, traps, rogue.T_TRAP),
            [((3, 4), rogue.T_DOOR), ((5, 6), rogue.T_CORR), ((7, 8), rogue.T_TRAP)],
        )

    def test_rogue_544_scrolls_helper_aggravate_monsters_runs_all(self):
        # Rogue 5.4.4 scrolls.c:S_AGGR calls misc.c:aggravate(), which runto()s all monsters.
        import rogue_scrolls

        first = monster_at(1, 1)
        second = monster_at(2, 2)
        first.held = 3
        second.scared = 4
        seen = []

        rogue_scrolls.aggravate_monsters([first, second], seen.append)

        self.assertEqual(seen, [first, second])
        self.assertEqual((first.held, second.scared), (0, 0))

    def test_rogue_544_scrolls_helper_teleport_identifies_on_room_change(self):
        # Rogue 5.4.4 scrolls.c:S_TELEP identifies only when cur_room changes.
        import rogue_scrolls

        room = object()
        self.assertFalse(rogue_scrolls.teleport_identifies(room, room))
        self.assertTrue(rogue_scrolls.teleport_identifies(room, object()))

    def test_rogue_544_scrolls_helper_identify_target_cats_matches_id_type(self):
        # Rogue 5.4.4 scrolls.c:S_ID_* uses id_type[] for whatis(TRUE, ...).
        import rogue_scrolls

        self.assertEqual(rogue_scrolls.identify_target_cats("identify potion", rogue), (rogue.CAT_POT,))
        self.assertEqual(rogue_scrolls.identify_target_cats("identify scroll", rogue), (rogue.CAT_SCR,))
        self.assertEqual(rogue_scrolls.identify_target_cats("identify weapon", rogue), (rogue.CAT_WPN,))
        self.assertEqual(rogue_scrolls.identify_target_cats("identify armor", rogue), (rogue.CAT_ARM,))
        self.assertEqual(
            rogue_scrolls.identify_target_cats("identify ring, wand or staff", rogue),
            (rogue.CAT_RING, rogue.CAT_STICK),
        )

    def test_rogue_544_hold_monster_identifies_only_when_it_holds_running_monster(self):
        # Rogue 5.4.4 scrolls.c:S_HOLD sets scr_info[S_HOLD].oi_know only when ch > 0.
        game = new_game(seed=321)
        set_open_floor(game)
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "hold monster")
        empty_scroll = rogue.Item(rogue.CAT_SCR, kind)
        game.p.inv.append(empty_scroll)

        game.use_scr(empty_scroll)

        self.assertFalse(game.ident.sk[kind])
        self.assertIn("you feel a strange sense of loss", game.msgs)

        hold_scroll = rogue.Item(rogue.CAT_SCR, kind)
        monster = monster_at(game.p.x + 1, game.p.y)
        monster.running = True
        game.p.inv.append(hold_scroll)
        game.mons = [monster]

        game.use_scr(hold_scroll)

        self.assertTrue(game.ident.sk[kind])
        self.assertGreater(monster.held, 0)
        self.assertIn("the monster freezes", game.msgs)
        self.assertNotIn("Nearby monsters freeze!", game.msgs)

        multi_scroll = rogue.Item(rogue.CAT_SCR, kind)
        second = monster_at(game.p.x + 2, game.p.y)
        monster.running = True
        second.running = True
        game.p.inv.append(multi_scroll)
        game.mons = [monster, second]

        game.use_scr(multi_scroll)

        self.assertIn("the monsters around you freeze", game.msgs)

    def test_rogue_544_enchant_weapon_does_not_identify_on_read(self):
        # Rogue 5.4.4 scrolls.c:S_ENCH enchants cur_weapon but does not set scr_info[].oi_know.
        game = new_game(seed=322)
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "enchant weapon")
        empty_scroll = rogue.Item(rogue.CAT_SCR, kind)
        game.p.wpn = None
        game.p.inv.append(empty_scroll)

        game.use_scr(empty_scroll)

        self.assertFalse(game.ident.sk[kind])
        self.assertIn("you feel a strange sense of loss", game.msgs)

        weapon = rogue.Item(rogue.CAT_WPN, 0, hit_plus=0, dam_plus=0, cursed=True)
        scroll = rogue.Item(rogue.CAT_SCR, kind)
        game.p.wpn = weapon
        game.p.inv.extend([weapon, scroll])

        game.use_scr(scroll)

        self.assertFalse(game.ident.sk[kind])
        self.assertFalse(weapon.cursed)
        self.assertIn("your mace glows blue for a moment", game.msgs)
        self.assertNotIn("Your mace glows blue!", game.msgs)

    def test_rogue_544_enchant_weapon_uses_rnd_two(self):
        # Rogue 5.4.4 scrolls.c:S_ENCH chooses hit/damage with rnd(2).
        game = new_game(seed=324)
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "enchant weapon")
        weapon = rogue.Item(rogue.CAT_WPN, 0, hit_plus=0, dam_plus=0, cursed=True)
        scroll = rogue.Item(rogue.CAT_SCR, kind)
        game.p.wpn = weapon
        game.p.inv.extend([weapon, scroll])
        old_rnd = rogue.RNG.rnd
        old_randrange = rogue.RNG.randrange
        calls = []
        try:
            rogue.RNG.rnd = lambda n: calls.append(n) or 0
            rogue.RNG.randrange = lambda n: (_ for _ in ()).throw(AssertionError("randrange used"))
            game.use_scr(scroll)
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.RNG.randrange = old_randrange

        self.assertEqual(calls, [2])
        self.assertEqual(weapon.hit_plus, 1)
        self.assertEqual(weapon.dam_plus, 0)

    def test_rogue_544_scrolls_helper_enchant_weapon_matches_s_ench(self):
        # Rogue 5.4.4 scrolls.c:S_ENCH clears ISCURSED and increments one weapon plus.
        import rogue_scrolls

        weapon = rogue.Item(rogue.CAT_WPN, 0, hit_plus=2, dam_plus=3, cursed=True)
        self.assertTrue(rogue_scrolls.enchant_weapon(weapon, lambda n: 1))
        self.assertFalse(weapon.cursed)
        self.assertEqual((weapon.hit_plus, weapon.dam_plus), (2, 4))
        self.assertFalse(rogue_scrolls.enchant_weapon(None, lambda n: 0))

    def test_rogue_544_enchant_armor_does_not_identify_on_read(self):
        # Rogue 5.4.4 scrolls.c:S_ARMOR enchants cur_armor but does not set scr_info[].oi_know.
        game = new_game(seed=323)
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "enchant armor")
        empty_scroll = rogue.Item(rogue.CAT_SCR, kind)
        game.p.arm = None
        game.p.inv.append(empty_scroll)

        game.use_scr(empty_scroll)

        self.assertFalse(game.ident.sk[kind])
        self.assertIn("you feel a strange sense of loss", game.msgs)

        armor = rogue.Item(rogue.CAT_ARM, 0, ench=0, cursed=True)
        scroll = rogue.Item(rogue.CAT_SCR, kind)
        game.p.arm = armor
        game.p.inv.extend([armor, scroll])

        game.use_scr(scroll)

        self.assertFalse(game.ident.sk[kind])
        self.assertFalse(armor.cursed)
        self.assertEqual(armor.ench, 1)
        self.assertIn("your armor glows silver for a moment", game.msgs)
        self.assertNotIn("Your armor glows!", game.msgs)

    def test_rogue_544_scrolls_helper_enchant_armor_matches_s_armor(self):
        # Rogue 5.4.4 scrolls.c:S_ARMOR decrements o_arm and clears ISCURSED.
        import rogue_scrolls

        armor = rogue.Item(rogue.CAT_ARM, 0, ench=2, cursed=True)
        self.assertTrue(rogue_scrolls.enchant_armor(armor))
        self.assertFalse(armor.cursed)
        self.assertEqual(armor.ench, 3)
        self.assertFalse(rogue_scrolls.enchant_armor(None))

    def test_rogue_544_teleport_scroll_identifies_only_when_room_changes(self):
        # Rogue 5.4.4 scrolls.c:S_TELEP calls wizard.c:teleport(), which emits no log
        # and clears ISHELD/vf_hit when teleporting away from a Venus Flytrap.
        game = new_game(seed=324)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        room_a = rogue.Room(1, 1, 8, 6)
        room_b = rogue.Room(20, 1, 8, 6)
        game.rooms = [room_a, room_b]
        for room in game.rooms:
            for y in range(room.y + 1, room.y + room.h - 1):
                for x in range(room.x + 1, room.x + room.w - 1):
                    game.tm[y][x] = rogue.T_FLOOR
        game.p.x, game.p.y = room_a.inner()
        flytrap = monster_at(game.p.x + 1, game.p.y, "F", "venus flytrap")
        flytrap.vf_hit = 4
        game.p.held_by = flytrap
        game.mons = [flytrap]
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "teleportation")
        same_room_scroll = rogue.Item(rogue.CAT_SCR, kind)
        game.p.inv.append(same_room_scroll)
        game.usable_rooms = lambda: [room_a]
        game.random_room_tile = lambda room, tiles: room.inner()

        game.use_scr(same_room_scroll)

        self.assertFalse(game.ident.sk[kind])
        self.assertIs(game.room_at(game.p.x, game.p.y), room_a)
        self.assertNotIn("You are teleported!", game.msgs)

        other_room_scroll = rogue.Item(rogue.CAT_SCR, kind)
        game.p.inv.append(other_room_scroll)
        game.p.x, game.p.y = room_a.inner()
        game.p.held_by = flytrap
        flytrap.vf_hit = 4
        flytrap.damage_expr = "4x1"
        game.p.no_move = 5
        game.dashing = True
        game.dash_steps = 3
        game.usable_rooms = lambda: [room_b]

        game.use_scr(other_room_scroll)

        self.assertTrue(game.ident.sk[kind])
        self.assertIs(game.room_at(game.p.x, game.p.y), room_b)
        self.assertIsNone(game.p.held_by)
        self.assertEqual(flytrap.vf_hit, 0)
        self.assertEqual(flytrap.damage_expr, "0x0")
        self.assertEqual(game.p.no_move, 0)
        self.assertFalse(game.dashing)
        self.assertEqual(game.dash_steps, 0)
        self.assertNotIn("You are teleported!", game.msgs)

    def test_rogue_544_create_monster_uses_eight_neighbors_and_does_not_identify(self):
        # Rogue 5.4.4 scrolls.c:S_CREATE scans the full 3x3 ring and does not set oi_know.
        game = new_game(seed=325)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        game.rooms = [rogue.Room(1, 1, 8, 8)]
        game.p.x, game.p.y = 4, 4
        game.tm[game.p.y][game.p.x] = rogue.T_FLOOR
        game.tm[game.p.y - 1][game.p.x - 1] = rogue.T_FLOOR
        game.mons = []
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "create monster")
        scroll = rogue.Item(rogue.CAT_SCR, kind)
        game.p.inv.append(scroll)

        game.use_scr(scroll)

        self.assertFalse(game.ident.sk[kind])
        self.assertEqual([(mo.x, mo.y) for mo in game.mons], [(game.p.x - 1, game.p.y - 1)])
        self.assertNotIn("A monster appears!", game.msgs)

    def test_rogue_544_create_monster_uses_reservoir_candidate_pick(self):
        # Rogue 5.4.4 scrolls.c:S_CREATE chooses neighbors with rnd(++i) == 0.
        class CreateMonsterRng:
            def __init__(self):
                self.rnd_calls = []

            def rnd(self, n):
                self.rnd_calls.append(n)
                return 0 if n in (1, 8) else 1

            def choice(self, seq):
                return seq[0]

            def roll(self, number, sides):
                return number

        game = new_game(seed=331)
        set_open_floor(game)
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "create monster")
        scroll = rogue.Item(rogue.CAT_SCR, kind)
        game.p.inv.append(scroll)
        old_rng = rogue.RNG
        test_rng = CreateMonsterRng()
        rogue.RNG = test_rng
        try:
            game.use_scr(scroll)
        finally:
            rogue.RNG = old_rng

        self.assertEqual(test_rng.rnd_calls[:8], [1, 2, 3, 4, 5, 6, 7, 8])
        self.assertEqual([(mo.x, mo.y) for mo in game.mons], [(game.p.x + 1, game.p.y + 1)])

    def test_rogue_544_create_monster_uses_randmonster_false_table(self):
        # Rogue 5.4.4 scrolls.c:S_CREATE calls monsters.c:randmonster(FALSE).
        class CreateMonsterRng:
            def __init__(self):
                self.rolls = iter([0, 0, 2])

            def rnd(self, n):
                return next(self.rolls)

            def choice(self, seq):
                raise AssertionError("choice used")

            def roll(self, dice, sides):
                return dice

        game = new_game(seed=337)
        set_open_floor(game)
        game.p.depth = 1
        px, py = game.p.x, game.p.y
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                game.tm[py + dy][px + dx] = rogue.T_VOID
        game.tm[py - 1][px - 1] = rogue.T_FLOOR
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "create monster")
        scroll = rogue.Item(rogue.CAT_SCR, kind)
        game.p.inv.append(scroll)
        old_rng = rogue.RNG
        rogue.RNG = CreateMonsterRng()
        try:
            game.use_scr(scroll)
        finally:
            rogue.RNG = old_rng

        self.assertEqual([mo.sym for mo in game.mons], ["B"])

    def test_rogue_544_random_monster_spec_uses_randmonster_false_table(self):
        # Rogue 5.4.4 rooms.c:do_rooms() uses monsters.c:randmonster(FALSE).
        class MonsterRng:
            def __init__(self):
                self.rolls = iter([0, 2])

            def rnd(self, n):
                return next(self.rolls)

            def choice(self, seq):
                raise AssertionError("choice used")

        game = new_game(seed=338)
        old_rng = rogue.RNG
        rogue.RNG = MonsterRng()
        try:
            spec = game.random_monster_spec(1)
        finally:
            rogue.RNG = old_rng

        self.assertEqual(spec.sym, "B")

    def test_rogue_544_spawn_wanderer_uses_randmonster_true_table(self):
        # Rogue 5.4.4 monsters.c:wanderer() uses randmonster(TRUE).
        class WanderRng:
            def __init__(self):
                self.rolls = iter([9, 6])

            def rnd(self, n):
                return next(self.rolls)

            def choice(self, seq):
                return seq[0]

            def roll(self, dice, sides):
                return dice

        game = new_game(seed=339)
        set_open_floor(game)
        game.p.depth = 2
        game.mons = []
        game.wanderer_floor_candidates = lambda: [(game.p.x + 3, game.p.y)]
        old_rng = rogue.RNG
        rogue.RNG = WanderRng()
        try:
            self.assertTrue(game.spawn_wanderer())
        finally:
            rogue.RNG = old_rng

        self.assertEqual([mo.sym for mo in game.mons], ["B"])

    def test_rogue_544_effect_scrolls_do_not_directly_identify_without_oi_know(self):
        # Rogue 5.4.4 scrolls.c:S_CONFUSE/S_SCARE/S_REMOVE/S_AGGR do not assign scr_info[].oi_know.
        cases = [
            ("monster confusion", lambda g: None),
            ("scare monster", lambda g: g.mons.append(monster_at(g.p.x + 1, g.p.y))),
            ("remove curse", lambda g: setattr(g.p.wpn, "cursed", True)),
            ("aggravate monsters", lambda g: g.mons.append(monster_at(g.p.x + 1, g.p.y))),
        ]
        for name, setup in cases:
            with self.subTest(name=name):
                game = new_game(seed=326)
                set_open_floor(game)
                kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == name)
                scroll = rogue.Item(rogue.CAT_SCR, kind)
                game.p.inv.append(scroll)
                setup(game)

                game.use_scr(scroll)

                self.assertFalse(game.ident.sk[kind])

    def test_rogue_544_reading_scare_monster_only_laughs(self):
        # Rogue 5.4.4 scrolls.c:S_SCARE has no monster scare effect when read.
        game = new_game(seed=335)
        set_open_floor(game)
        monster = monster_at(game.p.x + 1, game.p.y)
        game.mons = [monster]
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "scare monster")
        scroll = rogue.Item(rogue.CAT_SCR, kind)
        game.p.inv.append(scroll)

        game.use_scr(scroll)

        self.assertEqual(monster.scared, 0)
        self.assertIn("you hear maniacal laughter in the distance", game.msgs)

    def test_rogue_544_scroll_effects_use_original_messages(self):
        # Rogue 5.4.4 scrolls.c:read_scroll() messages for S_SLEEP/S_SCARE/S_REMOVE/S_AGGR/S_MAP.
        cases = [
            ("sleep", "you fall asleep", "You fall asleep."),
            ("scare monster", "you hear maniacal laughter in the distance", "Maniacal laughter echoes."),
            ("remove curse", "you feel as if somebody is watching over you", "Your equipment feels lighter."),
            ("aggravate monsters", "you hear a high pitched humming noise", "You hear a humming noise."),
            ("magic mapping", "oh, now this scroll has a map on it", "A map appears in your mind!"),
        ]
        for name, expected, old in cases:
            with self.subTest(name=name):
                game = new_game(seed=330)
                set_open_floor(game)
                kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == name)
                scroll = rogue.Item(rogue.CAT_SCR, kind)
                game.p.inv.append(scroll)
                if name == "remove curse":
                    game.p.wpn.cursed = True

                game.use_scr(scroll)

                self.assertIn(expected, game.msgs)
                self.assertNotIn(old, game.msgs)

    def test_rogue_544_sleep_scroll_stops_running(self):
        # Rogue 5.4.4 scrolls.c:S_SLEEP clears player ISRUN after setting no_command.
        game = new_game(seed=327)
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "sleep")
        scroll = rogue.Item(rogue.CAT_SCR, kind)
        game.p.inv.append(scroll)
        game.dashing = True
        game.dash_d = (1, 0)
        game.dash_steps = 2

        game.use_scr(scroll)

        self.assertTrue(game.ident.sk[kind])
        self.assertGreater(game.p.no_command, 0)
        self.assertFalse(game.dashing)

    def test_rogue_544_sleep_scroll_adds_to_existing_no_command(self):
        # Rogue 5.4.4 scrolls.c:S_SLEEP uses no_command += rnd(SLEEPTIME) + 4.
        game = new_game(seed=328)
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "sleep")
        scroll = rogue.Item(rogue.CAT_SCR, kind)
        game.p.inv.append(scroll)
        game.p.no_command = 10
        old_rng = rogue.RNG
        class SleepRng:
            def rnd(self, n):
                return 2

            def randint(self, a, b):
                return 6
        rogue.RNG = SleepRng()
        try:
            game.use_scr(scroll)
        finally:
            rogue.RNG = old_rng

        self.assertEqual(game.p.no_command, 16)

    def test_rogue_544_magic_mapping_reveals_hidden_features_and_traps(self):
        # Rogue 5.4.4 scrolls.c:S_MAP turns hidden DOOR/PASSAGE/TRAP into real mapped terrain.
        game = new_game(seed=329)
        set_open_floor(game)
        px, py = game.p.x, game.p.y
        game.hidden_tiles[(px + 1, py)] = rogue.T_DOOR
        game.tm[py][px + 1] = rogue.T_VWALL
        game.hidden_tiles[(px, py + 1)] = rogue.T_CORR
        game.tm[py + 1][px] = rogue.T_VOID
        game.traps[(px - 1, py)] = 1
        game.tm[py][px - 1] = rogue.T_FLOOR
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "magic mapping")
        scroll = rogue.Item(rogue.CAT_SCR, kind)
        game.p.inv.append(scroll)

        game.use_scr(scroll)

        self.assertTrue(game.ident.sk[kind])
        self.assertEqual(game.tm[py][px + 1], rogue.T_DOOR)
        self.assertEqual(game.tm[py + 1][px], rogue.T_CORR)
        self.assertEqual(game.tm[py][px - 1], rogue.T_TRAP)
        self.assertNotIn((px + 1, py), game.hidden_tiles)
        self.assertIn((px + 1, py), game.explored)

    def test_rogue_544_scroll_table_has_five_identify_types(self):
        # Rogue 5.4.4 rogue.h:S_* / MAXSCROLLS and extern.c:scr_info[].
        self.assertEqual(len(rogue.SCROLLS), 18)
        self.assertEqual([s["name"] for s in rogue.SCROLLS], [
            "monster confusion", "magic mapping", "hold monster", "sleep",
            "enchant armor", "identify potion", "identify scroll",
            "identify weapon", "identify armor", "identify ring, wand or staff",
            "scare monster", "food detection", "teleportation",
            "enchant weapon", "create monster", "remove curse",
            "aggravate monsters", "protect armor",
        ])
        self.assertEqual([s["prob"] for s in rogue.SCROLLS],
                         [7, 4, 2, 3, 7, 10, 10, 6, 7, 10, 3, 2, 5, 8, 4, 7, 3, 2])

    def test_rogue_544_identify_potion_scroll_only_identifies_matching_type(self):
        # Rogue 5.4.4 scrolls.c:S_ID_POTION calls whatis(TRUE, POTION).
        # Now interactive: use_scr() sets up picker, item_confirm() completes it.
        game = new_game(seed=317)
        pot = rogue.Item(rogue.CAT_POT, 0)
        other_scroll = rogue.Item(rogue.CAT_SCR, 0)
        ident_kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "identify potion")
        ident_scroll = rogue.Item(rogue.CAT_SCR, ident_kind)
        game.p.inv.extend([ident_scroll, pot, other_scroll])
        game.ident.pk[pot.kind] = False
        game.ident.sk[other_scroll.kind] = False

        pending = game.use_scr(ident_scroll)
        # use_scr returns True and sets up picker when unidentified items exist.
        self.assertTrue(pending)
        self.assertEqual(game.cact, "Identify")
        self.assertIn(pot, game.fitems)
        self.assertNotIn(other_scroll, game.fitems)
        # Simulate player confirming selection of the potion.
        game.icur = game.fitems.index(pot)
        game.item_confirm()

        self.assertTrue(game.ident.sk[ident_kind])
        self.assertTrue(game.ident.pk[pot.kind])
        self.assertFalse(game.ident.sk[other_scroll.kind])
        self.assertIn("this scroll is an identify potion scroll", game.msgs)

    def test_rogue_544_identify_scroll_is_consumed_before_target_selection(self):
        # Rogue 5.4.4 scrolls.c:read_scroll() calls leave_pack() before whatis().
        game = new_game(seed=336)
        pot = rogue.Item(rogue.CAT_POT, 0)
        ident_kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "identify potion")
        ident_scroll = rogue.Item(rogue.CAT_SCR, ident_kind)
        game.p.inv.extend([ident_scroll, pot])
        game.ident.pk[pot.kind] = False

        pending = game.use_scr(ident_scroll)

        self.assertTrue(pending)
        self.assertNotIn(ident_scroll, game.p.inv)
        self.assertIn(pot, game.fitems)

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
            player.has_amulet = True
            player.food = 100
            player.hunger()
            self.assertEqual(player.food, 99)
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

    def test_rogue_544_eat_ration_can_taste_awful_and_add_exp(self):
        # Rogue 5.4.4 misc.c:eat() gives food ration a rnd(100)>70 awful branch with +1 exp.
        game = new_game(seed=203)
        ration = rogue.Item(rogue.CAT_FOOD, 0)
        game.p.inv.append(ration)
        game.p.food = -5
        game.p.exp = 0
        old_randrange = rogue.RNG.randrange
        old_rnd = rogue.RNG.rnd
        try:
            rolls = iter([0, 71])
            rogue.RNG.rnd = lambda n: next(rolls)
            rogue.RNG.randrange = lambda n: (_ for _ in ()).throw(AssertionError("randrange used"))
            game.eat(ration)
        finally:
            rogue.RNG.randrange = old_randrange
            rogue.RNG.rnd = old_rnd

        self.assertEqual(game.p.food, rogue.HUNGERTIME - 200)
        self.assertEqual(game.p.state, "normal")
        self.assertEqual(game.p.exp, 1)
        self.assertIn("yuk, this food tastes awful", game.msgs)
        self.assertNotIn(ration, game.p.inv)

    def test_rogue_544_eat_slime_mold_uses_yummy_fruit_message(self):
        # Rogue 5.4.4 misc.c:eat() uses "my, that was a yummy %s" for slime-mold.
        game = new_game(seed=204)
        slime = rogue.Item(rogue.CAT_FOOD, 1)
        game.p.inv.append(slime)

        game.eat(slime)

        self.assertIn("my, that was a yummy slime-mold", game.msgs)
        self.assertNotIn(slime, game.p.inv)

    def test_rogue_544_game_eat_uses_rnd_for_food_amount(self):
        # Rogue 5.4.4 misc.c:eat() adds HUNGERTIME - 200 + rnd(400).
        game = new_game(seed=205)
        ration = rogue.Item(rogue.CAT_FOOD, 0)
        game.p.inv.append(ration)
        initial_food = game.p.food
        old_rnd = rogue.RNG.rnd
        old_randrange = rogue.RNG.randrange
        calls = []
        try:
            def rnd(n):
                calls.append(n)
                return 0 if n == 400 else 70

            rogue.RNG.rnd = rnd
            rogue.RNG.randrange = lambda n: (_ for _ in ()).throw(AssertionError("randrange used"))
            game.eat(ration)
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.RNG.randrange = old_randrange

        self.assertEqual(calls, [400, 100])
        self.assertEqual(game.p.food, min(initial_food + rogue.HUNGERTIME - 200, rogue.STOMACHSIZE))

    def test_rogue_544_food_helper_eat_matches_misc_c_branches(self):
        # Rogue 5.4.4 misc.c:eat() food amount and ration/slime-mold outcome live in rogue_food.py.
        import rogue_food

        amount = lambda n: 0
        awful = lambda n: 71
        good = lambda n: 70

        self.assertEqual(
            rogue_food.eat_food(-5, 0, amount, awful, rogue.HUNGERTIME, rogue.STOMACHSIZE),
            (rogue.HUNGERTIME - 200, "awful", 1),
        )
        self.assertEqual(
            rogue_food.eat_food(rogue.STOMACHSIZE, 0, amount, good, rogue.HUNGERTIME, rogue.STOMACHSIZE),
            (rogue.STOMACHSIZE, "good", 0),
        )
        self.assertEqual(
            rogue_food.eat_food(100, 1, amount, awful, rogue.HUNGERTIME, rogue.STOMACHSIZE),
            (100 + rogue.HUNGERTIME - 200, "slime-mold", 0),
        )

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

    def test_rogue_544_potion_see_invisible_reveals_phantom_for_spread_seeduration(self):
        # Rogue 5.4.4 potions.c:do_pot(P_SEEINVIS) sets CANSEE for misc.c:spread(SEEDURATION).
        game = new_game(seed=207)
        set_open_floor(game)
        phantom = monster_at(game.p.x + 1, game.p.y, "P", "phantom", flags="invis")
        game.mons = [phantom]
        game.visible.add((phantom.x, phantom.y))
        potion_kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "see invisible")
        potion = rogue.Item(rogue.CAT_POT, potion_kind)
        game.p.inv.append(potion)

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 7
            self.assertFalse(game.can_see_monster(phantom))
            game.use_pot(potion)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertTrue(game.can_see_monster(phantom))
        self.assertEqual(game.p.see_invisible, rogue.SEEDURATION - rogue.SEEDURATION // 20 + 7)
        self.assertEqual(game.fuses.remaining("unsee"), rogue.SEEDURATION - rogue.SEEDURATION // 20 + 7)
        # Rogue 5.4.4 potions.c P_SEEINVIS/p_actions uses prbuf with extern.c fruit.
        self.assertIn("this potion tastes like slime-mold juice", game.msgs)
        self.assertNotIn("You can see invisible monsters.", game.msgs)
        self.assertNotIn(potion, game.p.inv)

    def test_rogue_544_potion_knowit_flags_follow_quaff_branches(self):
        # Rogue 5.4.4 potions.c:quaff()/do_pot(): P_SEEINVIS knowit=FALSE,
        # P_MFIND does not set oi_know, while P_HASTE sets pot_info[].oi_know.
        game = new_game(seed=318)
        set_open_floor(game)

        see = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "see invisible")
        mfind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "monster detection")
        haste = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "haste self")
        see_pot = rogue.Item(rogue.CAT_POT, see)
        mfind_pot = rogue.Item(rogue.CAT_POT, mfind)
        haste_pot = rogue.Item(rogue.CAT_POT, haste)
        game.p.inv.extend([see_pot, mfind_pot, haste_pot])

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 0
            game.use_pot(see_pot)
            game.use_pot(mfind_pot)
            game.use_pot(haste_pot)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertFalse(game.ident.pk[see])
        self.assertFalse(game.ident.pk[mfind])
        self.assertTrue(game.ident.pk[haste])

    def test_rogue_544_restore_strength_potion_does_not_identify_on_quaff(self):
        # Rogue 5.4.4 potions.c:P_RESTORE restores strength but does not set pot_info[].oi_know.
        game = new_game(seed=322)
        set_open_floor(game)
        kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "restore strength")
        potion = rogue.Item(rogue.CAT_POT, kind)
        game.p.inv.append(potion)
        game.p.max_st = 16
        game.p.st = 9

        game.use_pot(potion)

        self.assertEqual(game.p.st, 16)
        self.assertFalse(game.ident.pk[kind])
        self.assertIn("hey, this tastes great.  It make you feel warm all over", game.msgs)
        self.assertNotIn("You feel warm all over.", game.msgs)
        self.assertNotIn(potion, game.p.inv)

    def test_rogue_544_restore_strength_does_not_lower_strength_above_max(self):
        # Rogue 5.4.4 potions.c:P_RESTORE only raises pstats.s_str when below max_stats.s_str.
        import rogue_rings

        game = new_game(seed=324)
        set_open_floor(game)
        kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "restore strength")
        potion = rogue.Item(rogue.CAT_POT, kind)
        game.p.inv.append(potion)
        game.p.ring_l = rogue.Item(rogue.CAT_RING, rogue_rings.R_ADDSTR, ench=2)
        game.p.max_st = 18
        game.p.st = 20

        game.use_pot(potion)

        self.assertEqual(game.p.st, 20)
        self.assertEqual(game.p.max_st, 18)
        self.assertFalse(game.ident.pk[kind])

    def test_rogue_544_gain_strength_potion_uses_original_message(self):
        # Rogue 5.4.4 potions.c:P_STRENGTH sets oi_know and says the bulging muscles message.
        game = new_game(seed=323)
        set_open_floor(game)
        kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "gain strength")
        potion = rogue.Item(rogue.CAT_POT, kind)
        game.p.inv.append(potion)

        game.use_pot(potion)

        self.assertEqual(game.p.st, 17)
        self.assertTrue(game.ident.pk[kind])
        self.assertIn("you feel stronger, now.  What bulging muscles!", game.msgs)
        self.assertNotIn("Str +1!", game.msgs)
        self.assertNotIn(potion, game.p.inv)

    def test_rogue_544_monster_detection_without_monsters_uses_feeling_message(self):
        # Rogue 5.4.4 potions.c:P_MFIND calls turn_see(FALSE), then choose_str("normal", "strange") if none appear.
        game = new_game(seed=319)
        set_open_floor(game)
        kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "monster detection")
        potion = rogue.Item(rogue.CAT_POT, kind)
        game.p.inv.append(potion)
        game.mons = []

        game.use_pot(potion)

        self.assertFalse(game.ident.pk[kind])
        self.assertIn("you have a strange feeling for a moment, then it passes", game.msgs)
        self.assertNotIn("You sense monsters.", game.msgs)

    def test_rogue_544_magic_detection_sees_monster_pack_magic(self):
        # Rogue 5.4.4 potions.c:P_TFIND scans mlist t_pack with is_magic().
        import rogue_rings

        game = new_game(seed=320)
        set_open_floor(game)
        kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "magic detection")
        potion = rogue.Item(rogue.CAT_POT, kind)
        food = rogue.Item(rogue.CAT_FOOD, 0)
        food.x, food.y = game.p.x + 2, game.p.y
        monster = monster_at(game.p.x + 4, game.p.y)
        monster.pack = [rogue.Item(rogue.CAT_RING, rogue_rings.R_PROTECT)]
        game.p.inv.append(potion)
        game.gitems = [food]
        game.mons = [monster]
        game.visible = set()
        game.explored = set()

        game.use_pot(potion)

        self.assertTrue(game.ident.pk[kind])
        self.assertIn((monster.x, monster.y), game.visible)
        self.assertIn((monster.x, monster.y), game.explored)
        self.assertNotIn((food.x, food.y), game.visible)

    def test_rogue_544_magic_detection_without_magic_uses_feeling_message(self):
        # Rogue 5.4.4 potions.c:P_TFIND uses choose_str("normal", "strange") when no magic is found.
        game = new_game(seed=321)
        set_open_floor(game)
        kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "magic detection")
        potion = rogue.Item(rogue.CAT_POT, kind)
        food = rogue.Item(rogue.CAT_FOOD, 0)
        food.x, food.y = game.p.x + 2, game.p.y
        game.p.inv.append(potion)
        game.gitems = [food]
        game.mons = []

        game.use_pot(potion)

        self.assertFalse(game.ident.pk[kind])
        self.assertIn("you have a strange feeling for a moment, then it passes", game.msgs)
        self.assertNotIn("You sense magic.", game.msgs)

    def test_rogue_544_raise_level_potion_uses_e_levels_and_original_message(self):
        # Rogue 5.4.4 extern.c:e_levels[] and potions.c:raise_level() set exp to e_levels[level-1]+1.
        game = new_game(seed=325)
        set_open_floor(game)
        kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "raise level")
        potion = rogue.Item(rogue.CAT_POT, kind)
        game.p.inv.append(potion)
        game.p.level = 10
        game.p.exp = 5200

        old_randint = rogue.RNG.randint
        try:
            rogue.RNG.randint = lambda a, b: 4
            game.use_pot(potion)
        finally:
            rogue.RNG.randint = old_randint

        self.assertEqual(game.p.level, 11)
        self.assertEqual(game.p.exp, 5201)
        self.assertEqual(rogue.Player.EXP_T[11], 13000)
        self.assertTrue(game.ident.pk[kind])
        self.assertIn("you suddenly feel much more skillful", game.msgs)
        self.assertIn("welcome to level 11", game.msgs)
        self.assertNotIn("You rise to level 11!", game.msgs)

    def test_rogue_544_raise_level_potion_uses_check_level_d10_hp_gain(self):
        # Rogue 5.4.4 potions.c:raise_level() calls misc.c:check_level(), which rolls delta d10 hp.
        game = new_game(seed=326)
        kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "raise level")
        potion = rogue.Item(rogue.CAT_POT, kind)
        game.p.inv.append(potion)
        game.p.level = 3
        game.p.exp = 20
        game.p.hp = 12
        game.p.max_hp = 12
        calls = []
        old_roll = rogue.RNG.roll
        try:
            rogue.RNG.roll = lambda number, sides: calls.append((number, sides)) or 9
            game.use_pot(potion)
        finally:
            rogue.RNG.roll = old_roll

        self.assertEqual(game.p.level, 4)
        self.assertEqual(game.p.exp, 41)
        self.assertEqual((game.p.hp, game.p.max_hp), (21, 21))
        self.assertEqual(calls, [(1, 10)])

    def test_rogue_544_do_pot_does_not_forget_known_confusion_while_hallucinating(self):
        # Rogue 5.4.4 potions.c:do_pot() only assigns oi_know when it is not already known.
        game = new_game(seed=319)
        set_open_floor(game)
        confusion = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "confusion")
        potion = rogue.Item(rogue.CAT_POT, confusion)
        game.p.inv.append(potion)
        game.p.hallucinating = 10
        game.ident.pk[confusion] = True

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 0
            game.use_pot(potion)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertTrue(game.ident.pk[confusion])

    def test_rogue_544_potion_see_invisible_lengthens_unsee_fuse(self):
        # Rogue 5.4.4 potions.c:do_pot(P_SEEINVIS) calls lengthen(unsee, spread(SEEDURATION)).
        game = new_game(seed=312)
        set_open_floor(game)
        potion_kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "see invisible")
        first = rogue.Item(rogue.CAT_POT, potion_kind)
        second = rogue.Item(rogue.CAT_POT, potion_kind)
        game.p.inv.extend([first, second])
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 0
            game.use_pot(first)
            game.use_pot(second)
        finally:
            rogue.RNG.rnd = old_rnd

        duration = rogue.SEEDURATION - rogue.SEEDURATION // 20
        self.assertEqual(game.p.see_invisible, duration * 2)
        self.assertEqual(game.fuses.remaining("unsee"), duration * 2)

    def test_rogue_544_potion_see_invisible_expires_without_ring(self):
        # Rogue 5.4.4 daemons.c:unsee clears CANSEE after the P_SEEINVIS fuse expires.
        game = new_game(seed=208)
        set_open_floor(game)
        phantom = monster_at(game.p.x + 1, game.p.y, "P", "phantom", flags="invis")
        game.mons = [phantom]
        game.visible.add((phantom.x, phantom.y))
        game.p.see_invisible = 1

        self.assertTrue(game.can_see_monster(phantom))
        game.end_turn()

        self.assertEqual(game.p.see_invisible, 0)
        self.assertEqual(game.fuses.remaining("unsee"), 0)
        self.assertFalse(game.can_see_monster(phantom))

    def test_rogue_544_potion_see_invisible_calls_sight_when_blind(self):
        # Rogue 5.4.4 potions.c:P_SEEINVIS calls daemons.c:sight() after invis_on().
        game = new_game(seed=209)
        set_open_floor(game)
        potion_kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "see invisible")
        potion = rogue.Item(rogue.CAT_POT, potion_kind)
        game.p.inv.append(potion)
        game.p.blind = 20

        game.use_pot(potion)

        self.assertEqual(game.p.blind, 0)
        self.assertIn("the veil of darkness lifts", game.msgs)

    def test_rogue_544_potion_confusion_uses_unconfuse_fuse(self):
        # Rogue 5.4.4 potions.c:do_pot(P_CONFUSE) uses fuse/lengthen(unconfuse, spread(HUHDURATION)).
        game = new_game(seed=315)
        set_open_floor(game)
        potion_kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "confusion")
        first = rogue.Item(rogue.CAT_POT, potion_kind)
        second = rogue.Item(rogue.CAT_POT, potion_kind)
        game.p.inv.extend([first, second])
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            game.use_pot(first)
            game.use_pot(second)
        finally:
            rogue.RNG.rnd = old_rnd

        duration = rogue.HUHDURATION - rogue.HUHDURATION // 20 + 1
        self.assertEqual(game.p.confused, duration * 2)
        self.assertEqual(game.fuses.remaining("unconfuse"), duration * 2)
        self.assertIn("wait, what's going on here. Huh? What? Who?", game.msgs)

        game.p.confused = 1
        game.fuses.extinguish("unconfuse")
        game.fuses.fuse("unconfuse", 1, rogue.rogue_daemons.AFTER)
        game.end_turn()

        self.assertEqual(game.p.confused, 0)
        self.assertEqual(game.fuses.remaining("unconfuse"), 0)
        self.assertIn("you feel less confused now", game.msgs)

    def test_rogue_544_potion_blindness_uses_sight_fuse(self):
        # Rogue 5.4.4 potions.c:do_pot(P_BLIND) uses fuse/lengthen(sight, spread(SEEDURATION)).
        game = new_game(seed=316)
        set_open_floor(game)
        potion_kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "blindness")
        first = rogue.Item(rogue.CAT_POT, potion_kind)
        second = rogue.Item(rogue.CAT_POT, potion_kind)
        game.p.inv.extend([first, second])
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 0
            game.use_pot(first)
            game.use_pot(second)
        finally:
            rogue.RNG.rnd = old_rnd

        duration = rogue.SEEDURATION - rogue.SEEDURATION // 20
        self.assertEqual(game.p.blind, duration * 2)
        self.assertEqual(game.fuses.remaining("sight"), duration * 2)
        self.assertIn("a cloak of darkness falls around you", game.msgs)

        game.p.blind = 1
        game.fuses.extinguish("sight")
        game.fuses.fuse("sight", 1, rogue.rogue_daemons.AFTER)
        game.end_turn()

        self.assertEqual(game.p.blind, 0)
        self.assertEqual(game.fuses.remaining("sight"), 0)
        self.assertIn("the veil of darkness lifts", game.msgs)

    def test_rogue_544_daemon_fuse_lengthen_extinguish_and_after_tick(self):
        # Rogue 5.4.4 daemon.c:fuse()/lengthen()/extinguish()/do_fuses(AFTER).
        import rogue_daemons

        fuses = rogue_daemons.FuseList()
        fuses.fuse("nohaste", 2, rogue_daemons.AFTER)
        self.assertEqual(fuses.tick(rogue_daemons.BEFORE), [])
        self.assertEqual(fuses.tick(rogue_daemons.AFTER), [])
        fuses.lengthen("nohaste", 2)
        self.assertEqual(fuses.remaining("nohaste"), 3)
        self.assertEqual(fuses.tick(rogue_daemons.AFTER), [])
        fuses.extinguish("nohaste")
        self.assertEqual(fuses.tick(rogue_daemons.AFTER), [])
        self.assertEqual(fuses.remaining("nohaste"), 0)

    def test_rogue_544_daemon_table_keeps_duplicate_slots(self):
        # Rogue 5.4.4 daemon.c:start_daemon()/kill_daemon() use slots, not a unique map.
        import rogue_daemons

        daemons = rogue_daemons.DaemonList()
        daemons.start("rollwand", rogue_daemons.BEFORE)
        daemons.start("rollwand", rogue_daemons.BEFORE)
        self.assertEqual(daemons.tick(rogue_daemons.BEFORE), ["rollwand", "rollwand"])

        daemons.kill("rollwand")
        self.assertEqual(daemons.tick(rogue_daemons.BEFORE), ["rollwand"])

    def test_rogue_544_fuse_table_keeps_duplicate_slots(self):
        # Rogue 5.4.4 daemon.c:fuse()/extinguish() use slots, not a unique map.
        import rogue_daemons

        fuses = rogue_daemons.FuseList()
        fuses.fuse("swander", 1, rogue_daemons.BEFORE)
        fuses.fuse("swander", 1, rogue_daemons.BEFORE)
        fuses.extinguish("swander")

        self.assertEqual(fuses.tick(rogue_daemons.BEFORE), ["swander"])

    def test_rogue_544_daemon_and_fuse_share_maxdaemon_slots(self):
        # Rogue 5.4.4 daemon.c stores daemons and fuses in one MAXDAEMONS d_list.
        import rogue_daemons

        actions = rogue_daemons.DelayedActionTable()
        for idx in range(rogue_daemons.MAXDAEMONS):
            actions.daemons.start(f"daemon_{idx}", rogue_daemons.AFTER)

        actions.fuses.fuse("blocked", 1, rogue_daemons.AFTER)

        self.assertEqual(actions.fuses.tick(rogue_daemons.AFTER), [])

    def test_rogue_544_main_starts_after_daemons(self):
        # Rogue 5.4.4 main.c starts runners, doctor, and stomach with start_daemon(..., AFTER).
        game = new_game(seed=309)

        self.assertTrue(game.daemons.running("runners", rogue.rogue_daemons.AFTER))
        self.assertTrue(game.daemons.running("doctor", rogue.rogue_daemons.AFTER))
        self.assertTrue(game.daemons.running("stomach", rogue.rogue_daemons.AFTER))

    def test_rogue_544_after_daemons_gate_runners_doctor_and_stomach(self):
        # Rogue 5.4.4 command.c runs runners/doctor/stomach through do_daemons(AFTER).
        game = new_game(seed=309)
        set_open_floor(game)
        monster = monster_at(game.p.x + 3, game.p.y)
        monster.running = True
        game.mons = [monster]
        turns = []
        game.m_turn = lambda m: turns.append(m)
        game.daemons.kill("runners")
        game.daemons.kill("doctor")
        game.daemons.kill("stomach")
        game.p.hp = 10
        game.p.quiet = 19
        game.p.food = 100

        game.end_turn()

        self.assertEqual(turns, [])
        self.assertEqual(game.p.hp, 10)
        self.assertEqual(game.p.food, 100)

    def test_rogue_544_runners_skips_held_running_monsters(self):
        # Rogue 5.4.4 chase.c:runners() gates move_monst() on !ISHELD && ISRUN.
        game = new_game(seed=310)
        set_open_floor(game)
        monster = monster_at(game.p.x + 3, game.p.y)
        monster.running = True
        monster.held = 2
        game.mons = [monster]
        moved = []
        game.move_monst = lambda m: moved.append(m)

        game.run_runners()

        self.assertEqual(moved, [])
        self.assertEqual(monster.held, 2)

    def test_rogue_544_chase_helper_runners_filters_held_and_not_running(self):
        # Rogue 5.4.4 chase.c:runners() lives in rogue_chase.py as a small boundary.
        import rogue_chase

        sleeping = monster_at(1, 1)
        held = monster_at(2, 1)
        running = monster_at(3, 1)
        held.running = True
        held.held = 1
        running.running = True
        moved = []

        rogue_chase.runners([sleeping, held, running], lambda monster: moved.append(monster))

        self.assertEqual(moved, [running])

    def test_rogue_544_chase_helper_runners_clears_target_after_move(self):
        # Rogue 5.4.4 chase.c:runners() clears ISTARGET if the monster moved.
        import rogue_chase

        monster = monster_at(3, 1)
        monster.running = True
        monster.target = True

        def move(mon):
            mon.x += 1

        rogue_chase.runners([monster], move)

        self.assertFalse(monster.target)

    def test_rogue_544_chase_helper_monster_turn_repeats_for_flying_at_distance(self):
        # Rogue 5.4.4 chase.c:runners() calls move_monst() again for ISFLY at distance >= 3.
        import rogue_chase

        monster = monster_at(9, 5, "K", "kestrel", flags="fly")
        monster.running = True
        calls = []

        rogue_chase.monster_turn(monster, lambda m: calls.append(m), lambda m: 3)

        self.assertEqual(calls, [monster, monster])

    def test_rogue_544_chase_helper_monster_turn_stops_fly_repeat_after_minus_one(self):
        # Rogue 5.4.4 chase.c:runners() continues when move_monst() returns -1.
        import rogue_chase

        monster = monster_at(9, 5, "K", "kestrel", flags="fly")
        monster.running = True
        calls = []

        rogue_chase.monster_turn(monster, lambda m: calls.append(m) or -1, lambda m: 3)

        self.assertEqual(calls, [monster])

    def test_rogue_544_chase_helper_move_monst_runs_steps_and_finishes_turn(self):
        # Rogue 5.4.4 chase.c:move_monst() runs chase steps, then toggles t_turn.
        import rogue_chase

        monster = monster_at(3, 1)
        calls = []
        finished = []

        rogue_chase.move_monst(
            monster,
            lambda m: calls.append(m) or 0,
            lambda m: 2,
            lambda m: finished.append(m),
        )

        self.assertEqual(calls, [monster, monster])
        self.assertEqual(finished, [monster])

    def test_rogue_544_chase_helper_runto_sets_running_and_clears_held(self):
        # Rogue 5.4.4 chase.c:runto() sets ISRUN, clears ISHELD, and sets destination.
        import rogue_chase

        monster = monster_at(3, 1)
        monster.held = 3

        rogue_chase.runto(monster, rogue.DEST_GOLD)

        self.assertTrue(monster.running)
        self.assertEqual(monster.held, 0)
        self.assertEqual(monster.dest, rogue.DEST_GOLD)

    def test_rogue_544_chase_helper_diag_ok_checks_diagonal_side_steps(self):
        # Rogue 5.4.4 chase.c:diag_ok() checks the two side squares for diagonal moves.
        import rogue_chase

        blocked = {(5, 4)}
        step_calls = []

        def step_ok(x, y):
            step_calls.append((x, y))
            return (x, y) not in blocked

        self.assertFalse(rogue_chase.diag_ok(4, 4, 5, 5, rogue.in_play_area, step_ok))
        self.assertEqual(step_calls, [(4, 5), (5, 4)])

    def test_rogue_544_chase_helper_diag_ok_allows_orthogonal_without_step_check(self):
        # Rogue 5.4.4 chase.c:diag_ok() returns TRUE for non-diagonal moves inside bounds.
        import rogue_chase

        step_calls = []

        self.assertTrue(
            rogue_chase.diag_ok(
                4,
                4,
                4,
                5,
                rogue.in_play_area,
                lambda x, y: step_calls.append((x, y)) or False,
            )
        )
        self.assertEqual(step_calls, [])

    def test_rogue_544_chase_helper_dist_uses_squared_distance(self):
        # Rogue 5.4.4 chase.c:dist() returns d^2, not the square root.
        import rogue_chase

        self.assertEqual(rogue_chase.dist(2, 3, 6, 9), 52)
        self.assertEqual(rogue_chase.dist_points((3, 2), (9, 6)), 52)

    def test_rogue_544_chase_helper_roomin_matches_room_bounds(self):
        # Rogue 5.4.4 chase.c:roomin() treats the full room rectangle as inside.
        import rogue_chase

        room = rogue.Room(10, 4, 6, 5)

        self.assertIs(rogue_chase.roomin(10, 4, [room]), room)
        self.assertIs(rogue_chase.roomin(15, 8, [room]), room)
        self.assertIsNone(rogue_chase.roomin(16, 8, [room]))

    def test_rogue_544_chase_helper_see_monst_blocks_blind_and_unseen_invisible(self):
        # Rogue 5.4.4 chase.c:see_monst() rejects blind sight and invisible monsters without CANSEE.
        import rogue_chase

        self.assertFalse(rogue_chase.see_monst(player_blind=True, monster_invisible=False, can_see_invisible=True))
        self.assertFalse(rogue_chase.see_monst(player_blind=False, monster_invisible=True, can_see_invisible=False))
        self.assertTrue(rogue_chase.see_monst(player_blind=False, monster_invisible=True, can_see_invisible=True))

    def test_rogue_544_chase_helper_lamp_sees_by_squared_distance(self):
        # Rogue 5.4.4 chase.c:see_monst()/cansee() use dist(...) < LAMPDIST.
        import rogue_chase

        self.assertTrue(rogue_chase.within_lamp_distance(2, 3))
        self.assertFalse(rogue_chase.within_lamp_distance(3, 3))

    def test_rogue_544_chase_helper_lamp_diagonal_needs_one_side_step(self):
        # Rogue 5.4.4 chase.c:see_monst()/cansee() block diagonal lamp sight only when both side cells are blocked.
        import rogue_chase

        self.assertTrue(rogue_chase.lamp_diagonal_clear((5, 5), (6, 6), lambda pos: pos == (5, 6)))
        self.assertFalse(rogue_chase.lamp_diagonal_clear((5, 5), (6, 6), lambda pos: False))
        self.assertTrue(rogue_chase.lamp_diagonal_clear((5, 5), (5, 6), lambda pos: False))

    def test_rogue_544_chase_helper_room_sight_requires_same_lit_room(self):
        # Rogue 5.4.4 chase.c:cansee() outside lamp range requires roomin(tp) == proom and !ISDARK.
        import rogue_chase

        self.assertTrue(rogue_chase.same_lit_room_visible("room", "room", False))
        self.assertFalse(rogue_chase.same_lit_room_visible("room", "other", False))
        self.assertFalse(rogue_chase.same_lit_room_visible("room", "room", True))

    def test_rogue_544_chase_helper_cansee_order_matches_source(self):
        # Rogue 5.4.4 chase.c:cansee() checks blind, lamp sight, then same lit room.
        import rogue_chase

        self.assertFalse(rogue_chase.cansee(False, True, False))
        self.assertTrue(rogue_chase.cansee(True, True, False))
        self.assertTrue(rogue_chase.cansee(True, False, True))
        self.assertFalse(rogue_chase.cansee(True, False, False))

    def test_rogue_544_chase_helper_see_monst_uses_lamp_then_room_when_supplied(self):
        # Rogue 5.4.4 chase.c:see_monst() checks blind/invisible, then lamp sight, then same lit room.
        import rogue_chase

        self.assertTrue(rogue_chase.see_monst(False, False, False, lamp_visible=True, same_lit_room_visible=False))
        self.assertTrue(rogue_chase.see_monst(False, False, False, lamp_visible=False, same_lit_room_visible=True))
        self.assertFalse(rogue_chase.see_monst(False, False, False, lamp_visible=False, same_lit_room_visible=False))
        self.assertFalse(rogue_chase.see_monst(False, True, False, lamp_visible=True, same_lit_room_visible=True))

    def test_rogue_544_chase_helper_find_dest_skips_scare_and_claimed_items(self):
        # Rogue 5.4.4 chase.c:find_dest() skips S_SCARE and destinations already claimed by another monster.
        import rogue_chase

        scare = object()
        claimed = object()
        target = object()
        rooms = {scare: "room", claimed: "room", target: "room"}
        dests = {scare: (1, 1), claimed: (2, 2), target: (3, 3)}

        self.assertIs(
            rogue_chase.find_dest(
                carry_prob=100,
                monster_room="room",
                player_room="other",
                can_see_monster=False,
                items=[scare, claimed, target],
                claimed_dests={(2, 2)},
                room_of_item=lambda item: rooms[item],
                dest_of_item=lambda item: dests[item],
                is_scare_scroll=lambda item: item is scare,
                rnd=lambda n: 0,
            ),
            target,
        )

    def test_rogue_544_chase_helper_dragon_breath_direction_matches_do_chase_gate(self):
        # Rogue 5.4.4 chase.c:do_chase() Dragon flame requires line, range, !ISCANC, and rnd(DRAGONSHOT)==0.
        import rogue_chase

        self.assertEqual(rogue_chase.dragon_breath_direction("D", (10, 10), (16, 10), 36, 6, False, lambda n: 0), (1, 0))
        self.assertEqual(rogue_chase.dragon_breath_direction("D", (10, 10), (14, 14), 32, 6, False, lambda n: 0), (1, 1))
        self.assertIsNone(rogue_chase.dragon_breath_direction("O", (10, 10), (16, 10), 36, 6, False, lambda n: 0))
        self.assertIsNone(rogue_chase.dragon_breath_direction("D", (10, 10), (13, 14), 25, 6, False, lambda n: 0))
        self.assertIsNone(rogue_chase.dragon_breath_direction("D", (10, 10), (17, 10), 49, 6, False, lambda n: 0))
        self.assertIsNone(rogue_chase.dragon_breath_direction("D", (10, 10), (16, 10), 36, 6, True, lambda n: 0))
        self.assertIsNone(rogue_chase.dragon_breath_direction("D", (10, 10), (16, 10), 36, 6, False, lambda n: 1))

    def test_rogue_544_chase_helper_nearest_exit_to_dest_uses_dist_cp(self):
        # Rogue 5.4.4 chase.c:do_chase() chooses the exit with the smallest dist_cp() to t_dest.
        import rogue_chase

        exits = [(1, 1), (5, 5), (9, 1)]
        self.assertEqual(rogue_chase.nearest_exit_to_dest(exits, (8, 2), rogue_chase.dist_points), (9, 1))
        self.assertIsNone(rogue_chase.nearest_exit_to_dest([], (8, 2), rogue_chase.dist_points))

    def test_rogue_544_chase_helper_stop_after_dest_excludes_venus_flytrap(self):
        # Rogue 5.4.4 chase.c:do_chase() sets stoprun after t_dest except when t_type == 'F'.
        import rogue_chase

        self.assertTrue(rogue_chase.should_stop_after_dest("O"))
        self.assertFalse(rogue_chase.should_stop_after_dest("F"))

    def test_rogue_544_chase_helper_dragon_breath_uses_dragonshot_constant(self):
        # Rogue 5.4.4 chase.c:do_chase() rolls rnd(DRAGONSHOT).
        import rogue_chase

        calls = []
        rogue_chase.dragon_breath_direction("D", (10, 10), (16, 10), 36, 6, False, lambda n: calls.append(n) or 0, 7)

        self.assertEqual(calls, [7])

    def test_rogue_544_chase_helper_greedy_destination_falls_back_to_hero_without_gold(self):
        # Rogue 5.4.4 chase.c:do_chase() sends ISGREED monsters after hero when room gold is gone.
        import rogue_chase

        self.assertEqual(rogue_chase.greedy_destination(True, "gold", None, "player"), "player")
        self.assertEqual(rogue_chase.greedy_destination(True, "gold", (3, 4), "player"), (3, 4))
        self.assertEqual(rogue_chase.greedy_destination(False, "gold", None, "player"), "gold")

    def test_rogue_544_chase_helper_destination_room_uses_proom_for_hero(self):
        # Rogue 5.4.4 chase.c:do_chase() uses proom when t_dest == &hero, otherwise roomin(t_dest).
        import rogue_chase

        self.assertEqual(rogue_chase.destination_room(True, "player-room", "dest-room"), "player-room")
        self.assertEqual(rogue_chase.destination_room(False, "player-room", "dest-room"), "dest-room")

    def test_rogue_544_doctor_increments_quiet_even_at_full_hp(self):
        # Rogue 5.4.4 daemons.c:doctor() increments quiet before checking whether HP can rise.
        game = new_game(seed=313)
        game.daemons.kill("runners")
        game.daemons.kill("stomach")
        game.p.hp = game.p.max_hp
        game.p.quiet = 0

        game.do_after_daemons()

        self.assertEqual(game.p.hp, game.p.max_hp)
        self.assertEqual(game.p.quiet, 1)

    def test_rogue_544_doctor_caps_full_hp_and_resets_quiet_after_heal_check(self):
        # Rogue 5.4.4 daemons.c:doctor() compares old HP before capping to max_hp, then clears quiet.
        game = new_game(seed=314)
        game.daemons.kill("runners")
        game.daemons.kill("stomach")
        game.p.level = 1
        game.p.hp = game.p.max_hp
        game.p.quiet = 18

        game.do_after_daemons()

        self.assertEqual(game.p.hp, game.p.max_hp)
        self.assertEqual(game.p.quiet, 0)

    def test_rogue_544_doctor_high_level_heal_uses_rnd_level_minus_seven_plus_one(self):
        # Rogue 5.4.4 daemons.c:doctor() heals high-level players by rnd(lv - 7) + 1.
        game = new_game(seed=319)
        game.daemons.kill("runners")
        game.daemons.kill("stomach")
        game.p.level = 10
        game.p.hp = 10
        game.p.max_hp = 20
        game.p.quiet = 2
        calls = []
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: calls.append(n) or 2
            game.do_after_daemons()
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(calls, [3])
        self.assertEqual(game.p.hp, 13)
        self.assertEqual(game.p.quiet, 0)

    def test_rogue_544_daemons_helper_doctor_matches_high_level_roll(self):
        # Rogue 5.4.4 daemons.c:doctor() lives in rogue_daemons.py as pure logic.
        player = rogue.Player()
        player.level = 10
        player.hp = 10
        player.max_hp = 20
        player.quiet = 2
        calls = []
        rng = SequenceRng([2])
        old_rnd = rng.rnd
        rng.rnd = lambda n: calls.append(n) or old_rnd(n)

        rogue.rogue_daemons.doctor_tick(player, rng, regeneration_count=0)

        self.assertEqual(calls, [3])
        self.assertEqual(player.hp, 13)
        self.assertEqual(player.quiet, 0)

    def test_rogue_544_stomach_does_not_extend_existing_no_command_faint(self):
        # Rogue 5.4.4 daemons.c:stomach() returns when no_command is already nonzero.
        game = new_game(seed=315)
        game.p.food = 0
        game.p.state = "weak"
        game.p.no_command = 5
        old_randrange = rogue.RNG.randrange
        old_randint = rogue.RNG.randint
        try:
            rogue.RNG.randrange = lambda n: 0
            rogue.RNG.randint = lambda a, b: b
            game.run_stomach()
        finally:
            rogue.RNG.randrange = old_randrange
            rogue.RNG.randint = old_randint

        self.assertEqual(game.p.food, -1)
        self.assertEqual(game.p.state, "weak")
        self.assertEqual(game.p.no_command, 5)

    def test_rogue_544_stomach_keeps_state_when_faint_roll_fails(self):
        # Rogue 5.4.4 daemons.c:stomach() sets hungry_state=3 only after faint starts.
        game = new_game(seed=321)
        game.p.food = 0
        game.p.state = "weak"
        game.p.no_command = 0
        old_randrange = rogue.RNG.randrange
        try:
            rogue.RNG.randrange = lambda n: 1
            game.run_stomach()
        finally:
            rogue.RNG.randrange = old_randrange

        self.assertEqual(game.p.food, -1)
        self.assertEqual(game.p.state, "weak")
        self.assertEqual(game.p.no_command, 0)

    def test_rogue_544_daemons_helper_stomach_keeps_state_when_faint_roll_fails(self):
        # Rogue 5.4.4 daemons.c:stomach() lives in rogue_daemons.py as pure logic.
        player = rogue.Player()
        player.food = 0
        player.state = "weak"
        player.no_command = 0
        rng = SequenceRng([1])
        rng.randrange = lambda n: 1

        msg = rogue.rogue_daemons.stomach_tick(
            player,
            rng,
            food_cost=1,
            moretime=rogue.MORETIME,
            starvetime=rogue.STARVETIME,
        )

        self.assertIsNone(msg)
        self.assertEqual(player.food, -1)
        self.assertEqual(player.state, "weak")
        self.assertEqual(player.no_command, 0)

    def test_rogue_544_daemons_helper_stomach_uses_rnd_for_faint_gate(self):
        # Rogue 5.4.4 daemons.c:stomach() uses rnd(5), not a generic randrange().
        player = rogue.Player()
        player.food = 0
        rng = SequenceRng([1])
        rng.randrange = lambda n: (_ for _ in ()).throw(AssertionError("randrange used"))

        msg = rogue.rogue_daemons.stomach_tick(
            player,
            rng,
            food_cost=1,
            moretime=rogue.MORETIME,
            starvetime=rogue.STARVETIME,
        )

        self.assertIsNone(msg)
        self.assertEqual(rng.calls, [5])

    def test_rogue_544_stomach_faint_uses_rnd_8_plus_four(self):
        # Rogue 5.4.4 daemons.c:stomach() uses no_command += rnd(8) + 4.
        game = new_game(seed=316)
        game.p.food = 0
        game.p.no_command = 0
        calls = []
        old_randrange = rogue.RNG.randrange
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.randrange = lambda n: 0

            def fake_rnd(n):
                calls.append(n)
                return 0 if n == 5 else 7

            rogue.RNG.rnd = fake_rnd
            game.run_stomach()
        finally:
            rogue.RNG.randrange = old_randrange
            rogue.RNG.rnd = old_rnd

        self.assertEqual(calls, [5, 8])
        self.assertEqual(game.p.no_command, 11)

    def test_rogue_544_stomach_decrements_food_on_starvation_death_check(self):
        # Rogue 5.4.4 daemons.c:stomach() uses food_left-- in the starvation death check.
        player = rogue.Player()
        player.food = -rogue.STARVETIME - 1
        player.state = "weak"

        msg = rogue.rogue_daemons.stomach_tick(
            player,
            SequenceRng([0]),
            food_cost=1,
            moretime=rogue.MORETIME,
            starvetime=rogue.STARVETIME,
        )

        self.assertEqual(msg, "pyxel.starve_to_death")
        self.assertEqual(player.food, -rogue.STARVETIME - 2)
        self.assertEqual(player.hp, 0)

    def test_rogue_544_stomach_crossing_zero_does_not_faint_until_next_tick(self):
        # Rogue 5.4.4 daemons.c:stomach() only runs faint logic when food_left <= 0 at entry.
        game = new_game(seed=320)
        game.p.food = 1
        game.p.state = "weak"
        game.p.no_command = 0

        game.run_stomach()

        self.assertEqual(game.p.food, 0)
        self.assertEqual(game.p.state, "weak")
        self.assertEqual(game.p.no_command, 0)

    def test_rogue_544_no_command_recovery_message_when_counter_reaches_zero(self):
        # Rogue 5.4.4 command.c:command() prints "you can move again" when --no_command reaches 0.
        game = new_game(seed=317)
        game.daemons.kill("runners")
        game.daemons.kill("doctor")
        game.daemons.kill("stomach")
        game.p.no_command = 1

        game.end_turn()

        self.assertEqual(game.p.no_command, 0)
        self.assertIn("you can move again", game.msgs)

    def test_rogue_544_before_daemons_run_before_no_command_decrement(self):
        # Rogue 5.4.4 command.c:command() calls do_daemons(BEFORE) before --no_command.
        game = new_game(seed=318)
        seen = []
        game.daemons.start("rollwand", rogue.rogue_daemons.BEFORE)
        game.roll_wanderer = lambda: seen.append(game.p.no_command)
        game.p.no_command = 1

        game.end_turn()

        self.assertEqual(seen, [1])
        self.assertEqual(game.p.no_command, 0)

    def test_rogue_544_swander_starts_rollwand_as_before_daemon(self):
        # Rogue 5.4.4 daemons.c:swander() calls start_daemon(rollwand, ..., BEFORE).
        game = new_game(seed=311)
        game.swander()

        self.assertTrue(game.daemons.running("rollwand", rogue.rogue_daemons.BEFORE))
        self.assertFalse(game.daemons.running("rollwand", rogue.rogue_daemons.AFTER))

    def test_rogue_544_rollwand_success_reschedules_swander_before_fuse(self):
        # Rogue 5.4.4 daemons.c:rollwand() calls fuse(swander, ..., WANDERTIME, BEFORE).
        game = new_game(seed=312)
        old_roll = rogue.RNG.roll
        old_spread = rogue.RNG.spread
        try:
            rogue.RNG.roll = lambda number, sides: 4
            rogue.RNG.spread = lambda n: 1
            game.wander_between = 3
            game.daemons.start("rollwand", rogue.rogue_daemons.BEFORE)
            game.spawn_wanderer = lambda: True
            game.roll_wanderer()
        finally:
            rogue.RNG.roll = old_roll
            rogue.RNG.spread = old_spread

        self.assertFalse(game.daemons.running("rollwand"))
        self.assertEqual(game.fuses.tick(rogue.rogue_daemons.AFTER), [])
        self.assertEqual(game.fuses.tick(rogue.rogue_daemons.BEFORE), ["swander"])

    def test_rogue_544_potion_haste_self_uses_nohaste_fuse_and_half_turns(self):
        # Rogue 5.4.4 potions.c:P_HASTE calls misc.c:add_haste(TRUE);
        # command.c:command() gives hasted player two actions before do_fuses(AFTER).
        game = new_game(seed=310)
        set_open_floor(game)
        potion_kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "haste self")
        potion = rogue.Item(rogue.CAT_POT, potion_kind)
        game.p.inv.append(potion)
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            game.use_pot(potion)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(game.p.haste, 5)
        self.assertEqual(game.fuses.remaining("nohaste"), 5)
        self.assertTrue(game.ident.pk[potion_kind])
        self.assertIn("you feel yourself moving much faster", game.msgs)
        self.assertNotIn(potion, game.p.inv)

        turn = game.turn
        game.end_turn()
        self.assertEqual(game.turn, turn)
        self.assertEqual(game.p.haste, 5)

        game.end_turn()
        self.assertEqual(game.turn, turn + 1)
        self.assertEqual(game.p.haste, 4)

    def test_rogue_544_second_haste_self_faints_and_extinguishes_nohaste(self):
        # Rogue 5.4.4 misc.c:add_haste() clears ISHASTE, extinguishes nohaste, and adds rnd(8) no_command.
        game = new_game(seed=311)
        set_open_floor(game)
        game.add_haste(True)
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 3
            self.assertFalse(game.add_haste(True))
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(game.p.haste, 0)
        self.assertEqual(game.fuses.remaining("nohaste"), 0)
        self.assertEqual(game.p.no_command, 3)
        self.assertIn("you faint from exhaustion", game.msgs)

    def test_rogue_544_potion_levitation_uses_spread_healtime_and_lands(self):
        # Rogue 5.4.4 potions.c:P_LEVIT uses do_pot(ISLEVIT, land, HEALTIME).
        game = new_game(seed=212)
        potion_kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "levitation")
        potion = rogue.Item(rogue.CAT_POT, potion_kind)
        game.p.inv.append(potion)

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 2
            game.use_pot(potion)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(game.p.levitating, rogue.HEALTIME - rogue.HEALTIME // 20 + 2)
        self.assertEqual(game.fuses.remaining("land"), rogue.HEALTIME - rogue.HEALTIME // 20 + 2)
        self.assertTrue(game.ident.pk[potion_kind])
        self.assertIn("you start to float in the air", game.msgs)

        game.p.levitating = 1
        game.fuses.extinguish("land")
        game.fuses.fuse("land", 1, rogue.rogue_daemons.AFTER)
        game.end_turn()

        self.assertEqual(game.p.levitating, 0)
        self.assertEqual(game.fuses.remaining("land"), 0)
        self.assertIn("you float gently to the ground", game.msgs)

    def test_rogue_544_potion_levitation_lengthens_land_fuse(self):
        # Rogue 5.4.4 potions.c:do_pot(P_LEVIT) calls lengthen(land, spread(HEALTIME)).
        game = new_game(seed=314)
        potion_kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "levitation")
        first = rogue.Item(rogue.CAT_POT, potion_kind)
        second = rogue.Item(rogue.CAT_POT, potion_kind)
        game.p.inv.extend([first, second])
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 0
            game.use_pot(first)
            game.use_pot(second)
        finally:
            rogue.RNG.rnd = old_rnd

        duration = rogue.HEALTIME - rogue.HEALTIME // 20
        self.assertEqual(game.p.levitating, duration * 2)
        self.assertEqual(game.fuses.remaining("land"), duration * 2)

    def test_rogue_544_potion_hallucination_uses_spread_seeduration_and_comes_down(self):
        # Rogue 5.4.4 potions.c:P_LSD uses do_pot(ISHALU, come_down, SEEDURATION).
        game = new_game(seed=214)
        potion_kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "hallucination")
        potion = rogue.Item(rogue.CAT_POT, potion_kind)
        game.p.inv.append(potion)

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 4
            game.use_pot(potion)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(game.p.hallucinating, rogue.SEEDURATION - rogue.SEEDURATION // 20 + 4)
        self.assertEqual(game.fuses.remaining("come_down"), rogue.SEEDURATION - rogue.SEEDURATION // 20 + 4)
        self.assertTrue(game.ident.pk[potion_kind])
        self.assertIn("Oh, wow!  Everything seems so cosmic!", game.msgs)

        game.p.hallucinating = 1
        game.fuses.extinguish("come_down")
        game.fuses.fuse("come_down", 1, rogue.rogue_daemons.AFTER)
        game.end_turn()

        self.assertEqual(game.p.hallucinating, 0)
        self.assertEqual(game.fuses.remaining("come_down"), 0)
        self.assertIn("Everything looks SO boring now.", game.msgs)

    def test_rogue_544_hallucination_turns_off_detect_monster_display(self):
        # Rogue 5.4.4 potions.c:P_LSD calls turn_see(FALSE) when SEEMONST is active.
        game = new_game(seed=216)
        potion_kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "hallucination")
        potion = rogue.Item(rogue.CAT_POT, potion_kind)
        game.p.inv.append(potion)
        game.p.see_monsters = rogue.HUHDURATION
        game.fuses.fuse("turn_see", rogue.HUHDURATION, rogue.rogue_daemons.AFTER)

        game.use_pot(potion)

        self.assertEqual(game.p.see_monsters, 0)

    def test_rogue_544_potion_hallucination_lengthens_come_down_fuse(self):
        # Rogue 5.4.4 potions.c:do_pot(P_LSD) lengthens come_down when ISHALU is already set.
        game = new_game(seed=313)
        set_open_floor(game)
        potion_kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "hallucination")
        first = rogue.Item(rogue.CAT_POT, potion_kind)
        second = rogue.Item(rogue.CAT_POT, potion_kind)
        game.p.inv.extend([first, second])
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 0
            game.use_pot(first)
            game.use_pot(second)
        finally:
            rogue.RNG.rnd = old_rnd

        duration = rogue.SEEDURATION - rogue.SEEDURATION // 20
        self.assertEqual(game.p.hallucinating, duration * 2)
        self.assertEqual(game.fuses.remaining("come_down"), duration * 2)

    def test_rogue_544_hallucination_increases_search_probinc_and_changes_trap_name(self):
        # Rogue 5.4.4 command.c:search() adds 3 to probinc while ISHALU.
        game = new_game(seed=215)
        set_open_floor(game)
        px, py = game.p.x, game.p.y
        game.hidden_tiles[(px + 1, py)] = rogue.T_DOOR
        game.tm[py][px + 1] = rogue.T_VWALL
        game.p.hallucinating = 10

        old_rnd = rogue.RNG.rnd
        calls = []
        try:
            rogue.RNG.rnd = lambda n: calls.append(n) or n - 1
            game.do_search()
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertIn(8, calls)
        self.assertEqual(game.tm[py][px + 1], rogue.T_VWALL)

        game.hidden_tiles = {}
        game.traps[(px - 1, py)] = next(i for i, t in enumerate(rogue.TRAPS) if t["name"] == "dart trap")
        game.tm[py][px - 1] = rogue.T_FLOOR
        old_rnd = rogue.RNG.rnd
        bear = next(i for i, t in enumerate(rogue.TRAPS) if t["name"] == "bear trap")
        seq = iter([0, bear])
        try:
            rogue.RNG.rnd = lambda n: next(seq)
            game.do_search()
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(game.tm[py][px - 1], rogue.T_TRAP)
        self.assertIn("You found something!", game.msgs)
        self.assertTrue(any("bear trap" in msg for msg in game.msgs))

    def test_rogue_544_confusion_does_not_change_search_probinc(self):
        # Rogue 5.4.4 command.c:search() probinc checks ISHALU and ISBLIND, not ISHUH.
        game = new_game(seed=217)
        set_open_floor(game)
        px, py = game.p.x, game.p.y
        game.hidden_tiles[(px + 1, py)] = rogue.T_DOOR
        game.tm[py][px + 1] = rogue.T_VWALL
        game.p.confused = 10

        old_rnd = rogue.RNG.rnd
        calls = []
        try:
            rogue.RNG.rnd = lambda n: calls.append(n) or n - 1
            game.do_search()
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertIn(5, calls)
        self.assertNotIn(8, calls)

    def test_rogue_544_search_helper_probinc_and_reveal_rolls_match_source(self):
        # Rogue 5.4.4 command.c:search() uses ISHALU +3, ISBLIND +2 and door/trap/passage divisors.
        import rogue_search

        self.assertEqual(rogue_search.search_probinc(False, False), 0)
        self.assertEqual(rogue_search.search_probinc(True, True), 5)
        self.assertTrue(rogue_search.reveals_secret_door(0, 0))
        self.assertFalse(rogue_search.reveals_secret_door(1, 0))
        self.assertTrue(rogue_search.reveals_trap(0, 3))
        self.assertFalse(rogue_search.reveals_trap(1, 3))
        self.assertTrue(rogue_search.reveals_secret_passage(0, 2))
        self.assertFalse(rogue_search.reveals_secret_passage(1, 2))

    def test_rogue_544_hallucination_randomizes_visible_items_stairs_and_monsters(self):
        # Rogue 5.4.4 misc.c:trip_ch() and daemons.c:visuals() use rnd_thing();
        # misc.c:look() displays visible monsters as rnd(26)+'A' while ISHALU.
        game = new_game(seed=216)
        set_open_floor(game)
        px, py = game.p.x, game.p.y
        potion = rogue.Item(rogue.CAT_POT, 0)
        potion.x, potion.y = px + 1, py
        game.gitems = [potion]
        phantom = monster_at(px + 2, py, "P", "phantom", flags="invis")
        game.mons = [phantom]
        game.tm[py][px - 1] = rogue.T_STAIR
        game.visible.update({(px + 1, py), (px + 2, py), (px - 1, py)})
        game.p.see_invisible = 10
        game.p.hallucinating = 10

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 0
            self.assertEqual(game.visible_item_sym(potion), "!")
            self.assertEqual(game.visible_tile_sym(px - 1, py, rogue.T_STAIR), "!")
            self.assertEqual(game.visible_monster_sym(phantom), "A")
        finally:
            rogue.RNG.rnd = old_rnd

    def test_rogue_544_xeroc_new_monster_uses_rnd_thing_disguise(self):
        # Rogue 5.4.4 monsters.c:new_monster() sets X t_disguise = misc.c:rnd_thing().
        game = new_game(seed=306)
        set_open_floor(game)
        game.p.depth = 7
        monster = monster_at(game.p.x + 1, game.p.y, sym="H", name="hobgoblin")
        spec = next(s for s in rogue.BESTIARY if s.sym == "X")
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 2
            game.set_monster_from_spec(monster, spec)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(monster.sym, "X")
        self.assertEqual(monster.disguise, "=")
        self.assertEqual(game.visible_monster_sym(monster), "=")

    def test_rogue_544_new_monster_applies_deep_level_stat_bonus(self):
        # Rogue 5.4.4 monsters.c:new_monster() applies level-AMULETLEVEL to stats.
        game = new_game(seed=307)
        set_open_floor(game)
        depth = rogue.AMULET_LEVEL + 3
        spec = next(s for s in rogue.BESTIARY if s.sym == "C")
        calls = []
        old_roll = rogue.RNG.roll
        try:
            rogue.RNG.roll = lambda n, sides: calls.append((n, sides)) or 17
            monster = game.new_monster_from_spec(game.p.x + 1, game.p.y, spec, depth=depth)
        finally:
            rogue.RNG.roll = old_roll

        self.assertEqual(calls, [(spec.level + 3, 8)])
        self.assertEqual(monster.level, spec.level + 3)
        self.assertEqual(monster.armor, spec.armor - 3)
        self.assertEqual(monster.exp, spec.exp + 30 + 8)
        self.assertEqual(monster.hp, 17)
        self.assertEqual(monster.max_hp, 17)

    def test_rogue_544_monster_exp_add_uses_level_and_max_hp(self):
        # Rogue 5.4.4 monsters.c:exp_add() scales by level and max HP.
        import rogue_monsters

        self.assertEqual(rogue_monsters.exp_add(1, 17), 2)
        self.assertEqual(rogue_monsters.exp_add(6, 17), 2)
        self.assertEqual(rogue_monsters.exp_add(7, 17), 8)
        self.assertEqual(rogue_monsters.exp_add(10, 17), 40)

    def test_rogue_544_monster_new_stats_helper_matches_new_monster(self):
        # Rogue 5.4.4 monsters.c:new_monster() stat rebuild helper.
        import rogue_monsters

        calls = []
        stats = rogue_monsters.new_monster_stats(
            base_level=4,
            base_armor=3,
            base_exp=17,
            depth=rogue.AMULET_LEVEL + 3,
            amulet_level=rogue.AMULET_LEVEL,
            roll=lambda n, sides: calls.append((n, sides)) or 17,
        )

        self.assertEqual(calls, [(7, 8)])
        self.assertEqual(stats, (7, 17, 0, 17 + 30 + 8))

    def test_rogue_544_save_throw_uses_monsters_c_threshold(self):
        # Rogue 5.4.4 monsters.c:save_throw() uses roll(1,20) >= 14 + which - lvl/2.
        import rogue_monsters

        self.assertFalse(rogue_monsters.save_throw(rogue.VS_MAGIC, 4, lambda n, sides: 14))
        self.assertTrue(rogue_monsters.save_throw(rogue.VS_MAGIC, 4, lambda n, sides: 15))

    def test_rogue_544_save_magic_uses_protection_ring_adjustment(self):
        # Rogue 5.4.4 monsters.c:save() subtracts R_PROTECT enchantment from VS_MAGIC.
        import rogue_rings

        game = new_game(seed=309)
        game.p.level = 4
        game.p.ring_l = rogue.Item(rogue.CAT_RING, rogue_rings.R_PROTECT, ench=2)
        calls = []
        old_roll = rogue.RNG.roll
        try:
            rogue.RNG.roll = lambda n, sides: calls.append((n, sides)) or 13
            self.assertTrue(game.save_vs_magic())
        finally:
            rogue.RNG.roll = old_roll

        self.assertEqual(calls, [(1, 20)])

    def test_rogue_544_new_monster_hastes_after_level_29(self):
        # Rogue 5.4.4 monsters.c:new_monster() sets ISHASTE when level > 29.
        game = new_game(seed=308)
        set_open_floor(game)
        spec = next(s for s in rogue.BESTIARY if s.sym == "C")
        monster = game.new_monster_from_spec(game.p.x + 1, game.p.y, spec, depth=30)

        self.assertIn(rogue.rogue_monsters.FLAG_HASTE, monster.flags)

    def test_rogue_544_levitation_blocks_stairs_pickup_and_traps(self):
        # Rogue 5.4.4 command.c:levit_check() blocks stairs and pickup;
        # move.c:be_trapped() returns before trap effects while ISLEVIT.
        game = new_game(seed=213)
        set_open_floor(game)
        game.p.levitating = 10
        item = rogue.Item(rogue.CAT_FOOD, 0)
        item.x, item.y = game.p.x, game.p.y
        game.gitems = [item]

        game.do_pickup()

        self.assertIn(item, game.gitems)
        self.assertNotIn(item, game.p.inv)
        self.assertIn("You can't.  You're floating off the ground!", game.msgs)

        game.gitems = []
        game.tm[game.p.y][game.p.x] = rogue.T_STAIR
        old_depth = game.p.depth

        game.do_action()

        self.assertEqual(game.p.depth, old_depth)
        self.assertIn("You can't.  You're floating off the ground!", game.msgs)

        game.tm[game.p.y][game.p.x] = rogue.T_FLOOR
        x, y = game.p.x + 1, game.p.y
        game.traps[(x, y)] = 3
        game.try_move(1, 0)

        self.assertEqual((game.p.x, game.p.y), (x, y))
        self.assertEqual(game.tm[y][x], rogue.T_FLOOR)
        self.assertEqual(game.p.stuck, 0)
        self.assertNotIn("you are caught in a bear trap", game.msgs)

    def test_rogue_544_ring_aggravate_and_stealth_affect_monster_running(self):
        # Rogue 5.4.4 rings.c:ring_on() aggravates; monsters.c:wake_monster checks R_STEALTH.
        import rogue_rings

        game = new_game(seed=210)
        set_open_floor(game)
        first = monster_at(game.p.x + 1, game.p.y)
        second = monster_at(game.p.x + 2, game.p.y)
        game.mons = [first, second]

        game.put_on_ring(rogue.Item(rogue.CAT_RING, rogue_rings.R_AGGR))
        self.assertTrue(first.running)
        self.assertTrue(second.running)
        self.assertFalse(game.ident.rk[rogue_rings.R_AGGR])

        game = new_game(seed=211)
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

        game = new_game(seed=212)
        set_open_floor(game)
        game.p.ring_l = rogue.Item(rogue.CAT_RING, rogue_rings.R_SUSTSTR)
        game.p.st = 10
        snake = monster_at(game.p.x + 1, game.p.y, "R", "rattlesnake", 10, 20, 100, "0x0", 5, "poison")
        game.swing_hits = lambda at_lvl, op_arm, wplus: True
        game.m_attack(snake)
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

    def test_rogue_544_rattlesnake_save_runs_before_sustain_strength_check(self):
        # Rogue 5.4.4 fight.c:attack() calls save(VS_POISON), then checks R_SUSTSTR.
        import rogue_rings

        game = new_game(seed=213)
        set_open_floor(game)
        game.p.ring_l = rogue.Item(rogue.CAT_RING, rogue_rings.R_SUSTSTR)
        game.p.st = 10
        snake = monster_at(game.p.x + 1, game.p.y, "R", "rattlesnake", 10, 20, 100, "0x0", 5, "poison")
        game.swing_hits = lambda at_lvl, op_arm, wplus: True
        calls = []
        game.save_vs_poison = lambda: calls.append(True) or False

        game.m_attack(snake)

        self.assertEqual(calls, [True])
        self.assertEqual(game.p.st, 10)
        self.assertIn("a bite momentarily weakens you", game.msgs)

    def test_rogue_544_poison_potion_ends_hallucination_after_strength_loss(self):
        # Rogue 5.4.4 potions.c:P_POISON calls daemons.c:come_down() after chg_str().
        game = new_game(seed=213)
        poison = next(i for i, spec in enumerate(rogue.POTIONS) if spec["name"] == "poison")
        potion = rogue.Item(rogue.CAT_POT, poison)
        game.p.inv.append(potion)
        game.p.hallucinating = 10
        game.fuses.fuse("come_down", 10, rogue.rogue_daemons.AFTER)

        game.use_pot(potion)

        self.assertEqual(game.p.hallucinating, 0)
        self.assertIn("Everything looks SO boring now.", game.msgs)

    def test_rogue_544_poison_potion_uses_original_sick_message(self):
        # Rogue 5.4.4 potions.c:P_POISON says "you feel very sick now" after chg_str().
        game = new_game(seed=214)
        set_open_floor(game)
        poison = next(i for i, spec in enumerate(rogue.POTIONS) if spec["name"] == "poison")
        potion = rogue.Item(rogue.CAT_POT, poison)
        game.p.inv.append(potion)
        game.p.st = 10

        old_randint = rogue.RNG.randint
        try:
            rogue.RNG.randint = lambda a, b: 2
            game.use_pot(potion)
        finally:
            rogue.RNG.randint = old_randint

        self.assertEqual(game.p.st, 8)
        self.assertTrue(game.ident.pk[poison])
        self.assertIn("you feel very sick now", game.msgs)
        self.assertNotIn("You feel sick. (Str -2)", game.msgs)

    def test_rogue_544_poison_potion_strength_floor_is_three(self):
        # Rogue 5.4.4 misc.c:add_str() floors Strength at 3.
        game = new_game(seed=216)
        poison = next(i for i, spec in enumerate(rogue.POTIONS) if spec["name"] == "poison")
        potion = rogue.Item(rogue.CAT_POT, poison)
        game.p.inv.append(potion)
        game.p.st = 4
        old_randint = rogue.RNG.randint
        try:
            rogue.RNG.randint = lambda a, b: 3
            game.use_pot(potion)
        finally:
            rogue.RNG.randint = old_randint

        self.assertEqual(game.p.st, 3)

    def test_rogue_544_potions_helper_strength_changes_match_misc_add_str(self):
        # Rogue 5.4.4 misc.c:add_str()/chg_str() floor at 3, cap at 31, and track base max strength.
        import rogue_potions

        self.assertEqual(rogue_potions.add_str(4, -3), 3)
        self.assertEqual(rogue_potions.add_str(30, 5), 31)
        self.assertEqual(rogue_potions.gain_strength(31, 30), (31, 31))
        self.assertEqual(rogue_potions.poison_strength(10, 2), 8)
        self.assertEqual(rogue_potions.restore_strength(20, 18, 2), 20)
        self.assertEqual(rogue_potions.restore_strength(11, 16, 2), 16)

    def test_rogue_544_potions_helper_healing_matches_quaff(self):
        # Rogue 5.4.4 potions.c:P_HEALING/P_XHEAL max_hp overflow rules.
        import rogue_potions

        self.assertEqual(rogue_potions.healing_hp(10, 16, 6), (16, 16))
        self.assertEqual(rogue_potions.healing_hp(10, 16, 7), (17, 17))
        self.assertEqual(rogue_potions.extra_healing_hp(16, 16, 2, 3), (17, 17))
        self.assertEqual(rogue_potions.extra_healing_hp(16, 16, 2, 4), (18, 18))

    def test_rogue_544_level_helper_check_level_matches_misc(self):
        # Rogue 5.4.4 misc.c:check_level() rolls one d10 per gained level.
        import rogue_levels

        class Rng:
            def __init__(self):
                self.calls = []

            def roll(self, number, sides):
                self.calls.append((number, sides))
                return 17

        rng = Rng()
        result = rogue_levels.check_level(1, 41, 12, 12, rogue.Player.EXP_T, rng)

        self.assertEqual(result, (4, 29, 29, True))
        self.assertEqual(rng.calls, [(3, 10)])

    def test_rogue_544_level_helper_raise_level_exp_matches_potions(self):
        # Rogue 5.4.4 potions.c:raise_level() sets exp to e_levels[level-1]+1.
        import rogue_levels

        self.assertEqual(rogue_levels.raise_level_exp(10, rogue.Player.EXP_T), 5201)

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

    def test_rogue_544_rust_armor_uses_current_armor_class_limit(self):
        # Rogue 5.4.4 move.c:rust_armor() rusts armor while o_arm < 9.
        game = new_game(seed=212)
        armor = rogue.Item(rogue.CAT_ARM, 7, ench=-3)
        game.p.arm = armor
        game.p.recalc_ac()

        game.rust_armor()

        self.assertEqual(armor.ench, -4)
        self.assertIn("your armor weakens", game.msgs)

    def test_full_map_layout_baseline(self):
        self.assertEqual((rogue.SCR_W, rogue.SCR_H), (576, 360))
        self.assertEqual((rogue.ZV_COLS, rogue.ZV_ROWS), (rogue.MAP_W, rogue.PLAY_H))
        self.assertEqual((rogue.ZV_PX_W, rogue.ZV_PX_H), (480, 264))
        self.assertEqual(rogue.HUD_W, 78)
        self.assertEqual(rogue.MSG_LINES, 7)
        self.assertEqual(rogue.AUX_ACTIONS, ["Inventory", "Help", "Search", "Trap", "Pickup", "Language", "Palette", "Quit"])

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

    def test_text_catalog_loads_external_message_json(self):
        self.assertEqual(
            rogue.TextCatalog.msg(rogue.LANG_EN, "command.no_monster_there"),
            "no monster there",
        )
        self.assertEqual(
            rogue.TextCatalog.msg(rogue.LANG_JA, "command.no_monster_there"),
            "その方向には怪物がいない。",
        )

    def test_text_catalog_falls_back_to_english_for_missing_ja_key(self):
        catalogs = rogue.TextCatalog._load_catalogs()
        ja_catalog = catalogs[rogue.LANG_JA]
        original = ja_catalog.pop("command.no_monster_there")
        try:
            self.assertEqual(
                rogue.TextCatalog.msg(rogue.LANG_JA, "command.no_monster_there"),
                "no monster there",
            )
        finally:
            ja_catalog["command.no_monster_there"] = original

    def test_text_catalog_falls_back_when_json_assets_are_missing(self):
        import builtins

        def pyodide_open(*args, **kwargs):
            raise Exception("[Errno 44] No such file or directory")

        original_open = builtins.open
        original_file = rogue.__file__
        original_catalogs = rogue.TextCatalog._catalogs
        try:
            builtins.open = pyodide_open
            rogue.__file__ = os.path.join("/tmp", "missing_pyxel_web", "rogue.py")
            rogue.TextCatalog._catalogs = None
            self.assertEqual(
                rogue.TextCatalog.msg(rogue.LANG_EN, "pyxel.welcome_to_dungeons"),
                "Welcome to the Dungeons of Doom!",
            )
        finally:
            builtins.open = original_open
            rogue.__file__ = original_file
            rogue.TextCatalog._catalogs = original_catalogs

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

    def test_rogue_544_wear_rejects_new_armor_until_current_armor_is_removed(self):
        # Rogue 5.4.4 armor.c:wear() rejects cur_armor != NULL.
        game = new_game(seed=8)
        current = game.p.arm
        replacement = rogue.Item(rogue.CAT_ARM, 1)
        game.p.inv.append(replacement)

        game.wear(replacement)

        self.assertIs(game.p.arm, current)
        self.assertIn("take it off first", game.msgs[-1])

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

    def test_rogue_544_monster_carry_table_and_give_pack_probability(self):
        # Rogue 5.4.4 extern.c:monsters[] m_carry and monsters.c:give_pack().
        specs = {m.sym: m for m in rogue.BESTIARY}
        self.assertEqual(
            [specs[sym].carry for sym in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"],
            [0, 0, 15, 100, 0, 0, 20, 0, 0, 70, 0, 0, 40, 100, 15, 0, 0, 0, 0, 50, 0, 20, 0, 30, 30, 0],
        )

        game = new_game(seed=301)
        set_open_floor(game)
        game.max_depth = game.p.depth
        nymph = monster_at(game.p.x + 1, game.p.y, "N", "nymph", flags="steal_item")
        carried = rogue.Item(rogue.CAT_FOOD, 0)
        old_rnd = rogue.RNG.rnd
        old_make_item = rogue.make_item
        try:
            rogue.RNG.rnd = lambda n: 99
            rogue.make_item = lambda depth: carried
            game.give_pack(nymph)
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.make_item = old_make_item

        self.assertEqual(nymph.pack, [carried])

        nymph.pack = []
        game.max_depth = game.p.depth + 1
        old_rnd = rogue.RNG.rnd
        old_make_item = rogue.make_item
        try:
            rogue.RNG.rnd = lambda n: 0
            rogue.make_item = lambda depth: rogue.Item(rogue.CAT_FOOD, 0)
            game.give_pack(nymph)
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.make_item = old_make_item

        self.assertEqual(nymph.pack, [])

    def test_rogue_544_nymph_steal_uses_reservoir_selection(self):
        # Rogue 5.4.4 fight.c:attack() picks among magic pack items with rnd(++nobj)==0.
        game = new_game(seed=302)
        first = rogue.Item(rogue.CAT_POT, 0)
        second = rogue.Item(rogue.CAT_SCR, 0)
        equipped = rogue.Item(rogue.CAT_WPN, 0)
        game.p.inv = [equipped, first, second]
        game.p.wpn = equipped
        calls = []
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: calls.append(n) or 0
            self.assertIs(game.monster_has_magic_item_to_steal(), second)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(calls, [1, 2])

    def test_rogue_544_fight_helper_nymph_steal_uses_reservoir_selection(self):
        # Rogue 5.4.4 fight.c:attack() excludes equipped items and uses rnd(++nobj)==0.
        import rogue_fight

        equipped = object()
        first = object()
        second = object()
        calls = []

        self.assertIs(
            rogue_fight.magic_item_to_steal(
                [equipped, first, second],
                {equipped},
                lambda item: item is not equipped,
                lambda n: calls.append(n) or 0,
            ),
            second,
        )
        self.assertEqual(calls, [1, 2])

    def test_rogue_544_leprechaun_steals_gold_with_goldcalc(self):
        # Rogue 5.4.4 fight.c:attack() subtracts GOLDCALC once, plus four
        # more times on failed VS_MAGIC; rogue.h:GOLDCALC uses rnd(50+10*level)+2.
        game = new_game(seed=303)
        set_open_floor(game)
        game.p.depth = 3
        game.p.gold = 100
        leprechaun = monster_at(game.p.x + 1, game.p.y, "L", "leprechaun", damage="0x0", flags="steal_gold")
        game.mons = [leprechaun]
        game.roll_monster_attack = lambda m: (True, 0)
        game.save_vs_magic = lambda: False
        game.monster_hit_message = lambda name: "hit"
        calls = []
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: calls.append(n) or 0
            game.m_attack(leprechaun)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(calls, [80, 80, 80, 80, 80])
        self.assertEqual(game.p.gold, 90)
        self.assertNotIn(leprechaun, game.mons)

    def test_rogue_544_fight_helper_goldcalc_uses_level_scaled_roll(self):
        # Rogue 5.4.4 rogue.h:GOLDCALC is rnd(50 + 10 * level) + 2.
        import rogue_fight

        calls = []

        self.assertEqual(rogue_fight.goldcalc(3, lambda n: calls.append(n) or 7), 9)
        self.assertEqual(calls, [80])

    def test_rogue_544_fight_helper_leprechaun_gold_loss_rolls_once_plus_four_on_failed_save(self):
        # Rogue 5.4.4 fight.c:attack() subtracts one GOLDCALC, plus four more when save fails.
        import rogue_fight

        rolls = []

        self.assertEqual(
            rogue_fight.leprechaun_gold_loss(3, magic_saved=False, goldcalc=lambda level: rolls.append(level) or 2),
            10,
        )
        self.assertEqual(rolls, [3, 3, 3, 3, 3])

    def test_rogue_544_fight_helper_leprechaun_kill_gold_rolls_extra_on_saved_magic(self):
        # Rogue 5.4.4 fight.c:killed() gives GOLDCALC, plus four more when save(VS_MAGIC) succeeds.
        import rogue_fight

        rolls = []

        self.assertEqual(
            rogue_fight.leprechaun_kill_gold(3, magic_saved=True, goldcalc=lambda level: rolls.append(level) or 2),
            10,
        )
        self.assertEqual(rolls, [3, 3, 3, 3, 3])

    def test_rogue_544_killed_leprechaun_drops_gold_at_max_depth(self):
        # Rogue 5.4.4 fight.c:killed() attaches Leprechaun gold to t_pack before remove_mon(..., TRUE).
        game = new_game(seed=3011)
        set_open_floor(game)
        game.max_depth = game.p.depth
        leprechaun = monster_at(game.p.x + 1, game.p.y, "L", "leprechaun")
        game.mons = [leprechaun]
        old_rnd = rogue.RNG.rnd
        old_save_vs_magic = game.save_vs_magic
        try:
            rogue.RNG.rnd = lambda n: 0
            game.save_vs_magic = lambda: True
            game.award_monster_kill(leprechaun)
        finally:
            rogue.RNG.rnd = old_rnd
            game.save_vs_magic = old_save_vs_magic

        gold = [item for item in game.gitems if item.cat == rogue.CAT_GOLD]
        self.assertEqual([item.qty for item in gold], [10])

    def test_rogue_544_leprechaun_disappears_even_when_purse_is_empty(self):
        # Rogue 5.4.4 fight.c:attack() always remove_mon()s a Leprechaun hit;
        # the purse message is only printed when purse != lastpurse.
        game = new_game(seed=303)
        set_open_floor(game)
        game.p.depth = 3
        game.p.gold = 0
        leprechaun = monster_at(game.p.x + 1, game.p.y, "L", "leprechaun", damage="0x0", flags="steal_gold")
        game.mons = [leprechaun]
        game.roll_monster_attack = lambda m: (True, 0)
        game.save_vs_magic = lambda: True
        game.monster_hit_message = lambda name: "hit"

        game.m_attack(leprechaun)

        self.assertEqual(game.p.gold, 0)
        self.assertNotIn(leprechaun, game.mons)
        self.assertNotIn("your purse feels lighter", game.msgs)

    def test_rogue_544_wraith_drain_sets_exp_to_new_level_threshold_plus_one(self):
        # Rogue 5.4.4 fight.c:attack() sets s_exp = e_levels[s_lvl-1] + 1
        # after Wraith level drain decrements s_lvl.
        game = new_game(seed=304)
        set_open_floor(game)
        game.p.level = 3
        game.p.exp = 50
        game.p.hp = 20
        game.p.max_hp = 20
        wraith = monster_at(game.p.x + 1, game.p.y, "W", "wraith", damage="0x0", flags="drain_level")
        game.roll_monster_attack = lambda m: (True, 0)
        game.monster_hit_message = lambda name: "hit"
        old_rnd = rogue.RNG.rnd
        old_roll = rogue.RNG.roll
        try:
            rogue.RNG.rnd = lambda n: 0
            rogue.RNG.roll = lambda number, sides: 1
            game.m_attack(wraith)
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.RNG.roll = old_roll

        self.assertEqual(game.p.level, 2)
        self.assertEqual(game.p.exp, rogue.Player.EXP_T[1] + 1)
        self.assertEqual((game.p.hp, game.p.max_hp), (19, 19))

    def test_rogue_544_fight_helper_wraith_drain_decrements_level_and_hp(self):
        # Rogue 5.4.4 fight.c:attack() decrements level, sets exp, and subtracts fewer from hp/max_hp.
        import rogue_fight

        self.assertEqual(
            rogue_fight.wraith_drain(3, 50, 10, 20, rogue.Player.EXP_T, lambda: 2),
            (2, rogue.Player.EXP_T[1] + 1, 8, 18, False),
        )
        self.assertEqual(
            rogue_fight.wraith_drain(1, 5, 10, 20, rogue.Player.EXP_T, lambda: 2),
            (1, 0, 8, 18, False),
        )

    def test_rogue_544_wraith_drain_at_level_one_keeps_level_and_clears_exp(self):
        # Rogue 5.4.4 fight.c:attack() decrements s_lvl, then restores it
        # to 1 and clears s_exp when --s_lvl reaches 0.
        game = new_game(seed=304)
        set_open_floor(game)
        game.p.level = 1
        game.p.exp = 5
        game.p.hp = 20
        game.p.max_hp = 20
        wraith = monster_at(game.p.x + 1, game.p.y, "W", "wraith", damage="0x0", flags="drain_level")
        game.roll_monster_attack = lambda m: (True, 0)
        game.monster_hit_message = lambda name: "hit"
        old_rnd = rogue.RNG.rnd
        old_roll = rogue.RNG.roll
        try:
            rogue.RNG.rnd = lambda n: 0
            rogue.RNG.roll = lambda number, sides: 1
            game.m_attack(wraith)
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.RNG.roll = old_roll

        self.assertEqual(game.p.level, 1)
        self.assertEqual(game.p.exp, 0)
        self.assertEqual((game.p.hp, game.p.max_hp), (19, 19))

    def test_rogue_544_wraith_drain_kills_when_exp_is_zero(self):
        # Rogue 5.4.4 fight.c:attack() calls death('W') if pstats.s_exp == 0.
        game = new_game(seed=305)
        set_open_floor(game)
        game.p.level = 1
        game.p.exp = 0
        game.p.hp = 20
        wraith = monster_at(game.p.x + 1, game.p.y, "W", "wraith", damage="0x0", flags="drain_level")
        game.roll_monster_attack = lambda m: (True, 0)
        game.monster_hit_message = lambda name: "hit"
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 0
            game.m_attack(wraith)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(game.p.hp, 0)
        self.assertEqual(game.death_cause, "killed by a wraith")

    def test_rogue_544_wraith_drain_kills_when_max_hp_reaches_zero(self):
        # Rogue 5.4.4 fight.c:attack() calls death('W') if max_hp <= 0.
        game = new_game(seed=306)
        set_open_floor(game)
        game.p.level = 2
        game.p.exp = 20
        game.p.hp = 3
        game.p.max_hp = 3
        wraith = monster_at(game.p.x + 1, game.p.y, "W", "wraith", damage="0x0", flags="drain_level")
        game.roll_monster_attack = lambda m: (True, 0)
        game.monster_hit_message = lambda name: "hit"
        old_rnd = rogue.RNG.rnd
        old_roll = rogue.RNG.roll
        try:
            rogue.RNG.rnd = lambda n: 0
            rogue.RNG.roll = lambda number, sides: 4
            game.m_attack(wraith)
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.RNG.roll = old_roll

        self.assertEqual(game.p.hp, 0)
        self.assertEqual(game.death_cause, "killed by a wraith")

    def test_rogue_544_vampire_drain_kills_when_max_hp_reaches_zero(self):
        # Rogue 5.4.4 fight.c:attack() calls death('V') if max_hp <= 0.
        game = new_game(seed=306)
        set_open_floor(game)
        game.p.hp = 2
        game.p.max_hp = 2
        vampire = monster_at(game.p.x + 1, game.p.y, "V", "vampire", damage="0x0", flags="drain")
        game.roll_monster_attack = lambda m: (True, 0)
        game.monster_hit_message = lambda name: "hit"
        old_rnd = rogue.RNG.rnd
        old_roll = rogue.RNG.roll
        try:
            rogue.RNG.rnd = lambda n: 0
            rogue.RNG.roll = lambda number, sides: 3
            game.m_attack(vampire)
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.RNG.roll = old_roll

        self.assertEqual(game.p.hp, 0)
        self.assertEqual(game.death_cause, "killed by a vampire")

    def test_rogue_544_fight_helper_vampire_drain_subtracts_hp_and_max_hp(self):
        # Rogue 5.4.4 fight.c:attack() Vampire drain subtracts roll(1,3) from hp and max_hp.
        import rogue_fight

        self.assertEqual(rogue_fight.max_hp_drain(10, 20, lambda: 3), (7, 17, False))
        self.assertEqual(rogue_fight.max_hp_drain(1, 2, lambda: 3), (1, -1, True))

    def test_rogue_544_fight_helper_drain_chance_uses_monster_type_threshold(self):
        # Rogue 5.4.4 fight.c:attack() uses 15% for Wraith, 30% for Vampire.
        import rogue_fight

        self.assertTrue(rogue_fight.drain_hits("W", lambda n: 14))
        self.assertFalse(rogue_fight.drain_hits("W", lambda n: 15))
        self.assertTrue(rogue_fight.drain_hits("V", lambda n: 29))
        self.assertFalse(rogue_fight.drain_hits("V", lambda n: 30))

    def test_rogue_544_melee_attack_reveals_disguised_xeroc_without_damage(self):
        # Rogue 5.4.4 fight.c:attack() reveals disguised X and returns FALSE for non-thrown attacks.
        game = new_game(seed=307)
        set_open_floor(game)
        xeroc = monster_at(game.p.x + 1, game.p.y, sym="X", name="xeroc", hp=40, level=7, armor=7, damage="4x4", exp=100)
        xeroc.disguise = "?"
        game.mons = [xeroc]
        calls = []
        old_roll_player_attack = game.roll_player_attack
        try:
            game.roll_player_attack = lambda *args, **kwargs: calls.append(args) or (True, 5)
            game.p_attack(xeroc)
        finally:
            game.roll_player_attack = old_roll_player_attack

        self.assertEqual(calls, [])
        self.assertEqual(xeroc.hp, 40)
        self.assertEqual(xeroc.disguise, "X")
        self.assertIn("wait!  That's a xeroc!", game.msgs)

    def test_rogue544_treasure_room_counts_match_new_level_treas_room(self):
        # Rogue 5.4.4 new_level.c:treas_room() uses MINTREAS/MAXTREAS
        # and forces monster count to at least treasure count + 2.
        import rogue_dungeon

        rng = SequenceRng([0, 0])
        self.assertEqual(rogue_dungeon.treasure_room_counts(16, rng), (2, 4))
        self.assertEqual(rng.calls, [8, 8])

        rng = SequenceRng([7, 7])
        self.assertEqual(rogue_dungeon.treasure_room_counts(80, rng), (9, 11))

        rng = SequenceRng([0, 0])
        self.assertEqual(rogue_dungeon.treasure_room_counts(4, rng), (2, 4))

    def test_rogue544_spawn_treasure_room_places_items_and_next_level_mean_pack_monsters(self):
        # Rogue 5.4.4 new_level.c:treas_room() places treasures, then
        # level++ monsters with ISMEAN and monsters.c:give_pack().
        game = new_game(seed=303)
        set_open_floor(game)
        game.p.depth = 7
        game.max_depth = 7
        room = game.rooms[0]
        positions = iter((x, game.p.y + 2) for x in range(2, 8))
        pack_depths = []
        old_make_item = rogue.make_item
        old_random_room_tile = game.random_room_tile
        old_random_monster_spec = getattr(game, "random_monster_spec", None)
        old_give_pack = game.give_pack
        old_rnd = rogue.RNG.rnd
        rnd_calls = []
        try:
            def rnd(n):
                rnd_calls.append(n)
                return 8 if n == 10 else 0

            rogue.RNG.rnd = rnd
            rogue.make_item = lambda depth: rogue.Item(rogue.CAT_FOOD, 0)
            game.random_room_tile = lambda room_arg, tiles: next(positions)
            game.random_monster_spec = lambda depth: (_ for _ in ()).throw(AssertionError("random_monster_spec used"))
            game.give_pack = lambda monster, depth=None: pack_depths.append(depth) or monster.pack.append(rogue.Item(rogue.CAT_FOOD, 0))

            game._spawn_treasure_room(room)
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.make_item = old_make_item
            game.random_room_tile = old_random_room_tile
            if old_random_monster_spec is not None:
                game.random_monster_spec = old_random_monster_spec
            game.give_pack = old_give_pack

        self.assertEqual(len(game.gitems), 2)
        self.assertEqual(len(game.mons), 4)
        self.assertTrue(all(item.cat == rogue.CAT_FOOD for item in game.gitems))
        self.assertTrue(all(monster.sym == "C" and monster.mean for monster in game.mons))
        self.assertEqual(pack_depths, [8, 8, 8, 8])
        self.assertTrue(all(monster.pack for monster in game.mons))

    def test_rogue544_put_things_uses_one_in_20_treasure_room_gate(self):
        # Rogue 5.4.4 new_level.c:put_things() calls treas_room() when rnd(TREAS_ROOM)==0.
        game = new_game(seed=304)
        set_open_floor(game)
        calls = []
        old_spawn_treasure_room = getattr(game, "_spawn_treasure_room", None)
        old_rnd = rogue.RNG.rnd
        old_randint = rogue.RNG.randint
        try:
            rogue.RNG.rnd = lambda n: 0
            rogue.RNG.randint = lambda a, b: 0
            game._spawn_treasure_room = lambda room=None: calls.append(room)
            game._spawn_items()
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.RNG.randint = old_randint
            if old_spawn_treasure_room is not None:
                game._spawn_treasure_room = old_spawn_treasure_room

        self.assertEqual(calls, [None])

    def test_rogue544_put_things_uses_nine_36_percent_item_attempts(self):
        # Rogue 5.4.4 rogue.h:MAXOBJ=9 and new_level.c:put_things() places when rnd(100)<36.
        import rogue_dungeon

        rng = SequenceRng([0, 35, 36, 99, 12, 60, 34, 35, 90])
        self.assertEqual(rogue_dungeon.put_things_item_count(rng), 5)
        self.assertEqual(rng.calls, [100] * 9)

    def test_rogue544_put_things_skips_when_returning_up_with_amulet(self):
        # Rogue 5.4.4 new_level.c:put_things() returns when amulet && level < max_level.
        import rogue_dungeon

        self.assertFalse(rogue_dungeon.should_put_things(True, 3, 4))
        self.assertTrue(rogue_dungeon.should_put_things(True, 4, 4))
        self.assertTrue(rogue_dungeon.should_put_things(False, 3, 4))

    def test_rogue544_room_gold_gate_matches_do_rooms(self):
        # Rogue 5.4.4 rooms.c:do_rooms() places gold on rnd(2)==0 unless ascending with Amulet.
        import rogue_dungeon

        self.assertTrue(rogue_dungeon.should_place_room_gold(SequenceRng([0]), False, 3, 4))
        self.assertFalse(rogue_dungeon.should_place_room_gold(SequenceRng([1]), False, 3, 4))
        self.assertFalse(rogue_dungeon.should_place_room_gold(SequenceRng([0]), True, 3, 4))
        self.assertTrue(rogue_dungeon.should_place_room_gold(SequenceRng([0]), True, 4, 4))

    def test_rogue544_room_monster_gate_matches_do_rooms(self):
        # Rogue 5.4.4 rooms.c:do_rooms() uses 80% with gold in room, otherwise 25%.
        import rogue_dungeon

        self.assertTrue(rogue_dungeon.should_place_room_monster(SequenceRng([79]), True))
        self.assertFalse(rogue_dungeon.should_place_room_monster(SequenceRng([80]), True))
        self.assertTrue(rogue_dungeon.should_place_room_monster(SequenceRng([24]), False))
        self.assertFalse(rogue_dungeon.should_place_room_monster(SequenceRng([25]), False))

    def test_rogue544_rooms_helper_gone_room_selection_allows_duplicates(self):
        # Rogue 5.4.4 rooms.c:do_rooms() loops left_out times and may pick the same room twice.
        import rogue_rooms

        rng = SequenceRng([3, 2, 2, 5])
        self.assertEqual(rogue_rooms.gone_room_indices(9, rng), {2, 5})
        self.assertEqual(rng.calls, [4, 9, 9, 9])

    def test_rogue544_rooms_helper_room_kind_flags_match_dark_maze_gate(self):
        # Rogue 5.4.4 rooms.c:do_rooms() sets ISDARK on rnd(10)<level-1, then ISMAZE on rnd(15)==0.
        import rogue_rooms

        self.assertIsNone(rogue_rooms.room_kind_flag(5, SequenceRng([4])))
        self.assertEqual(rogue_rooms.room_kind_flag(5, SequenceRng([3, 1])), "dark")
        self.assertEqual(rogue_rooms.room_kind_flag(5, SequenceRng([3, 0])), "maze")

    def test_rogue544_spawn_mons_uses_room_gold_monster_gate(self):
        # Rogue 5.4.4 rooms.c:do_rooms() rolls one monster gate per real room.
        game = new_game(seed=3303)
        set_open_floor(game)
        room = game.rooms[0]
        spec = next(s for s in rogue.BESTIARY if s.sym == "E")
        old_rnd = rogue.RNG.rnd
        old_usable_rooms = game.usable_rooms
        old_random_room_tile = game.random_room_tile
        old_random_monster_spec = game.random_monster_spec
        old_give_pack = game.give_pack
        try:
            game.mons = []
            game.gitems = []
            game.usable_rooms = lambda: [room]
            game.random_room_tile = lambda room_arg, tiles: (game.p.x + 1, game.p.y)
            game.random_monster_spec = lambda depth: spec
            game.give_pack = lambda monster: None
            rogue.RNG.rnd = lambda n: 25
            game._spawn_mons()
            self.assertEqual(game.mons, [])

            rogue.RNG.rnd = lambda n: 24
            game._spawn_mons()
            self.assertEqual([m.sym for m in game.mons], ["E"])
        finally:
            rogue.RNG.rnd = old_rnd
            game.usable_rooms = old_usable_rooms
            game.random_room_tile = old_random_room_tile
            game.random_monster_spec = old_random_monster_spec
            game.give_pack = old_give_pack

    def test_rogue_544_killed_monster_drops_pack_items_at_monster_position(self):
        # Rogue 5.4.4 fight.c:killed() calls remove_mon(..., TRUE), which falls t_pack items.
        game = new_game(seed=302)
        set_open_floor(game)
        monster = monster_at(game.p.x + 1, game.p.y)
        item = rogue.Item(rogue.CAT_FOOD, 0)
        monster.pack = [item]
        game.mons = [monster]

        game.award_monster_kill(monster)

        self.assertNotIn(monster, game.mons)
        self.assertEqual(monster.pack, [])
        self.assertIn(item, game.gitems)
        self.assertEqual((item.x, item.y), (monster.x, monster.y))

    def test_rogue_544_polymorph_rebuilds_monster_and_preserves_pack(self):
        # Rogue 5.4.4 sticks.c:do_zap() WS_POLYMORPH saves t_pack and restores it after new_monster().
        game = new_game(seed=303)
        set_open_floor(game)
        monster = monster_at(game.p.x + 1, game.p.y)
        item = rogue.Item(rogue.CAT_FOOD, 0)
        monster.pack = [item]
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 3
            game.polymorph_monster(monster)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual((monster.sym, monster.name), ("D", "dragon"))
        self.assertEqual(monster.pack, [item])

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

    def test_rogue_544_fight_helper_swing_uses_d20_threshold(self):
        # Rogue 5.4.4 fight.c:swing() hits when rnd(20)+wplus >= (20-at_lvl)-op_arm.
        import rogue_fight

        self.assertFalse(rogue_fight.swing(1, 5, 0, lambda n: 13))
        self.assertTrue(rogue_fight.swing(1, 5, 0, lambda n: 14))
        self.assertTrue(rogue_fight.swing(1, 5, 1, lambda n: 13))

    def test_rogue_544_game_swing_hits_uses_rng_rnd(self):
        # Rogue 5.4.4 fight.c:swing() calls rnd(20).
        game = new_game(seed=405)
        old_rnd = rogue.RNG.rnd
        old_randrange = rogue.RNG.randrange
        try:
            rogue.RNG.rnd = lambda n: 14
            rogue.RNG.randrange = lambda n: (_ for _ in ()).throw(AssertionError("randrange used"))
            self.assertTrue(game.swing_hits(1, 5, 0))
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.RNG.randrange = old_randrange

    def test_rogue_544_damage_expr_parser_handles_monster_attacks(self):
        old_randrange = rogue.RNG.randrange
        try:
            rogue.RNG.randrange = lambda n: n - 1
            self.assertEqual(rogue.roll_damage_expr("1x8"), 8)
            self.assertEqual(rogue.roll_damage_expr("1x2/1x5/1x5"), 12)
            self.assertEqual(rogue.roll_damage_expr("0x0"), 0)
        finally:
            rogue.RNG.randrange = old_randrange

    def test_rogue_544_fight_helper_roll_damage_expr_sums_damage_parts(self):
        # Rogue 5.4.4 fight.c:roll_em() parses each "%dx%d" damage part.
        import rogue_fight

        rolls = []

        self.assertEqual(
            rogue_fight.roll_damage_expr("1x2/1x5/1x5", lambda n, sides: rolls.append((n, sides)) or n * sides),
            12,
        )
        self.assertEqual(rolls, [(1, 2), (1, 5), (1, 5)])

    def test_rogue_544_roll_em_swings_once_per_damage_part(self):
        # Rogue 5.4.4 fight.c:roll_em() calls swing() inside the damage-part loop.
        game = new_game(seed=8)
        set_open_floor(game)
        game.p.hp = 20
        monster = monster_at(game.p.x + 1, game.p.y, damage="1x1/1x1")
        game.mons = [monster]
        swings = iter([False, True])
        game.swing_hits = lambda at_lvl, op_arm, wplus: next(swings)

        game.m_attack(monster)

        self.assertEqual(game.p.hp, 19)

    def test_rogue_544_fight_helper_roll_em_damage_adds_only_hit_parts(self):
        # Rogue 5.4.4 fight.c:roll_em() rolls damage only after each successful swing().
        import rogue_fight

        swings = iter([False, True])
        rolls = []

        hit, damage = rogue_fight.roll_em_damage(
            "1x1/1x4",
            swing=lambda: next(swings),
            roll_part=lambda part: rolls.append(part) or 4,
            dplus=1,
            add_dam=2,
        )

        self.assertTrue(hit)
        self.assertEqual(damage, 7)
        self.assertEqual(rolls, ["1x4"])

    def test_rogue_544_roll_em_gives_monster_plus_four_when_player_cannot_act(self):
        # Rogue 5.4.4 command.c clears player ISRUN during no_command;
        # fight.c:roll_em() gives +4 to hit when the defender lacks ISRUN.
        game = new_game(seed=8)
        set_open_floor(game)
        game.p.no_command = 1
        monster = monster_at(game.p.x + 1, game.p.y, damage="1x1")
        seen_wplus = []
        game.swing_hits = lambda at_lvl, op_arm, wplus: seen_wplus.append(wplus) or False

        game.roll_monster_attack(monster)

        self.assertEqual(seen_wplus, [4])

    def test_rogue_544_fight_helper_hit_plus_adds_four_when_defender_not_running(self):
        # Rogue 5.4.4 fight.c:roll_em() adds +4 when !ISRUN on the defender.
        import rogue_fight

        self.assertEqual(rogue_fight.hit_plus_vs_defender(0, defender_running=False), 4)
        self.assertEqual(rogue_fight.hit_plus_vs_defender(2, defender_running=True), 2)

    def test_rogue_544_fight_helper_weapon_profile_uses_hurl_damage_and_launcher_pluses(self):
        # Rogue 5.4.4 fight.c:roll_em() uses o_hurldmg and adds launcher pluses for matching missiles.
        import rogue_fight

        damage, hplus, dplus = rogue_fight.weapon_profile(
            weapon={"damage": "1d1", "hurl_damage": "2d3", "missile": True, "launcher": 2},
            hit_plus=1,
            dam_plus=2,
            thrown=True,
            ring_hit_bonus=0,
            ring_damage_bonus=0,
            launcher_kind=2,
            launcher_hit_plus=3,
            launcher_dam_plus=4,
        )

        self.assertEqual((damage, hplus, dplus), ("2d3", 4, 6))

    def test_rogue_544_fight_helper_strength_tables_match_source(self):
        # Rogue 5.4.4 fight.c:str_plus/add_dam tables clamp by strength index.
        import rogue_fight

        self.assertEqual(rogue_fight.str_hit_plus(0), -7)
        self.assertEqual(rogue_fight.str_hit_plus(31), 3)
        self.assertEqual(rogue_fight.str_hit_plus(40), 3)
        self.assertEqual(rogue_fight.str_dam_plus(16), 1)
        self.assertEqual(rogue_fight.str_dam_plus(31), 6)

    def test_rogue_544_fight_and_attack_stop_running_and_reset_quiet(self):
        # Rogue 5.4.4 fight.c:fight()/attack() clear count/running and set quiet = 0.
        game = new_game(seed=8)
        set_open_floor(game)
        player_target = monster_at(game.p.x + 1, game.p.y, hp=20)
        game.dashing = True
        game.p.quiet = 19
        game.p_attack(player_target)
        self.assertFalse(game.dashing)
        self.assertEqual(game.p.quiet, 0)

        monster = monster_at(game.p.x + 1, game.p.y, hp=20, damage="1x1")
        game.dashing = True
        game.p.quiet = 19
        game.m_attack(monster)
        self.assertFalse(game.dashing)
        self.assertEqual(game.p.quiet, 0)

    def test_rogue_544_venus_flytrap_miss_still_deals_vf_hit(self):
        # Rogue 5.4.4 fight.c:attack() subtracts vf_hit when an F misses.
        game = new_game(seed=8)
        set_open_floor(game)
        flytrap = monster_at(game.p.x + 1, game.p.y, "F", "venus flytrap", damage="0x0", flags="hold")
        flytrap.vf_hit = 4
        game.p.hp = 20
        game.swing_hits = lambda at_lvl, op_arm, wplus: False

        game.m_attack(flytrap)

        self.assertEqual(game.p.hp, 16)

    def test_rogue_544_fight_helper_venus_flytrap_miss_subtracts_vf_hit(self):
        # Rogue 5.4.4 fight.c:attack() applies vf_hit even on a Venus Flytrap miss.
        import rogue_fight

        self.assertEqual(rogue_fight.venus_flytrap_miss_hp(20, 4), 16)
        self.assertEqual(rogue_fight.venus_flytrap_miss_hp(20, 0), 20)

    def test_rogue_544_venus_flytrap_hit_updates_next_damage_expr(self):
        # Rogue 5.4.4 fight.c:attack() sets monsters['F'-'A'].m_stats.s_dmg to "%dx1".
        game = new_game(seed=8)
        set_open_floor(game)
        flytrap = monster_at(game.p.x + 1, game.p.y, "F", "venus flytrap", damage="0x0", flags="hold")
        game.p.hp = 20
        game.swing_hits = lambda at_lvl, op_arm, wplus: True

        game.m_attack(flytrap)

        self.assertEqual(flytrap.vf_hit, 1)
        self.assertEqual(flytrap.damage_expr, "1x1")
        self.assertEqual(game.p.hp, 19)

    def test_rogue_544_fight_helper_venus_flytrap_hit_increments_vf_hit(self):
        # Rogue 5.4.4 fight.c:attack() increments vf_hit and sets next F damage to "%dx1".
        import rogue_fight

        self.assertEqual(rogue_fight.venus_flytrap_hit(3), (4, "4x1"))

    def test_rogue_544_killing_venus_flytrap_resets_hold_damage(self):
        # Rogue 5.4.4 fight.c:killed() clears ISHELD/vf_hit and restores F damage.
        game = new_game(seed=8)
        set_open_floor(game)
        flytrap = monster_at(game.p.x + 1, game.p.y, "F", "venus flytrap", hp=1, damage="3x1", flags="hold")
        flytrap.vf_hit = 3
        game.p.held_by = flytrap
        game.mons = [flytrap]
        game.roll_player_attack = lambda m, weap=None, thrown=False: (True, 1)

        game.p_attack(flytrap)

        self.assertIsNone(game.p.held_by)
        self.assertEqual(flytrap.vf_hit, 0)
        self.assertEqual(flytrap.damage_expr, "0x0")

    def test_rogue_544_fight_helper_venus_flytrap_release_resets_hold_damage(self):
        # Rogue 5.4.4 fight.c:killed() clears vf_hit and restores F damage to "0x0".
        import rogue_fight

        self.assertEqual(rogue_fight.venus_flytrap_release(), (0, "0x0"))

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

        self.assertTrue(any("the hobgoblin" in m.lower() for m in game.msgs))
        self.assertFalse(any("(" in m and "dmg" not in m.lower() for m in game.msgs))

        game.msgs = []
        monster.armor = -100
        game.p_attack(monster)
        self.assertTrue(any("the hobgoblin" in m.lower() for m in game.msgs))

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

    def test_rogue544_passages_do_passages_fixed_seed_audits_tree_and_extra_edges(self):
        # Rogue 5.4.4 passages.c:do_passages() first connects 9 rooms with
        # 8 spanning-tree edges, then attempts rnd(5) extra adjacent edges.
        random.seed(44)
        audit = rogue.DGen._passage_edges(audit=True)

        self.assertEqual(
            audit["tree"],
            [(6, 7), (6, 3), (3, 4), (3, 0), (0, 1), (4, 5), (5, 8), (5, 2)],
        )
        self.assertEqual(audit["extra"], [(2, 1), (8, 7)])
        self.assertEqual(audit["edges"], audit["tree"] + audit["extra"])

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

    def test_rogue544_lit_room_does_not_reveal_corridor_beyond_far_door(self):
        # Rogue 5.4.4 rooms.c:enter_room() lights only the room's own cells.
        # Corridor tiles beyond a door become visible only when the player is
        # adjacent (misc.c:look() 3x3), not merely because the door exists.
        game = new_game(seed=14)
        room = rogue.Room(5, 5, 10, 6)
        game.rooms = [room]
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        rogue.DGen._room(game.tm, room)
        door_x, door_y = room.x, room.cy
        game.tm[door_y][door_x] = rogue.T_DOOR
        corridor_x = door_x - 1
        game.tm[door_y][corridor_x] = rogue.T_CORR
        # Place the player at the far (right) side of the room, >2 tiles from
        # the left door so the 3x3 look zone never reaches the corridor.
        game.p.x, game.p.y = room.x + room.w - 2, room.cy

        game.update_fov()

        self.assertIn((door_x, door_y), game.visible)
        self.assertNotIn((corridor_x, door_y), game.visible)

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

    def test_settings_collect_display_and_input_options_without_changing_state(self):
        game = new_game(seed=240, lang=rogue.LANG_JA)

        self.assertIsInstance(game.settings, rogue.Settings)
        self.assertEqual(game.settings.language, rogue.LANG_JA)
        self.assertEqual(game.lang, rogue.LANG_JA)
        self.assertTrue(game.settings.auto_pickup)
        self.assertTrue(game.auto_pickup)
        self.assertEqual(game.settings.palette, rogue.DEFAULT_PALETTE)
        self.assertTrue(game.settings.show_run_steps)
        self.assertEqual(rogue.DASH_INTERVAL, 1)
        self.assertEqual(game.run_step_interval(), rogue.DASH_INTERVAL)
        before = (game.turn, game.p.depth, len(game.mons), len(game.gitems))

        game.auto_pickup = False
        game.lang = rogue.LANG_EN
        game.settings.show_run_steps = False

        self.assertFalse(game.settings.auto_pickup)
        self.assertEqual(game.settings.language, rogue.LANG_EN)
        self.assertEqual(game.run_step_interval(), 1)
        self.assertEqual((game.turn, game.p.depth, len(game.mons), len(game.gitems)), before)

    def test_settings_palette_applies_named_palette(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings(palette="gbc_high_contrast")
        old_colors = getattr(rogue.pyxel, "colors", None)
        try:
            rogue.pyxel.colors = []
            game.apply_palette()
            self.assertEqual(
                rogue.pyxel.colors[: len(rogue.GBC_HIGH_CONTRAST_PALETTE)],
                rogue.GBC_HIGH_CONTRAST_PALETTE,
            )
        finally:
            if old_colors is None:
                del rogue.pyxel.colors
            else:
                rogue.pyxel.colors = old_colors

    def test_palette_options_are_three_32_color_candidates(self):
        self.assertEqual(rogue.PALETTE_IDS, ("gbc", "gbc_high_contrast", "flexoki_light"))
        for palette_id in rogue.PALETTE_IDS:
            self.assertEqual(len(rogue.PALETTES[palette_id]), 32)
        self.assertEqual(rogue.Settings(palette="unknown").palette, rogue.DEFAULT_PALETTE)

    def test_flexoki_light_uses_readable_monster_colors(self):
        game = new_game(seed=242)
        game.settings.palette = "flexoki_light"

        self.assertEqual(game.monster_color("K"), 30)

    def test_assist_palette_toggle_changes_display_only(self):
        game = new_game(seed=241)
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
        old_colors = getattr(rogue.pyxel, "colors", None)
        try:
            rogue.pyxel.colors = []
            game.st = rogue.ST_AUX
            game.acur = rogue.AUX_ACTIONS.index("Palette")
            rogue.pyxel.set_input(
                held={rogue.pyxel.GAMEPAD1_BUTTON_A},
                pressed={rogue.pyxel.GAMEPAD1_BUTTON_A},
            )

            game.update()

            self.assertEqual(game.settings.palette, "flexoki_light")
            self.assertEqual(
                rogue.pyxel.colors[: len(rogue.FLEXOKI_LIGHT_PALETTE)],
                rogue.FLEXOKI_LIGHT_PALETTE,
            )
            self.assertIn("Palette: Flexoki Light.", game.msgs)
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
        finally:
            rogue.pyxel.set_input()
            if old_colors is None:
                del rogue.pyxel.colors
            else:
                rogue.pyxel.colors = old_colors

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

    def test_rogue_544_full_pack_does_not_stack_floor_food(self):
        # Rogue 5.4.4 pack.c:add_pack() calls pack_room() before stacking food.
        game = new_game(seed=3301)
        game.gitems = []
        game.p.inv = [rogue.Item(rogue.CAT_FOOD, 0)] + [
            rogue.Item(rogue.CAT_POT, i % len(rogue.POTIONS)) for i in range(rogue.INV_MAX - 1)
        ]
        item = rogue.Item(rogue.CAT_FOOD, 0)
        item.x, item.y = game.p.x, game.p.y
        game.gitems.append(item)

        game.do_pickup()

        self.assertIn(item, game.gitems)
        self.assertEqual(game.p.inv[0].qty, 1)
        self.assertIn("pack too full", game.msgs)

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

    def test_explored_stairs_remain_visible_after_leaving_room(self):
        game = new_game(seed=342)
        set_open_floor(game)
        sx, sy = game.p.x, game.p.y
        game.tm[sy][sx] = rogue.T_STAIR
        game.visible = set()
        game.explored = {(sx, sy)}
        calls = []
        game.txt = lambda x, y, s, c: calls.append((str(s), c))

        game.draw_zoom()

        self.assertIn(("%", 29), calls)

    def test_explored_memory_uses_readable_dim_color(self):
        game = new_game(seed=342)
        set_open_floor(game)
        sx, sy = game.p.x, game.p.y
        game.visible = set()
        game.explored = {(sx, sy)}
        calls = []
        game.txt = lambda x, y, s, c: calls.append((str(s), c))

        game.draw_zoom()

        self.assertIn((".", rogue.MEMORY_TILE_COLOR), calls)
        self.assertNotIn((".", 1), calls)

    def test_rogue_544_blind_player_still_draws_hero(self):
        # Rogue 5.4.4 misc.c:look() skips other cells while ISBLIND, but still draws hero.
        game = new_game(seed=343)
        set_open_floor(game)
        game.p.blind = 10
        game.update_fov()
        calls = []
        game.txt = lambda x, y, s, c: calls.append(str(s))

        game.draw_zoom()

        self.assertIn("@", calls)
        self.assertNotIn(".", calls)

    def test_hud_title_includes_build_revision_stamp(self):
        game = new_game(seed=344)
        calls = []
        game.txt = lambda x, y, s, c: calls.append(str(s))

        game.draw_title()

        self.assertIn("Rogue V5", calls)
        self.assertIn(rogue.UI_BUILD, calls)
        self.assertRegex(rogue.UI_BUILD, r"^\d{6}_\d{4}$")

    def test_rogue_py_commits_update_ui_build_stamp(self):
        # AGENTS.md / DESIGN.md: player-visible rogue.py changes must carry UI_BUILD.
        try:
            subprocess.check_output(
                ["git", "rev-parse", "--verify", "HEAD^"],
                cwd=ROOT,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            changed = subprocess.check_output(
                ["git", "diff", "--name-only", "HEAD^..HEAD"],
                cwd=ROOT,
                text=True,
            ).splitlines()
            diff = subprocess.check_output(
                ["git", "diff", "HEAD^..HEAD", "--", "rogue.py"],
                cwd=ROOT,
                text=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.skipTest("git history unavailable")
        if "rogue.py" in changed:
            self.assertIn("+UI_BUILD =", diff)

    def test_hp_damage_bar_persists_for_current_turn_instead_of_frame_timer(self):
        game = new_game(seed=345)
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

    def test_hp_damage_bar_stays_orange_when_hp_is_low(self):
        game = new_game(seed=343)
        game.txt = lambda *args: None
        rects = []
        old_rect = rogue.pyxel.rect
        try:
            rogue.pyxel.rect = lambda *args: rects.append(args)
            game.p.max_hp = 20
            game.p.hp = 10
            game.draw_stat()
            game.p.hp = 4
            rects.clear()

            game.draw_stat()

            self.assertIn(21, [args[-1] for args in rects])
            self.assertIn(22, [args[-1] for args in rects])
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

    def test_message_log_uses_seven_rows_with_current_turn_highlighted(self):
        game = new_game(seed=35)
        calls = []
        game.txt = lambda x, y, s, c: calls.append((str(s), c))
        game.msgs = ["hidden", "one", "two", "three", "four", "five", "six", "latest"]
        game.msg_turns = [0, 0, 0, 1, 1, 1, 1, 1]
        game.turn = 1

        game.draw_msgs()

        self.assertEqual(rogue.MSG_LINES, 7)
        self.assertEqual([text for text, _ in calls], ["one", "two", "three", "four", "five", "six", "latest"])
        self.assertEqual([color for _, color in calls], [6, 6, 30, 30, 30, 30, 30])

    def test_message_before_end_turn_stays_highlighted_after_turn_advances(self):
        game = new_game(seed=35)
        set_open_floor(game)
        game.msgs = []
        game.msg_turns = []
        game.turn_msg_start = 0
        calls = []
        game.txt = lambda x, y, s, c: calls.append((str(s), c))

        game.msg_text("you hit the hobgoblin")
        game.end_turn()
        game.draw_msgs()

        self.assertEqual(calls, [("you hit the hobgoblin", 30)])

    def test_keyboard_esc_opens_and_cancels_menu_back_to_play(self):
        game = new_game(seed=35)

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_ESCAPE}, pressed={rogue.pyxel.KEY_ESCAPE})
        game.update()
        self.assertEqual(game.st, rogue.ST_MENU)

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_ESCAPE}, pressed={rogue.pyxel.KEY_ESCAPE})
        game.update()
        self.assertEqual(game.st, rogue.ST_PLAY)

    def test_keyboard_z_and_c_are_not_pad_action_or_cancel(self):
        game = new_game(seed=35)
        game.start_item_action = lambda aname, cat=None: setattr(game, "shortcut", aname)

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_C}, pressed={rogue.pyxel.KEY_C})
        game.update()
        self.assertEqual(game.st, rogue.ST_PLAY)

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_Z}, pressed={rogue.pyxel.KEY_Z})
        game.update()
        self.assertEqual(game.shortcut, "Zap")

        game.st = rogue.ST_MENU
        rogue.pyxel.set_input(held={rogue.pyxel.KEY_C}, pressed={rogue.pyxel.KEY_C})
        game.update()
        self.assertEqual(game.st, rogue.ST_MENU)

    def test_rogue_544_keyboard_upper_p_opens_put_on_ring(self):
        # Rogue 5.4.4 command.c:command() maps 'P' to rings.c:ring_on().
        game = new_game(seed=35)
        game.start_item_action = lambda aname, cat=None: setattr(game, "shortcut", (aname, cat))

        rogue.pyxel.set_input(
            held={rogue.pyxel.KEY_P, rogue.pyxel.KEY_SHIFT},
            pressed={rogue.pyxel.KEY_P},
        )
        game.update()

        self.assertEqual(game.shortcut, ("Put on", None))

    def test_keyboard_overlays_use_enter_escape_not_z_c(self):
        game = new_game(seed=35)
        selected = []
        game.st = rogue.ST_MENU
        game.menu_select = lambda: selected.append("menu")

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_Z}, pressed={rogue.pyxel.KEY_Z})
        game.update()
        self.assertEqual(selected, [])
        self.assertEqual(game.st, rogue.ST_MENU)

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_RETURN}, pressed={rogue.pyxel.KEY_RETURN})
        game.update()
        self.assertEqual(selected, ["menu"])

        game.st = rogue.ST_ITEM
        confirmed = []
        game.item_confirm = lambda: confirmed.append("item")
        rogue.pyxel.set_input(held={rogue.pyxel.KEY_Z}, pressed={rogue.pyxel.KEY_Z})
        game.update()
        self.assertEqual(confirmed, [])
        self.assertEqual(game.st, rogue.ST_ITEM)

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_RETURN}, pressed={rogue.pyxel.KEY_RETURN})
        game.update()
        self.assertEqual(confirmed, ["item"])

        game.st = rogue.ST_MENU
        rogue.pyxel.set_input(held={rogue.pyxel.KEY_C}, pressed={rogue.pyxel.KEY_C})
        game.update()
        self.assertEqual(game.st, rogue.ST_MENU)

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_ESCAPE}, pressed={rogue.pyxel.KEY_ESCAPE})
        game.update()
        self.assertEqual(game.st, rogue.ST_PLAY)

    def test_keyboard_escape_closes_help_and_inventory_without_blocking_later_keys(self):
        game = new_game(seed=35)
        game.st = rogue.ST_HELP

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_ESCAPE}, pressed={rogue.pyxel.KEY_ESCAPE})
        game.update()
        self.assertEqual(game.st, rogue.ST_PLAY)

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_I}, pressed={rogue.pyxel.KEY_I})
        game.update()
        self.assertEqual(game.st, rogue.ST_INVENTORY)

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_ESCAPE}, pressed={rogue.pyxel.KEY_ESCAPE})
        game.update()
        self.assertEqual(game.st, rogue.ST_PLAY)

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_QUESTION}, pressed={rogue.pyxel.KEY_QUESTION})
        game.update()
        self.assertEqual(game.st, rogue.ST_HELP)

    def test_keyboard_space_toggles_start_action(self):
        game = new_game(seed=35)
        self.assertFalse(game.diag_assist)

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_SPACE}, pressed={rogue.pyxel.KEY_SPACE})
        game.update()

        self.assertTrue(game.diag_assist)

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

    def test_rogue_544_score_entry_uses_ninety_percent_gold_on_death(self):
        entry = rogue.build_score_entry(
            score=0,
            result_flags="killed",
            level=7,
            killer="hobgoblin",
            player_name="tester",
            timestamp="2026-04-24T12:00:00Z",
            gold=123,
        )

        self.assertEqual(entry["score"], 110)
        self.assertEqual(entry["result_flags"], "killed")
        self.assertEqual(entry["killer"], "hobgoblin")

    def test_rogue_544_score_entry_keeps_full_gold_for_quit_and_win(self):
        quit_entry = rogue.build_score_entry(
            score=0,
            result_flags="quit",
            level=7,
            killer="",
            player_name="tester",
            timestamp="2026-04-24T12:00:00Z",
            gold=123,
        )
        win_entry = rogue.build_score_entry(
            score=0,
            result_flags="winner",
            level=26,
            killer="",
            player_name="tester",
            timestamp="2026-04-24T12:00:00Z",
            gold=456,
        )

        self.assertEqual(quit_entry["score"], 123)
        self.assertEqual(win_entry["score"], 456)

    def test_top_scores_sort_by_score_and_limit_to_ten(self):
        entries = [
            {"score": score, "player_name": f"p{score}", "result_flags": "quit", "level": 1, "killer": "", "timestamp": "t"}
            for score in (5, 42, 17, 90, 12, 33, 75, 10, 60, 55, 99)
        ]

        top = rogue.get_top_scores(entries, limit=10)

        self.assertEqual(len(top), 10)
        self.assertEqual([entry["score"] for entry in top], [99, 90, 75, 60, 55, 42, 33, 17, 12, 10])

    def test_rogue_544_score_lines_match_rip_score_printf(self):
        # Rogue 5.4.4 rip.c:score() prints "Top Ten Scores:", "   Score Name",
        # then "%2d %5d %s: %s on level %d" plus killer text and period.
        entries = [
            {"score": 346, "player_name": "masatora", "result_flags": "killed", "level": 4, "killer": "orc"},
            {"score": 194, "player_name": "masatora", "result_flags": "killed", "level": 3, "killer": "bat"},
            {"score": 109, "player_name": "masatora", "result_flags": "quit", "level": 1, "killer": ""},
            {"score": 47, "player_name": "masatora", "result_flags": "killed", "level": 2, "killer": "kestrel"},
        ]

        lines = rogue.format_top_score_lines(entries)

        self.assertEqual(
            lines,
            [
                "Top Ten Scores:",
                "   Score Name",
                " 1   346 masatora: killed on level 4 by an orc.",
                " 2   194 masatora: killed on level 3 by a bat.",
                " 3   109 masatora: quit on level 1.",
                " 4    47 masatora: killed on level 2 by a kestrel.",
            ],
        )

    def test_aux_quit_enters_quit_confirm_state(self):
        game = new_game(seed=35)
        game.open_aux()
        game.acur = rogue.AUX_ACTIONS.index("Quit")

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_RETURN}, pressed={rogue.pyxel.KEY_RETURN})
        game.update()

        self.assertEqual(game.st, rogue.ST_QUIT_CONFIRM)

    def test_quit_confirm_cancel_returns_to_play(self):
        game = new_game(seed=35)
        game.st = rogue.ST_QUIT_CONFIRM

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_ESCAPE}, pressed={rogue.pyxel.KEY_ESCAPE})
        game.update()

        self.assertEqual(game.st, rogue.ST_PLAY)

    def test_result_screens_advance_to_score_screen_before_new_game(self):
        for state in (rogue.ST_DEAD, rogue.ST_WIN, rogue.ST_QUIT):
            game = new_game(seed=35)
            game.st = state

            rogue.pyxel.set_input(held={rogue.pyxel.KEY_RETURN}, pressed={rogue.pyxel.KEY_RETURN})
            game.update()

            self.assertEqual(game.st, rogue.ST_SCORE, state)

    def test_score_screen_starts_new_game_on_confirm(self):
        game = new_game(seed=35)
        game.st = rogue.ST_SCORE
        game.turn = 12

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_RETURN}, pressed={rogue.pyxel.KEY_RETURN})
        game.update()

        self.assertEqual(game.st, rogue.ST_PLAY)
        self.assertEqual(game.turn, 0)

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
        game.gitems = []
        item = rogue.Item(rogue.CAT_WPN, 4)
        game.p.inv = [item]
        game.throw(item, 1, 0)
        self.assertIsNotNone(game.throw_anim)
        self.assertEqual(game.throw_anim["path"], [(3, 2), (4, 2), (5, 2), (6, 2)])
        self.assertEqual(game.gitems, [])

        for _ in range(len(game.throw_anim["path"]) * game.throw_anim["delay"]):
            rogue.pyxel.set_input()
            game.update()

        self.assertEqual((game.gitems[-1].x, game.gitems[-1].y), (6, 2))

    def test_rogue_544_thrown_kill_waits_until_animation_finishes(self):
        # Rogue 5.4.4 weapons.c:missile()/do_motion() resolves hit after motion finishes.
        game = new_game(seed=372)
        set_open_floor(game)
        arrow = rogue.Item(rogue.CAT_WPN, 3, qty=1)
        monster = monster_at(game.p.x + 2, game.p.y, hp=1, exp=0)
        game.p.inv = [arrow]
        game.mons = [monster]
        game.roll_player_attack = lambda m, weap=None, thrown=False: (True, 1)

        game.throw(arrow, 1, 0)

        self.assertTrue(monster.alive)
        self.assertIn(monster, game.mons)

        for _ in range(len(game.throw_anim["path"]) * game.throw_anim["delay"]):
            rogue.pyxel.set_input()
            game.update()

        self.assertFalse(monster.alive)
        self.assertNotIn(monster, game.mons)

    def test_rogue_544_throw_motion_finishes_before_monster_turn(self):
        # Rogue 5.4.4 command.c:t calls weapons.c:missile()/do_motion() before after-turn monsters.
        game = new_game(seed=371)
        set_open_floor(game)
        item = rogue.Item(rogue.CAT_WPN, 4)
        game.p.inv = [item]
        game.fitems = [item]
        game.cact = "Throw"
        game.throw_dir = (1, 0)
        game.st = rogue.ST_ITEM
        turns = []
        game.m_turn = lambda monster: turns.append(monster)
        monster = monster_at(game.p.x, game.p.y + 3)
        monster.running = True
        game.mons = [monster]

        game.item_confirm()

        self.assertIsNotNone(game.throw_anim)
        self.assertEqual(turns, [])

        for _ in range(len(game.throw_anim["path"]) * game.throw_anim["delay"]):
            rogue.pyxel.set_input()
            game.update()

        self.assertEqual(len(turns), 1)

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
        scroll = rogue.Item(rogue.CAT_SCR, next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "enchant weapon"))
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

    def test_rogue_544_extra_healing_uses_plain_quaff_message(self):
        # Rogue 5.4.4 potions.c:P_XHEAL msg("you begin to feel much better").
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
        self.assertIn("you begin to feel much better", game.msgs)
        self.assertNotIn("You feel much better. (+1)", game.msgs)

    def test_rogue_544_extra_healing_can_raise_max_hp_by_two(self):
        # Rogue 5.4.4 potions.c:P_XHEAL increments max_hp twice when the overflow exceeds level + 1.
        game = new_game(seed=392)
        extra_healing = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "extra healing")
        potion = rogue.Item(rogue.CAT_POT, extra_healing)
        game.p.inv.append(potion)
        game.p.level = 1
        game.p.hp = game.p.max_hp
        old_roll = rogue.RNG.roll
        try:
            rogue.RNG.roll = lambda number, sides: 8
            game.use_pot(potion)
        finally:
            rogue.RNG.roll = old_roll

        self.assertEqual((game.p.hp, game.p.max_hp), (18, 18))

    def test_rogue_544_extra_healing_small_overflow_raises_max_hp_by_one(self):
        # Rogue 5.4.4 potions.c:P_XHEAL skips the pre-increment unless overflow exceeds level + 1.
        game = new_game(seed=393)
        extra_healing = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "extra healing")
        potion = rogue.Item(rogue.CAT_POT, extra_healing)
        game.p.inv.append(potion)
        game.p.level = 2
        game.p.hp = game.p.max_hp
        old_roll = rogue.RNG.roll
        try:
            rogue.RNG.roll = lambda number, sides: 1
            game.use_pot(potion)
        finally:
            rogue.RNG.roll = old_roll

        self.assertEqual((game.p.hp, game.p.max_hp), (17, 17))

    def test_rogue_544_extra_healing_rolls_level_d8(self):
        # Rogue 5.4.4 potions.c:P_XHEAL uses roll(pstats.s_lvl, 8), not roll(1, 8) * level.
        game = new_game(seed=396)
        extra_healing = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "extra healing")
        potion = rogue.Item(rogue.CAT_POT, extra_healing)
        game.p.inv.append(potion)
        game.p.level = 3
        calls = []
        old_roll = rogue.RNG.roll
        try:
            rogue.RNG.roll = lambda number, sides: calls.append((number, sides)) or 5
            game.use_pot(potion)
        finally:
            rogue.RNG.roll = old_roll

        self.assertEqual(calls, [(3, 8)])

    def test_rogue_544_extra_healing_ends_hallucination(self):
        # Rogue 5.4.4 potions.c:P_XHEAL calls daemons.c:come_down().
        game = new_game(seed=394)
        extra_healing = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "extra healing")
        potion = rogue.Item(rogue.CAT_POT, extra_healing)
        game.p.inv.append(potion)
        game.p.hallucinating = 10
        game.fuses.fuse("come_down", 10, rogue.rogue_daemons.AFTER)

        game.use_pot(potion)

        self.assertEqual(game.p.hallucinating, 0)
        self.assertIn("Everything looks SO boring now.", game.msgs)

    def test_rogue_544_healing_can_raise_max_hp_by_one(self):
        # Rogue 5.4.4 potions.c:P_HEALING sets hp = ++max_hp, then uses a plain msg.
        game = new_game(seed=391)
        healing = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "healing")
        potion = rogue.Item(rogue.CAT_POT, healing)
        game.p.inv.append(potion)
        game.p.level = 1
        game.p.hp = game.p.max_hp
        old_roll = rogue.RNG.roll
        try:
            rogue.RNG.roll = lambda number, sides: 1
            game.use_pot(potion)
        finally:
            rogue.RNG.roll = old_roll

        self.assertEqual((game.p.hp, game.p.max_hp), (17, 17))
        self.assertIn("you begin to feel better", game.msgs)
        self.assertNotIn("You feel better. (+1)", game.msgs)

    def test_rogue_544_healing_calls_sight_when_blind(self):
        # Rogue 5.4.4 potions.c:P_HEALING calls daemons.c:sight().
        game = new_game(seed=395)
        healing = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "healing")
        potion = rogue.Item(rogue.CAT_POT, healing)
        game.p.inv.append(potion)
        game.p.blind = 20

        game.use_pot(potion)

        self.assertEqual(game.p.blind, 0)
        self.assertIn("the veil of darkness lifts", game.msgs)

    def test_rogue_544_healing_sight_extinguishes_blindness_fuse(self):
        # Rogue 5.4.4 daemons.c:sight() calls extinguish(sight).
        game = new_game(seed=398)
        healing = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "healing")
        potion = rogue.Item(rogue.CAT_POT, healing)
        game.p.inv.append(potion)
        game.p.blind = 20
        game.fuses.fuse("sight", 20, rogue.rogue_daemons.AFTER)

        game.use_pot(potion)

        self.assertEqual(game.p.blind, 0)
        self.assertEqual(game.fuses.remaining("sight"), 0)

    def test_rogue_544_extra_healing_calls_sight_when_blind(self):
        # Rogue 5.4.4 potions.c:P_XHEAL calls daemons.c:sight().
        game = new_game(seed=399)
        extra_healing = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "extra healing")
        potion = rogue.Item(rogue.CAT_POT, extra_healing)
        game.p.inv.append(potion)
        game.p.blind = 20
        game.fuses.fuse("sight", 20, rogue.rogue_daemons.AFTER)

        game.use_pot(potion)

        self.assertEqual(game.p.blind, 0)
        self.assertEqual(game.fuses.remaining("sight"), 0)
        self.assertIn("the veil of darkness lifts", game.msgs)

    def test_rogue_544_see_invisible_calls_sight_when_blind(self):
        # Rogue 5.4.4 potions.c:P_SEEINVIS calls daemons.c:sight().
        game = new_game(seed=400)
        see_invisible = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "see invisible")
        potion = rogue.Item(rogue.CAT_POT, see_invisible)
        game.p.inv.append(potion)
        game.p.blind = 20
        game.fuses.fuse("sight", 20, rogue.rogue_daemons.AFTER)

        game.use_pot(potion)

        self.assertEqual(game.p.blind, 0)
        self.assertEqual(game.fuses.remaining("sight"), 0)
        self.assertIn("the veil of darkness lifts", game.msgs)

    def test_rogue_544_healing_rolls_level_d4(self):
        # Rogue 5.4.4 potions.c:P_HEALING uses roll(pstats.s_lvl, 4), not roll(1, 4) * level.
        game = new_game(seed=397)
        healing = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "healing")
        potion = rogue.Item(rogue.CAT_POT, healing)
        game.p.inv.append(potion)
        game.p.level = 3
        calls = []
        old_roll = rogue.RNG.roll
        try:
            rogue.RNG.roll = lambda number, sides: calls.append((number, sides)) or 5
            game.use_pot(potion)
        finally:
            rogue.RNG.roll = old_roll

        self.assertEqual(calls, [(3, 4)])

    def test_random_weapon_generation_changes_hit_plus_only(self):
        old_randint = rogue.random.randint
        old_randrange = rogue.random.randrange
        seq = iter([80, 0, 9, 2])
        try:
            rogue.random.randint = lambda a, b: (_ for _ in ()).throw(AssertionError("randint() used for item kind"))
            rogue.random.randrange = lambda n: next(seq)
            item = rogue.make_item(depth=10)
        finally:
            rogue.random.randint = old_randint
            rogue.random.randrange = old_randrange
        self.assertEqual(item.cat, rogue.CAT_WPN)
        self.assertTrue(item.cursed)
        self.assertEqual(item.hit_plus, -3)
        self.assertEqual(item.dam_plus, 0)

    def test_rogue_544_weapon_generation_uses_rng_rnd_for_enchant(self):
        # Rogue 5.4.4 things.c:new_thing() weapon curse/enchant uses rnd(100), then rnd(3).
        old_rnd = rogue.RNG.rnd
        old_randrange = rogue.RNG.randrange
        seq = iter([80, 0, 9, 2])
        try:
            rogue.RNG.rnd = lambda n: next(seq)
            rogue.RNG.randrange = lambda n: (_ for _ in ()).throw(AssertionError("randrange used"))
            item = rogue.make_item(depth=10)
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.RNG.randrange = old_randrange

        self.assertEqual(item.cat, rogue.CAT_WPN)
        self.assertTrue(item.cursed)
        self.assertEqual(item.hit_plus, -3)

    def test_rogue_544_random_armor_generation_uses_new_thing_curse_rates(self):
        # Rogue 5.4.4 things.c:new_thing() curses armor on rnd(100) < 20.
        old_randrange = rogue.random.randrange
        try:
            seq = iter([88, 0, 19, 2])
            rogue.random.randrange = lambda n: next(seq)
            item = rogue.make_item(depth=10)
        finally:
            rogue.random.randrange = old_randrange

        self.assertEqual(item.cat, rogue.CAT_ARM)
        self.assertTrue(item.cursed)
        self.assertEqual(item.ench, -3)

    def test_rogue_544_make_item_category_uses_rnd_100_not_float_random(self):
        # Rogue 5.4.4 things.c:new_thing() calls pick_one(things, NUMTHINGS), which uses rnd(100).
        old_random = rogue.random.random
        old_randint = rogue.random.randint
        old_randrange = rogue.random.randrange
        try:
            rogue.random.random = lambda: (_ for _ in ()).throw(AssertionError("random() used"))
            rogue.random.randint = lambda a, b: a
            rogue.random.randrange = lambda n: 0
            item = rogue.make_item(depth=10)
        finally:
            rogue.random.random = old_random
            rogue.random.randint = old_randint
            rogue.random.randrange = old_randrange

        self.assertEqual(item.cat, rogue.CAT_POT)

    def test_rogue_544_make_item_kind_uses_pick_one_weights(self):
        # Rogue 5.4.4 things.c:new_thing() uses pick_one() for pot_info/weap_info/arm_info.
        self.assertEqual(sum(i["prob"] for i in rogue.POTIONS), 100)
        self.assertEqual(sum(i["prob"] for i in rogue.WEAPONS), 100)
        self.assertEqual(sum(i["prob"] for i in rogue.ARMORS), 100)
        self.assertEqual(sum(i["prob"] for i in rogue.RINGS), 100)
        self.assertEqual(sum(i["prob"] for i in rogue.STICKS), 100)

    def test_rogue_544_generated_armor_is_unknown_until_worn(self):
        # Rogue 5.4.4 inv_name() hides armor enchant until ISKNOW; armor.c:wear() sets ISKNOW.
        game = new_game(seed=8)
        armor = rogue.Item(rogue.CAT_ARM, 1, ench=-2, cursed=True, known=False)
        game.p.arm = None

        self.assertEqual(game.item_name(armor), "ring mail")
        game.wear(armor)

        self.assertTrue(armor.known)
        self.assertEqual(game.item_name(armor), "-2 ring mail [protection 1] (being worn)")

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
        for _ in range(len(game.throw_anim["path"]) * game.throw_anim["delay"]):
            rogue.pyxel.set_input()
            game.update()
        self.assertEqual(monster.hp, 8)
        self.assertIn(arrow, game.gitems)

    def test_baseline_combat_message_uses_catalog(self):
        game = new_game(seed=41, lang=rogue.LANG_JA)
        monster = monster_at(game.p.x + 1, game.p.y, hp=1, armor=100, exp=5)
        game.p_attack(monster)
        self.assertFalse(monster.alive)
        self.assertIn("小鬼を倒した", game.msgs)
        self.assertFalse(any("exp" in msg.lower() for msg in game.msgs))

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

    def test_rogue_544_dash_stops_for_item_in_look_ahead_zone(self):
        # Rogue 5.4.4 misc.c:look() stops door_stop running on visible non-terrain ahead.
        game = new_game(seed=46)
        set_open_floor(game)
        game.dash_steps = 1
        item = rogue.Item(rogue.CAT_FOOD, 0)
        item.x, item.y = game.p.x + 1, game.p.y - 1
        game.gitems = [item]

        self.assertTrue(game.dash_should_stop_here(1, 0))

    def test_rogue_544_dash_ignores_far_visible_monster_outside_look_zone(self):
        # Rogue 5.4.4 misc.c:look() only scans the 3x3 cells around the hero.
        game = new_game(seed=46)
        set_open_floor(game)
        px, py = game.p.x, game.p.y
        monster = monster_at(px + 6, py)
        game.mons = [monster]
        game.update_fov()
        game.dashing = True
        game.dash_d = (1, 0)
        game.dash_steps = 1

        game.dash_step()

        self.assertEqual((game.p.x, game.p.y), (px + 1, py))

    def test_rogue_544_dash_stops_at_door_until_run_button_released(self):
        # Rogue 5.4.4 misc.c:look() clears running at a door_stop DOOR.
        game = new_game(seed=461)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        room = rogue.Room(5, 5, 8, 6)
        game.rooms = [room]
        rogue.DGen._room(game.tm, room)
        game.tm[7][12] = rogue.T_DOOR
        game.tm[7][13] = rogue.T_CORR
        game.tm[7][14] = rogue.T_CORR
        game.mons = []
        game.gitems = []
        game.traps = {}
        game.hidden_tiles = {}
        game.p.x, game.p.y = 10, 7
        game.update_fov()

        held = {rogue.pyxel.GAMEPAD1_BUTTON_B, rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT}
        rogue.pyxel.set_input(held=held, pressed=held)
        game.update()
        rogue.pyxel.set_input(held=held, pressed=set())
        game.update()
        game.update()
        self.assertEqual((game.p.x, game.p.y), (11, 7))
        self.assertFalse(game.dashing)

        game.update()
        self.assertEqual((game.p.x, game.p.y), (11, 7))

    def test_rogue_544_dash_can_restart_with_run_button_held_after_stop(self):
        # Rogue 5.4.4 command.c lets each shifted direction start do_run() again.
        game = new_game(seed=463)
        set_open_floor(game)
        px, py = game.p.x, game.p.y
        item = rogue.Item(rogue.CAT_FOOD, 0)
        item.x, item.y = px + 2, py
        game.gitems = [item]

        held = {rogue.pyxel.GAMEPAD1_BUTTON_B, rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT}
        rogue.pyxel.set_input(held=held, pressed=held)
        game.update()
        rogue.pyxel.set_input(held=held, pressed=set())
        game.update()
        self.assertFalse(game.dashing)
        self.assertEqual((game.p.x, game.p.y), (px + 1, py))

        game.gitems = []
        held = {rogue.pyxel.GAMEPAD1_BUTTON_B, rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT}
        rogue.pyxel.set_input(held=held, pressed={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT})
        game.update()

        self.assertTrue(game.dashing)
        self.assertEqual((game.p.x, game.p.y), (px + 2, py))

    def test_rogue_544_detect_monster_does_not_leave_floor_memory(self):
        # Rogue 5.4.4 potions.c:P_MFIND uses SEEMONST/turn_see(), not map memory.
        game = new_game(seed=462)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        old = (20, 10)
        game.tm[old[1]][old[0]] = rogue.T_FLOOR
        game.tm[old[1]][old[0] + 1] = rogue.T_FLOOR
        game.rooms = []
        game.visible = set()
        game.explored = set()
        game.cam_x = game.cam_y = 0
        game.p.x, game.p.y = 5, 5
        monster = monster_at(*old)
        game.mons = [monster]
        kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "monster detection")

        game.use_pot(rogue.Item(rogue.CAT_POT, kind))
        self.assertEqual(game.p.see_monsters, rogue.HUHDURATION)
        self.assertEqual(game.fuses.remaining("turn_see"), rogue.HUHDURATION)
        monster.x += 1
        game.visible = set()
        calls = []
        game.txt = lambda x, y, s, c: calls.append(((x, y), str(s), c))
        game.draw_zoom()

        self.assertNotIn(old, game.explored)
        self.assertNotIn(".", [s for _, s, _ in calls])
        self.assertIn("H", [s for _, s, _ in calls])

        game.p.see_monsters = 1
        game.fuses.extinguish("turn_see")
        game.fuses.fuse("turn_see", 1, rogue.rogue_daemons.AFTER)
        game.end_turn()

        self.assertEqual(game.p.see_monsters, 0)
        self.assertEqual(game.fuses.remaining("turn_see"), 0)

    def test_rogue_544_monster_detection_refuses_to_lengthen_existing_turn_see(self):
        # Rogue 5.4.4 potions.c:P_MFIND always calls fuse(turn_see), not lengthen().
        game = new_game(seed=493)
        potion_kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "monster detection")
        first = rogue.Item(rogue.CAT_POT, potion_kind)
        second = rogue.Item(rogue.CAT_POT, potion_kind)
        game.p.inv.extend([first, second])

        game.use_pot(first)
        game.use_pot(second)

        self.assertEqual(game.fuses.remaining("turn_see"), rogue.HUHDURATION)
        self.assertEqual(game.p.see_monsters, rogue.HUHDURATION)

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

    def test_rogue_544_fight_helper_ice_freeze_adds_duration_and_reports_initial_freeze(self):
        # Rogue 5.4.4 fight.c:attack() adds rnd(2)+2; message only when no_command was zero.
        import rogue_fight

        self.assertEqual(
            rogue_fight.ice_freeze(0, bore_level=50, rnd=lambda n: 1),
            (3, True, False),
        )
        self.assertEqual(
            rogue_fight.ice_freeze(5, bore_level=50, rnd=lambda n: 0),
            (7, False, False),
        )

    def test_rogue_544_ice_monster_refreezes_without_repeating_message(self):
        # Rogue 5.4.4 fight.c:attack() only prints the frozen message
        # when no_command was zero before adding rnd(2)+2.
        game = new_game(seed=503)
        set_open_floor(game)
        game.p.ac = 0
        game.p.hp = 99
        game.p.no_command = 5
        monster = monster_at(game.p.x + 1, game.p.y, "I", "ice monster", 10, 20, 100, "0x0", 5, "freeze")
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 0
            game.m_attack(monster)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(game.p.no_command, 7)
        self.assertNotIn("you are frozen", game.msgs)

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
        self.assertIn("you feel a bite in your leg and now feel weaker", game.msgs)

        game.save_vs_poison = lambda: True
        game.m_attack(monster)
        self.assertEqual(game.p.st, 9)

    def test_rogue_544_fight_helper_poison_bite_strength_loss(self):
        # Rogue 5.4.4 fight.c:attack() lowers Strength only after failed poison save and no sustain strength.
        import rogue_fight

        self.assertEqual(rogue_fight.poison_bite_strength(10, poison_saved=False, sustain_strength=False), (9, "weakened"))
        self.assertEqual(rogue_fight.poison_bite_strength(10, poison_saved=False, sustain_strength=True), (10, "sustained"))
        self.assertEqual(rogue_fight.poison_bite_strength(10, poison_saved=True, sustain_strength=False), (10, None))
        self.assertEqual(rogue_fight.poison_bite_strength(3, poison_saved=False, sustain_strength=False), (3, "floor"))

    def test_rogue_544_move_helper_can_rust_armor_matches_source_gate(self):
        # Rogue 5.4.4 move.c:rust_armor() skips NULL, non-armor, LEATHER, and o_arm >= 9.
        import rogue_move

        self.assertTrue(rogue_move.can_rust_armor(True, False, 8))
        self.assertFalse(rogue_move.can_rust_armor(False, False, 8))
        self.assertFalse(rogue_move.can_rust_armor(True, True, 8))
        self.assertFalse(rogue_move.can_rust_armor(True, False, 9))

    def test_rogue_544_move_helper_rust_armor_result_matches_source_branches(self):
        # Rogue 5.4.4 move.c:rust_armor() preserves protected/sustain armor, otherwise increments o_arm.
        import rogue_move

        self.assertEqual(rogue_move.rust_armor_result(protected=True, sustain_armor=False), "vanish")
        self.assertEqual(rogue_move.rust_armor_result(protected=False, sustain_armor=True), "vanish")
        self.assertEqual(rogue_move.rust_armor_result(protected=False, sustain_armor=False), "weaken")

    def test_rogue_544_move_helper_mysterious_trap_message_table_matches_source(self):
        # Rogue 5.4.4 move.c:be_trapped() T_MYST switch has 11 fixed message cases.
        import rogue_move

        self.assertEqual(rogue_move.mysterious_trap_message(0), ("move.you_are_suddenly_in_a_parallel_dimension", None))
        self.assertEqual(rogue_move.mysterious_trap_message(1), ("move.the_light_in_here_suddenly_seems_color", "color"))
        self.assertEqual(rogue_move.mysterious_trap_message(6), ("move.value_sparks_dance_across_your_armor", "value"))
        self.assertEqual(rogue_move.mysterious_trap_message(10), ("move.you_pack_turns_value", "value"))

    def test_rogue_544_move_helper_rndmove_tries_one_random_square_only(self):
        # Rogue 5.4.4 move.c:rndmove() rolls y then x once and stays put if that square is bad.
        import rogue_move

        rng = SequenceRng([0, 2])
        self.assertEqual(
            rogue_move.rndmove((10, 10), rng.rnd, lambda src, dst: False),
            (10, 10),
        )
        self.assertEqual(rng.calls, [3, 3])

        rng = SequenceRng([2, 0])
        self.assertEqual(
            rogue_move.rndmove((10, 10), rng.rnd, lambda src, dst: True),
            (9, 11),
        )

    def test_rogue_544_chase_helper_random_move_gate_matches_source_order(self):
        # Rogue 5.4.4 chase.c:chase() tests ISHUH, Phantom, then Bat random movement.
        import rogue_chase

        rng = SequenceRng([1])
        self.assertTrue(rogue_chase.should_random_move(1, "O", rng.rnd))
        self.assertEqual(rng.calls, [5])

        rng = SequenceRng([0])
        self.assertTrue(rogue_chase.should_random_move(0, "P", rng.rnd))
        self.assertEqual(rng.calls, [5])

        rng = SequenceRng([0])
        self.assertTrue(rogue_chase.should_random_move(0, "B", rng.rnd))
        self.assertEqual(rng.calls, [2])

        rng = SequenceRng([])
        self.assertFalse(rogue_chase.should_random_move(0, "O", rng.rnd))
        self.assertEqual(rng.calls, [])

    def test_rogue_544_chase_helper_confusion_clears_on_rnd20_zero(self):
        # Rogue 5.4.4 chase.c:chase() clears ISHUH after random movement when rnd(20)==0.
        import rogue_chase

        rng = SequenceRng([0])
        self.assertTrue(rogue_chase.confusion_clears_after_random_move(1, rng.rnd))
        self.assertEqual(rng.calls, [20])

        rng = SequenceRng([1])
        self.assertFalse(rogue_chase.confusion_clears_after_random_move(1, rng.rnd))
        self.assertEqual(rng.calls, [20])

        rng = SequenceRng([])
        self.assertFalse(rogue_chase.confusion_clears_after_random_move(0, rng.rnd))
        self.assertEqual(rng.calls, [])

    def test_rogue_544_chase_helper_choose_chase_step_matches_tie_roll(self):
        # Rogue 5.4.4 chase.c:chase() replaces equal-distance candidates only when rnd(++plcnt)==0.
        import rogue_chase

        self.assertEqual(
            rogue_chase.choose_chase_step((1, 1), 10, 1, (2, 2), 5, lambda n: 0),
            ((2, 2), 5, 1),
        )

        rng = SequenceRng([1])
        self.assertEqual(
            rogue_chase.choose_chase_step((1, 1), 5, 1, (2, 2), 5, rng.rnd),
            ((1, 1), 5, 2),
        )
        self.assertEqual(rng.calls, [2])

        rng = SequenceRng([0])
        self.assertEqual(
            rogue_chase.choose_chase_step((1, 1), 5, 1, (2, 2), 5, rng.rnd),
            ((2, 2), 5, 2),
        )

    def test_rogue_544_chase_helper_candidate_gate_blocks_diag_step_scare_and_xeroc(self):
        # Rogue 5.4.4 chase.c:chase() skips bad diagonals, non-step cells, scare scrolls, and Xerocs.
        import rogue_chase

        self.assertTrue(rogue_chase.is_chase_candidate(True, True, False, False))
        self.assertFalse(rogue_chase.is_chase_candidate(False, True, False, False))
        self.assertFalse(rogue_chase.is_chase_candidate(True, False, False, False))
        self.assertFalse(rogue_chase.is_chase_candidate(True, True, True, False))
        self.assertFalse(rogue_chase.is_chase_candidate(True, True, False, True))

    def test_rogue_544_chase_helper_continues_unless_at_goal_or_hero(self):
        # Rogue 5.4.4 chase.c:chase() returns curdist != 0 && !ce(ch_ret, hero).
        import rogue_chase

        self.assertTrue(rogue_chase.chase_continues(5, (4, 4), (1, 1)))
        self.assertFalse(rogue_chase.chase_continues(0, (4, 4), (1, 1)))
        self.assertFalse(rogue_chase.chase_continues(5, (1, 1), (1, 1)))

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

    def test_keyboard_pad_style_enter_esc_tab_shortcuts(self):
        game = new_game(seed=46)
        set_open_floor(game)
        searched = []
        waited = []
        game.do_search = lambda front_only=False: searched.append(front_only)
        game.do_wait = lambda: waited.append(True)

        rogue.pyxel.set_input(
            held={rogue.pyxel.KEY_RETURN, rogue.pyxel.KEY_ESCAPE},
            pressed={rogue.pyxel.KEY_RETURN},
        )
        game.update()
        self.assertEqual(waited, [True])

        rogue.pyxel.set_input(
            held={rogue.pyxel.KEY_TAB, rogue.pyxel.KEY_RETURN},
            pressed={rogue.pyxel.KEY_RETURN},
        )
        game.update()
        self.assertEqual(searched, [False])
        self.assertEqual(game.st, rogue.ST_PLAY)

        rogue.pyxel.set_input(
            held={rogue.pyxel.KEY_TAB, rogue.pyxel.KEY_ESCAPE},
            pressed={rogue.pyxel.KEY_ESCAPE},
        )
        game.update()
        self.assertEqual(game.st, rogue.ST_DIR)
        self.assertEqual(game.cact, "Throw")
        self.assertEqual(game.dact, "Throw")

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

    def test_rogue_544_throw_direction_prompt_accepts_hjkl(self):
        # Rogue 5.4.4 misc.c:get_dir() accepts h/j/k/l as cardinal directions.
        game = new_game(seed=481)
        set_open_floor(game)
        game.start_item_action("Throw")

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_H}, pressed={rogue.pyxel.KEY_H})
        game.update()

        self.assertEqual(game.st, rogue.ST_ITEM)
        self.assertEqual(game.throw_dir, (-1, 0))

    def test_rogue_544_throw_direction_prompt_accepts_vi_diagonals(self):
        # Rogue 5.4.4 misc.c:get_dir() accepts y/u/b/n for diagonal missile directions.
        game = new_game(seed=482)
        set_open_floor(game)
        game.start_item_action("Throw")

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_U}, pressed={rogue.pyxel.KEY_U})
        game.update()

        self.assertEqual(game.st, rogue.ST_ITEM)
        self.assertEqual(game.throw_dir, (1, -1))

    def test_rogue_544_throw_motion_travels_diagonally(self):
        # Rogue 5.4.4 weapons.c:missile()/do_motion() advances by both deltas.
        game = new_game(seed=483)
        game.mons = []
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        game.p.x, game.p.y = 2, 5
        for i in range(5):
            game.tm[5 - i][2 + i] = rogue.T_FLOOR
        game.gitems = []
        item = rogue.Item(rogue.CAT_WPN, 4)
        game.p.inv = [item]

        game.throw(item, 1, -1)

        self.assertIsNotNone(game.throw_anim)
        self.assertEqual(game.throw_anim["path"], [(3, 4), (4, 3), (5, 2), (6, 1)])

    def test_rogue_544_thrown_item_falls_around_door_it_hits(self):
        # Rogue 5.4.4 weapons.c:do_motion() stops on DOOR, then fall(TRUE) uses fallpos() around that hit cell.
        game = new_game(seed=484)
        game.mons = []
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        game.p.x, game.p.y = 2, 2
        game.tm[2][2] = rogue.T_FLOOR
        game.tm[2][3] = rogue.T_FLOOR
        game.tm[2][4] = rogue.T_DOOR
        game.tm[3][4] = rogue.T_FLOOR
        game.gitems = []
        item = rogue.Item(rogue.CAT_WPN, 4)
        game.p.inv = [item]
        fall_calls = []
        game.fall_position = lambda x, y: fall_calls.append((x, y)) or (4, 3)

        game.throw(item, 1, 0)
        for _ in range(len(game.throw_anim["path"]) * game.throw_anim["delay"]):
            rogue.pyxel.set_input()
            game.update()

        self.assertEqual(fall_calls, [(4, 2)])
        self.assertEqual((game.gitems[-1].x, game.gitems[-1].y), (4, 3))

    def test_rogue_544_weapons_helper_fallpos_candidate_matches_source_tiles(self):
        # Rogue 5.4.4 weapons.c:fallpos() skips hero and accepts only FLOOR/PASSAGE.
        import rogue_weapons

        self.assertTrue(rogue_weapons.is_fallpos_candidate((4, 4), (5, 5), "FLOOR"))
        self.assertTrue(rogue_weapons.is_fallpos_candidate((4, 4), (5, 5), "PASSAGE"))
        self.assertFalse(rogue_weapons.is_fallpos_candidate((5, 5), (5, 5), "FLOOR"))
        self.assertFalse(rogue_weapons.is_fallpos_candidate((4, 4), (5, 5), "DOOR"))

    def test_rogue_544_weapons_helper_choose_fallpos_matches_rnd_count(self):
        # Rogue 5.4.4 weapons.c:fallpos() replaces newpos when rnd(++cnt)==0.
        import rogue_weapons

        rng = SequenceRng([0])
        self.assertEqual(rogue_weapons.choose_fallpos(None, 0, (4, 4), rng.rnd), ((4, 4), 1))
        self.assertEqual(rng.calls, [1])

        rng = SequenceRng([1])
        self.assertEqual(rogue_weapons.choose_fallpos((4, 4), 1, (5, 5), rng.rnd), ((4, 4), 2))
        self.assertEqual(rng.calls, [2])

        rng = SequenceRng([0])
        self.assertEqual(rogue_weapons.choose_fallpos((4, 4), 1, (5, 5), rng.rnd), ((5, 5), 2))

    def test_rogue_544_fall_position_uses_rng_rnd_for_choice(self):
        # Rogue 5.4.4 weapons.c:fallpos() uses rnd(++cnt), not randrange().
        game = new_game(seed=498)
        set_open_floor(game)
        old_rnd = rogue.RNG.rnd
        old_randrange = rogue.RNG.randrange
        try:
            rogue.RNG.rnd = lambda n: 0
            rogue.RNG.randrange = lambda n: (_ for _ in ()).throw(AssertionError("randrange used"))
            pos = game.fall_position(game.p.x + 2, game.p.y)
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.RNG.randrange = old_randrange

        self.assertIsNotNone(pos)

    def test_rogue_544_weapons_helper_fall_result_matches_source_branches(self):
        # Rogue 5.4.4 weapons.c:fall() attaches on fallpos success, otherwise only pr prints vanish.
        import rogue_weapons

        self.assertEqual(rogue_weapons.fall_result((4, 4), pr=True), ("drop", (4, 4)))
        self.assertEqual(rogue_weapons.fall_result(None, pr=True), ("vanish", None))
        self.assertEqual(rogue_weapons.fall_result(None, pr=False), ("discard", None))

    def test_rogue_544_weapons_helper_initial_weapon_count_matches_source(self):
        # Rogue 5.4.4 weapons.c:init_weapon() gives daggers rnd(4)+2, ISMANY weapons rnd(8)+8, others 1.
        import rogue_weapons

        self.assertEqual(rogue_weapons.initial_weapon_count("dagger", False, lambda n: 3), 5)
        self.assertEqual(rogue_weapons.initial_weapon_count("arrow", True, lambda n: 7), 15)
        self.assertEqual(rogue_weapons.initial_weapon_count("mace", False, lambda n: 99), 1)

    def test_rogue_544_weapons_helper_new_thing_weapon_enchant_matches_source(self):
        # Rogue 5.4.4 things.c:new_thing() curses weapons on rnd(100)<10, enchants on r<15.
        import rogue_weapons

        self.assertEqual(rogue_weapons.new_thing_weapon_enchant(9, lambda n: 2), (-3, True))
        self.assertEqual(rogue_weapons.new_thing_weapon_enchant(14, lambda n: 1), (2, False))
        self.assertEqual(rogue_weapons.new_thing_weapon_enchant(15, lambda n: 99), (0, False))

    def test_rogue_544_armor_helper_new_thing_armor_enchant_matches_source(self):
        # Rogue 5.4.4 things.c:new_thing() curses armor on rnd(100)<20, enchants on r<28.
        import rogue_armor

        self.assertEqual(rogue_armor.new_thing_armor_enchant(19, lambda n: 2), (-3, True))
        self.assertEqual(rogue_armor.new_thing_armor_enchant(27, lambda n: 1), (2, False))
        self.assertEqual(rogue_armor.new_thing_armor_enchant(28, lambda n: 99), (0, False))

    def test_rogue_544_things_helper_food_kind_matches_new_thing_ratio(self):
        # Rogue 5.4.4 things.c:new_thing() makes ration unless rnd(10)==0.
        import rogue_things

        self.assertEqual(rogue_things.new_thing_food_kind(lambda n: 1), 0)
        self.assertEqual(rogue_things.new_thing_food_kind(lambda n: 0), 1)

    def test_rogue_544_things_helper_category_weights_match_source_table(self):
        # Rogue 5.4.4 extern.c:things[] uses 26/36/16/7/7/4/4 weights.
        import rogue_things

        self.assertEqual(rogue_things.new_thing_category(0), "potion")
        self.assertEqual(rogue_things.new_thing_category(25), "potion")
        self.assertEqual(rogue_things.new_thing_category(26), "scroll")
        self.assertEqual(rogue_things.new_thing_category(77), "food")
        self.assertEqual(rogue_things.new_thing_category(78), "weapon")
        self.assertEqual(rogue_things.new_thing_category(85), "armor")
        self.assertEqual(rogue_things.new_thing_category(92), "ring")
        self.assertEqual(rogue_things.new_thing_category(96), "stick")
        self.assertEqual(rogue_things.new_thing_category(0, no_food=4), "food")

    def test_rogue_544_things_helper_pick_one_uses_subtractive_prob_table(self):
        # Rogue 5.4.4 things.c:pick_one() subtracts oi_prob from rnd(100).
        import rogue_things

        table = [("potion", 26), ("scroll", 36), ("food", 16), ("weapon", 7),
                 ("armor", 7), ("ring", 4), ("stick", 4)]
        self.assertEqual(rogue_things.pick_one(table, 0), 0)
        self.assertEqual(rogue_things.pick_one(table, 25), 0)
        self.assertEqual(rogue_things.pick_one(table, 26), 1)
        self.assertEqual(rogue_things.pick_one(table, 61), 1)
        self.assertEqual(rogue_things.pick_one(table, 62), 2)
        self.assertEqual(rogue_things.pick_one(table, 99), 6)
        self.assertEqual(rogue_things.pick_one([("only", 1)], 99), 0)

    def test_rogue_544_things_helper_category_roll_forces_food_after_four_levels(self):
        # Rogue 5.4.4 things.c:new_thing() bypasses pick_one() when no_food > 3.
        import rogue_things

        calls = []

        def rnd(n):
            calls.append(n)
            return 96

        self.assertEqual(rogue_things.new_thing_category_roll(rnd, no_food=4), "food")
        self.assertEqual(calls, [])
        self.assertEqual(rogue_things.new_thing_category_roll(rnd, no_food=0), "stick")
        self.assertEqual(calls, [100])

    def test_rogue_544_things_helper_no_food_counter_matches_new_level_and_new_thing(self):
        # Rogue 5.4.4 new_level.c:new_level() increments no_food; things.c:new_thing() resets it on FOOD.
        import rogue_things

        self.assertEqual(rogue_things.no_food_after_new_level(3), 4)
        self.assertEqual(rogue_things.no_food_after_new_thing("food", 4), 0)
        self.assertEqual(rogue_things.no_food_after_new_thing("scroll", 4), 4)

    def test_rogue_544_game_no_food_counter_forces_food_generation(self):
        # Rogue 5.4.4 things.c:new_thing() forces FOOD when no_food > 3 and then clears no_food.
        game = new_game(seed=3302)
        game.no_food = 4
        old_randrange = rogue.random.randrange
        try:
            rogue.random.randrange = lambda n: 96 if n == 100 else 1
            item = game.make_game_item(game.p.depth)
        finally:
            rogue.random.randrange = old_randrange

        self.assertEqual(item.cat, rogue.CAT_FOOD)
        self.assertEqual(game.no_food, 0)

    def test_rogue_544_pack_helper_scare_scroll_found_flag_and_dust(self):
        # Rogue 5.4.4 pack.c:add_pack() sets ISFOUND, then dusts S_SCARE on pickup.
        import rogue_pack

        self.assertEqual(rogue_pack.scare_scroll_pickup_result(False), "mark_found")
        self.assertEqual(rogue_pack.scare_scroll_pickup_result(True), "dust")

    def test_rogue_544_pack_helper_checks_room_before_stacking_floor_item(self):
        # Rogue 5.4.4 pack.c:add_pack() calls pack_room() before stacking ISMULT items.
        import rogue_pack

        self.assertTrue(rogue_pack.pack_room_allows(25, 26))
        self.assertFalse(rogue_pack.pack_room_allows(26, 26))

    def test_rogue_544_monsters_helper_give_pack_gate_matches_source(self):
        # Rogue 5.4.4 monsters.c:give_pack() uses level >= max_level && rnd(100) < m_carry.
        import rogue_monsters

        self.assertTrue(rogue_monsters.should_give_pack(10, 10, 20, lambda n: 19))
        self.assertFalse(rogue_monsters.should_give_pack(9, 10, 20, lambda n: 0))
        self.assertFalse(rogue_monsters.should_give_pack(10, 10, 20, lambda n: 20))

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

    def test_keyboard_rogue_commands_start_existing_actions_only_in_play(self):
        cases = [
            (rogue.pyxel.KEY_T, set(), "Throw"),
            (rogue.pyxel.KEY_Q, set(), "Quaff"),
            (rogue.pyxel.KEY_R, set(), "Read"),
            (rogue.pyxel.KEY_E, set(), "Eat"),
            (rogue.pyxel.KEY_W, set(), "Wear"),
            (rogue.pyxel.KEY_Z, set(), "Zap"),
            (rogue.pyxel.KEY_W, {rogue.pyxel.KEY_SHIFT}, "Wield"),
            (rogue.pyxel.KEY_T, {rogue.pyxel.KEY_SHIFT}, "Take off"),
        ]
        for key, modifiers, action in cases:
            game = new_game(seed=55)
            calls = []
            game.start_item_action = lambda aname, cat=None, calls=calls: calls.append(aname)

            held = set(modifiers) | {key}
            rogue.pyxel.set_input(held=held, pressed={key})
            game.update()

            self.assertEqual(calls, [action])

        game = new_game(seed=55)
        game.st = rogue.ST_MENU
        calls = []
        game.start_item_action = lambda aname, cat=None: calls.append(aname)

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_Q}, pressed={rogue.pyxel.KEY_Q})
        game.update()

        self.assertEqual(calls, [])

    def test_help_text_separates_gamepad_pad_style_and_rogue_commands(self):
        game = new_game(seed=56)
        calls = []
        game.txt = lambda x, y, s, c: calls.append(str(s))

        game.draw_help()

        text = "\n".join(calls)
        self.assertIn("--- Gamepad ---", text)
        self.assertIn("--- Keyboard: Pad ---", text)
        self.assertIn("--- Keyboard commands ---", text)
        self.assertIn("Enter+Esc", text)
        self.assertIn("q Quaff", text)
        self.assertNotIn("Z / Enter", text)
        self.assertNotIn("Close overlays", text)

    def test_help_text_uses_high_contrast_colors(self):
        game = new_game(seed=561)
        calls = []
        game.txt = lambda x, y, s, c: calls.append((str(s), c))

        game.draw_help()

        headers = [c for s, c in calls if s.startswith("---")]
        body = [c for s, c in calls if s and not s.startswith(("===", "---"))]
        self.assertTrue(headers)
        self.assertTrue(body)
        self.assertEqual(set(headers), {rogue.HELP_HEADER_COL})
        self.assertEqual(set(body), {rogue.HELP_TEXT_COL})

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

    def test_rogue544_new_level_trap_count_and_kind_helpers_match_source(self):
        # Rogue 5.4.4 new_level.c:new_level() uses rnd(10)<level, rnd(level/4)+1, MAXTRAPS, NTRAPS.
        import rogue_dungeon

        self.assertEqual(rogue_dungeon.trap_count_for_level(1, SequenceRng([1])), 0)
        self.assertEqual(rogue_dungeon.trap_count_for_level(1, SequenceRng([0, 0])), 1)
        self.assertEqual(rogue_dungeon.trap_count_for_level(40, SequenceRng([0, 99])), 10)
        self.assertEqual(rogue_dungeon.trap_kind(SequenceRng([7])), 7)

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

    def test_rogue544_passage_helper_secret_feature_gate_matches_source(self):
        # Rogue 5.4.4 passages.c:door()/putpass() use rnd(10)+1<level and rnd(denom)==0.
        import rogue_search

        self.assertFalse(rogue_search.secret_feature_hidden(1, SequenceRng([0, 0]), 5))
        self.assertTrue(rogue_search.secret_feature_hidden(2, SequenceRng([0, 0]), 5))
        self.assertFalse(rogue_search.secret_feature_hidden(2, SequenceRng([0, 1]), 5))

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

    def test_rogue_544_sleeping_gas_trap_adds_sleep_time(self):
        # Rogue 5.4.4 move.c:be_trapped() T_SLEEP uses no_command += SLEEPTIME.
        game = new_game(seed=61)
        set_open_floor(game)
        x, y = game.p.x + 1, game.p.y
        kind = next(i for i, t in enumerate(rogue.TRAPS) if t["name"] == "sleeping gas trap")
        game.traps[(x, y)] = kind
        game.p.no_command = 7
        game.dashing = True

        game.trigger_trap(x, y)

        self.assertEqual(game.p.no_command, 7 + rogue.SLEEPTIME)
        self.assertFalse(game.dashing)

    def test_rogue_544_bear_trap_adds_bear_time(self):
        # Rogue 5.4.4 move.c:be_trapped() T_BEAR uses no_move += BEARTIME.
        game = new_game(seed=62)
        set_open_floor(game)
        x, y = game.p.x + 1, game.p.y
        kind = next(i for i, t in enumerate(rogue.TRAPS) if t["name"] == "bear trap")
        game.traps[(x, y)] = kind
        game.p.no_move = 4

        game.trigger_trap(x, y)

        self.assertEqual(game.p.no_move, 4 + rogue.BEARTIME)

    def test_rogue_544_move_helper_simple_trap_state_additions_match_source(self):
        # Rogue 5.4.4 move.c:be_trapped() T_BEAR/T_SLEEP add fixed constants.
        import rogue_move

        self.assertEqual(rogue_move.bear_trap_no_move(4, rogue.BEARTIME), 4 + rogue.BEARTIME)
        self.assertEqual(rogue_move.sleep_trap_no_command(7, rogue.SLEEPTIME), 7 + rogue.SLEEPTIME)

    def test_rogue_544_arrow_trap_miss_drops_one_arrow_with_fallpos(self):
        # Rogue 5.4.4 move.c:T_ARROW uses weapons.c:fall()/fallpos() on a miss.
        game = new_game(seed=63)
        set_open_floor(game)
        x, y = game.p.x + 1, game.p.y
        kind = next(i for i, t in enumerate(rogue.TRAPS) if t["name"] == "arrow trap")
        game.traps[(x, y)] = kind
        game.gitems = []
        game.trap_hits = lambda bonus=0: False

        game.trigger_trap(x, y)

        self.assertEqual(len(game.gitems), 1)
        arrow = game.gitems[0]
        self.assertEqual((arrow.cat, arrow.kind, arrow.qty), (rogue.CAT_WPN, 3, 1))
        self.assertNotEqual((arrow.x, arrow.y), (game.p.x, game.p.y))
        self.assertLessEqual(abs(arrow.x - game.p.x), 1)
        self.assertLessEqual(abs(arrow.y - game.p.y), 1)

    def test_rogue_544_arrow_trap_miss_uses_fallpos_when_player_tile_has_item(self):
        # Rogue 5.4.4 move.c:T_ARROW uses weapons.c:fall()/fallpos() on a miss.
        game = new_game(seed=70)
        set_open_floor(game)
        x, y = game.p.x + 1, game.p.y
        kind = next(i for i, t in enumerate(rogue.TRAPS) if t["name"] == "arrow trap")
        game.traps[(x, y)] = kind
        game.trap_hits = lambda bonus=0: False
        food = rogue.Item(rogue.CAT_FOOD, 0)
        food.x, food.y = game.p.x, game.p.y
        game.gitems = [food]

        game.trigger_trap(x, y)

        arrows = [it for it in game.gitems if it.cat == rogue.CAT_WPN and it.kind == 3]
        self.assertEqual(len(arrows), 1)
        arrow = arrows[0]
        self.assertNotEqual((arrow.x, arrow.y), (game.p.x, game.p.y))
        self.assertLessEqual(abs(arrow.x - game.p.x), 1)
        self.assertLessEqual(abs(arrow.y - game.p.y), 1)

    def test_rogue_544_trap_hits_ignore_worn_armor(self):
        # Rogue 5.4.4 move.c:be_trapped() calls swing(..., pstats.s_arm, 1),
        # not cur_armor->o_arm; extern.c:INIT_STATS sets pstats.s_arm to 10.
        game = new_game(seed=71)
        game.p.level = 1
        game.p.arm = rogue.Item(rogue.CAT_ARM, 7, ench=20)
        game.p.recalc_ac()
        old_randrange = rogue.RNG.randrange
        try:
            rogue.RNG.randrange = lambda n: 8
            self.assertFalse(game.trap_hits(game.p.level - 1))
            rogue.RNG.randrange = lambda n: 9
            self.assertTrue(game.trap_hits(game.p.level - 1))
        finally:
            rogue.RNG.randrange = old_randrange

    def test_rogue_544_arrow_trap_kill_uses_killed_message(self):
        # Rogue 5.4.4 move.c:be_trapped() T_ARROW says "an arrow killed you" on death.
        game = new_game(seed=64)
        set_open_floor(game)
        x, y = game.p.x + 1, game.p.y
        kind = next(i for i, t in enumerate(rogue.TRAPS) if t["name"] == "arrow trap")
        game.traps[(x, y)] = kind
        game.trap_hits = lambda bonus=0: True
        game.p.hp = 1
        old_roll = rogue.roll
        rogue.roll = lambda s: 1
        try:
            game.trigger_trap(x, y)
        finally:
            rogue.roll = old_roll

        self.assertEqual(game.death_cause, "an arrow killed you")
        self.assertIn("an arrow killed you", game.msgs)
        self.assertNotIn("oh no! An arrow shot you", game.msgs)

    def test_rogue_544_dart_trap_kill_uses_poisoned_dart_message(self):
        # Rogue 5.4.4 move.c:be_trapped() T_DART says "a poisoned dart killed you" on death.
        game = new_game(seed=65)
        set_open_floor(game)
        x, y = game.p.x + 1, game.p.y
        kind = next(i for i, t in enumerate(rogue.TRAPS) if t["name"] == "dart trap")
        game.traps[(x, y)] = kind
        game.trap_hits = lambda bonus=0: True
        game.p.hp = 1
        old_roll = rogue.roll
        rogue.roll = lambda s: 1
        try:
            game.trigger_trap(x, y)
        finally:
            rogue.roll = old_roll

        self.assertEqual(game.death_cause, "a poisoned dart killed you")
        self.assertIn("a poisoned dart killed you", game.msgs)
        self.assertNotIn("a small dart just hit you in the shoulder", game.msgs)

    def test_rogue_544_dart_trap_kill_does_not_lower_strength_after_death(self):
        # Rogue 5.4.4 move.c:be_trapped() T_DART calls death('d') before poison strength loss.
        game = new_game(seed=66)
        set_open_floor(game)
        x, y = game.p.x + 1, game.p.y
        kind = next(i for i, t in enumerate(rogue.TRAPS) if t["name"] == "dart trap")
        game.traps[(x, y)] = kind
        game.trap_hits = lambda bonus=0: True
        game.save_vs_poison = lambda: False
        game.p.hp = 1
        game.p.st = 16
        old_roll = rogue.roll
        rogue.roll = lambda s: 1
        try:
            game.trigger_trap(x, y)
        finally:
            rogue.roll = old_roll

        self.assertEqual(game.p.st, 16)

    def test_rogue_544_dart_trap_poison_save_runs_before_min_strength_check(self):
        # Rogue 5.4.4 move.c:T_DART calls save(VS_POISON) before chg_str(-1);
        # the save is still consumed when Strength is already at the floor.
        game = new_game(seed=67)
        set_open_floor(game)
        x, y = game.p.x + 1, game.p.y
        kind = next(i for i, t in enumerate(rogue.TRAPS) if t["name"] == "dart trap")
        game.traps[(x, y)] = kind
        game.trap_hits = lambda bonus=0: True
        game.p.hp = 10
        game.p.st = 3
        calls = []
        game.save_vs_poison = lambda: calls.append(True) or False
        old_roll = rogue.roll
        rogue.roll = lambda s: 1
        try:
            game.trigger_trap(x, y)
        finally:
            rogue.roll = old_roll

        self.assertEqual(calls, [True])
        self.assertEqual(game.p.st, 3)

    def test_rogue_544_move_helper_dart_poison_strength_matches_source(self):
        # Rogue 5.4.4 move.c:T_DART lowers strength only without sustain strength and failed poison save.
        import rogue_move

        self.assertEqual(rogue_move.dart_poison_strength(10, False, False), 9)
        self.assertEqual(rogue_move.dart_poison_strength(10, True, False), 10)
        self.assertEqual(rogue_move.dart_poison_strength(10, False, True), 10)
        self.assertEqual(rogue_move.dart_poison_strength(3, False, False), 3)

    def test_rogue_544_mysterious_trap_only_rolls_color_for_color_messages(self):
        # Rogue 5.4.4 move.c:be_trapped() T_MYST rolls rnd(cNCOLORS) only in color message branches.
        game = new_game(seed=67)
        calls = []
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: calls.append(n) or 0
            game.mysterious_trap_msg()
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(calls, [11])
        self.assertIn("you are suddenly in a parallel dimension", game.msgs)

    def test_rogue_544_mysterious_trap_pack_turns_message_matches_source(self):
        # Rogue 5.4.4 move.c:T_MYST case 10 says "you pack turns %s!".
        game = new_game(seed=68)
        seq = iter([10, 0])
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: next(seq)
            game.mysterious_trap_msg()
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertIn("you pack turns red!", game.msgs)
        self.assertNotIn("your pack turns red!", game.msgs)

    def test_rogue_544_mysterious_trap_armor_sparks_uses_source_message_key(self):
        # Rogue 5.4.4 move.c:T_MYST case 6 says "%s sparks dance across your armor".
        game = new_game(seed=69, lang=rogue.LANG_JA)
        seq = iter([6, 0])
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: next(seq)
            game.mysterious_trap_msg()
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertIn("red火花がよろいの上で踊った。", game.msgs)
        self.assertNotIn("redの火花がよろいの上で踊った。", game.msgs)

    def test_poison_save_uses_rogue54_level_scaled_threshold(self):
        game = new_game(seed=60)
        game.p.level = 4
        old_roll = rogue.RNG.roll
        try:
            rogue.RNG.roll = lambda n, sides: 12
            self.assertTrue(game.save_vs_poison())
            rogue.RNG.roll = lambda n, sides: 11
            self.assertFalse(game.save_vs_poison())
        finally:
            rogue.RNG.roll = old_roll


class TestCallIt(unittest.TestCase):
    def setUp(self):
        self.g = new_game(seed=1)

    def _make_pot(self, kind=0):
        from rogue import Item, CAT_POT
        return Item(CAT_POT, kind, known=False)

    def test_call_sets_guess_on_unknown_potion(self):
        """oi_know=False のポーションに仮名が設定される"""
        it = self._make_pot(kind=0)
        self.g.ident.pk[0] = False
        self.g._call_it_apply(it, "boo")
        self.assertEqual(self.g.ident.pg[0], "boo")

    def test_call_clears_guess_when_known(self):
        """oi_know=True なら既存 oi_guess をクリアする"""
        it = self._make_pot(kind=0)
        self.g.ident.pk[0] = True
        self.g.ident.pg[0] = "old_name"
        self.g._call_it_apply(it, "new_name")
        self.assertIsNone(self.g.ident.pg[0])

    def test_call_empty_string_clears_guess(self):
        """空文字確定で oi_guess がクリアされる"""
        it = self._make_pot(kind=0)
        self.g.ident.pk[0] = False
        self.g.ident.pg[0] = "old"
        self.g._call_it_apply(it, "")
        self.assertIsNone(self.g.ident.pg[0])

    def test_rogue_544_call_sets_weapon_and_armor_o_label(self):
        # Rogue 5.4.4 command.c:call() stores weapon/armor names in o_label;
        # things.c:inv_name() appends "called NAME".
        weapon = rogue.Item(rogue.CAT_WPN, 0, known=False)
        armor = rogue.Item(rogue.CAT_ARM, 1, known=False)

        self.g._call_it_apply(weapon, "sting")
        self.g._call_it_apply(armor, "lucky")

        self.assertEqual(weapon.o_label, "sting")
        self.assertEqual(armor.o_label, "lucky")
        self.assertEqual(self.g.item_name(weapon), "mace called sting")
        self.assertEqual(self.g.item_name(armor), "ring mail called lucky")


class TestPrintDisc(unittest.TestCase):
    def setUp(self):
        self.g = new_game(seed=1)

    def test_disc_lines_has_nothing_when_empty(self):
        """何も識別していなければ nothing_discovered テキストが含まれる"""
        lines = self.g._disc_lines()
        texts = [t for _, t in lines]
        self.assertTrue(any("nothing" in t.lower() or "未発見" in t for t in texts))

    def test_disc_lines_shows_known_potion(self):
        """oi_know=True のポーションが一覧に現れる"""
        self.g.ident.pk[0] = True
        lines = self.g._disc_lines()
        # セクション見出し・空行・nothing 以外の行がある
        non_header = [t for col, t in lines if t and not t.startswith("--") and not t.startswith("(") and not t.startswith("（")]
        self.assertTrue(len(non_header) > 0)

    def test_disc_lines_shows_guess_potion(self):
        """oi_guess のあるポーションが一覧に現れる"""
        self.g.ident.pg[0] = "boo"
        lines = self.g._disc_lines()
        texts = [t for _, t in lines]
        self.assertTrue(any("boo" in t for t in texts))


if __name__ == "__main__":
    unittest.main()
