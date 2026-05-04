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
    pyxel.rect_calls = []
    pyxel.rect = lambda *a, **kw: pyxel.rect_calls.append((a, kw))
    pyxel.rectb_calls = []
    pyxel.rectb = lambda *a, **kw: pyxel.rectb_calls.append((a, kw))
    pyxel.blt_calls = []
    pyxel.blt = lambda *a, **kw: pyxel.blt_calls.append((a, kw))
    pyxel.dither_calls = []
    pyxel.dither = lambda alpha=1.0: pyxel.dither_calls.append(alpha)
    pyxel.play_calls = []
    pyxel.stop_calls = []
    pyxel.play = lambda *a, **kw: pyxel.play_calls.append((a, kw))
    pyxel.stop = lambda *a, **kw: pyxel.stop_calls.append((a, kw))
    pyxel.__file__ = os.path.join(os.getcwd(), "pyxel", "__init__.py")
    for i, key in enumerate([
        "KEY_NONE", "KEY_UP", "KEY_DOWN", "KEY_LEFT", "KEY_RIGHT",
        "KEY_H", "KEY_J", "KEY_K", "KEY_L",
        "KEY_Y", "KEY_U", "KEY_B", "KEY_N",
        "KEY_Z", "KEY_X", "KEY_C", "KEY_S",
        "KEY_Q", "KEY_W", "KEY_E", "KEY_T", "KEY_P",
        "KEY_A", "KEY_D", "KEY_F", "KEY_G", "KEY_M",
        "KEY_O", "KEY_V",
        "KEY_I", "KEY_6", "KEY_SPACE",
        "KEY_ESCAPE", "KEY_RETURN", "KEY_TAB", "KEY_BACKSPACE",
        "KEY_PERIOD", "KEY_COMMA", "KEY_MINUS",
        "KEY_0", "KEY_EQUALS", "KEY_RIGHTBRACKET", "KEY_AT",
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

    class MockSound:
        def __init__(self):
            self.mml_calls = []

        def mml(self, code=None):
            self.mml_calls.append(code)

    pyxel.sounds = [MockSound() for _ in range(64)]

    class MockImage:
        def __init__(self, w, h):
            self.w = w
            self.h = h
            self.load_calls = []

        def load(self, *a):
            self.load_calls.append(a)

    pyxel.Image = MockImage
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


def set_two_room_floor(game):
    game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
    room_a = rogue.Room(1, 1, 10, 8)
    room_b = rogue.Room(20, 1, 10, 8)
    game.rooms = [room_a, room_b]
    for room in game.rooms:
        for y in range(room.y, room.y + room.h):
            for x in range(room.x, room.x + room.w):
                game.tm[y][x] = rogue.T_FLOOR
    game.p.x, game.p.y = 3, 4
    game.visible = set()
    return room_a, room_b


def monster_at(x, y, sym="H", name="hobgoblin", hp=10, level=1, armor=5,
               damage="1x8", exp=3, flags=""):
    return rogue.Monster(x, y, sym, name, hp, level, armor, damage, exp, flags)


def state_signature(game):
    return (
        game.turn,
        game.p.x,
        game.p.y,
        game.p.hp,
        game.p.max_hp,
        game.p.food,
        game.p.exp,
        game.p.level,
        tuple((it.cat, it.kind, it.qty, it.known) for it in game.p.inv),
        tuple((it.cat, it.kind, it.qty, it.x, it.y) for it in game.gitems),
        tuple((m.sym, m.x, m.y, m.hp, tuple(sorted(m.flags))) for m in game.mons),
        tuple(game.ident.pk),
        tuple(game.ident.sk),
    )


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
        self.assertEqual((rogue.ST_LOGO, rogue.ST_TITLE, rogue.ST_NAME, rogue.ST_READY, rogue.ST_ONLINE_SCORE), (15, 16, 17, 18, 19))
        self.assertEqual(rogue.ST_ONLINE_CONFIRM, 22)
        self.assertEqual(rogue.ST_ONLINE_LOCAL_CONFIRM, 23)
        self.assertEqual(rogue.CALL_PRESETS, rogue_ui.CALL_PRESETS)
        self.assertEqual(rogue.MENU_ACTIONS, rogue_ui.MENU_ACTIONS)
        self.assertEqual(rogue.AUX_ACTIONS, rogue_ui.AUX_ACTIONS)
        self.assertEqual(
            rogue.PAD_ACTION_GRID,
            (
                ("Zap", "Throw", "Put on"),
                ("Quaff", "Eat", "Read"),
                ("Wield", "Wear", "Take off"),
                ("Call", "Discoveries", "Drop"),
            ),
        )
        self.assertEqual(
            rogue_ui.pad_menu_initial_index(rogue.MENU_ACTIONS),
            next(i for i, (name, _cat) in enumerate(rogue.MENU_ACTIONS) if name == "Eat"),
        )
        self.assertEqual(
            rogue_ui.pad_menu_move(rogue_ui.pad_menu_initial_index(rogue.MENU_ACTIONS), -1, 0, rogue.MENU_ACTIONS),
            next(i for i, (name, _cat) in enumerate(rogue.MENU_ACTIONS) if name == "Quaff"),
        )
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

    def test_rogue544_new_level_places_traps_stairs_then_hero_after_objects(self):
        # Rogue 5.4.4 new_level.c:new_level() runs do_rooms(), do_passages(), put_things(), traps, stairs, then hero.
        game = new_game(seed=35)
        order = []
        positions = [(5, 5), (6, 5)]

        game._populate_initial_room = lambda room: order.append(f"room:{len(order)}")
        game._spawn_items = lambda: order.append("put_things")
        game._spawn_amulet = lambda: order.append("amulet")
        game._hide_secret_features = lambda: None
        game._spawn_traps = lambda: order.append("traps")

        def fake_find_floor_pos(room=None, limit=0, monst=False, **kwargs):
            order.append("hero" if monst else "stairs")
            return positions.pop(0)

        game.find_floor_pos = fake_find_floor_pos
        game.descend()

        self.assertTrue(order[0].startswith("room:"))
        self.assertEqual(order[order.index("put_things"):], ["put_things", "amulet", "traps", "stairs", "hero"])
        self.assertTrue(all(entry.startswith("room:") for entry in order[:order.index("put_things")]))
        self.assertEqual((game.p.x, game.p.y), (6, 5))
        self.assertEqual(game.tm[5][5], rogue.T_STAIR)

    def test_rogue544_dgen_room_callback_runs_before_do_passages(self):
        # Rogue 5.4.4 rooms.c:do_rooms() populates each real room before passages.c:do_passages().
        events = []
        old_edges = rogue.DGen._passage_edges
        try:
            rogue.DGen._passage_edges = staticmethod(lambda *a, **kw: events.append("passages") or [])

            rogue.DGen.gen(depth=1, room_callback=lambda _tm, _rooms, room: events.append("room"))
        finally:
            rogue.DGen._passage_edges = old_edges

        self.assertTrue(events)
        self.assertEqual(events[-1], "passages")
        self.assertNotIn("room", events[events.index("passages"):])

    def test_rogue544_new_level_increments_no_food_after_do_passages_before_put_things(self):
        # Rogue 5.4.4 new_level.c:new_level() calls no_food++ after do_passages(), before put_things().
        game = new_game(seed=3051)
        events = []
        game.no_food = 7
        game._populate_initial_room = lambda room: events.append(("room", game.no_food))
        game._spawn_items = lambda: events.append(("put_things", game.no_food))
        game._spawn_amulet = lambda: None
        game._spawn_traps = lambda: None
        positions = iter([(5, 5), (6, 5)])
        game.find_floor_pos = lambda *a, **kw: next(positions)

        game.descend()

        self.assertIn(("room", 7), events)
        self.assertIn(("put_things", 8), events)

    def test_rogue_544_new_level_refreshes_hallucination_visuals_after_enter_room(self):
        # Rogue 5.4.4 new_level.c:new_level() calls visuals() after placing hero and enter_room().
        game = new_game(seed=3052)
        calls = []
        positions = iter([(5, 5), (6, 5)])
        game._populate_initial_room = lambda room: None
        game._spawn_items = lambda: None
        game._spawn_amulet = lambda: None
        game._spawn_traps = lambda: None
        game.find_floor_pos = lambda *a, **kw: next(positions)
        game.p.hallucinating = 10
        game.run_visuals = lambda: calls.append((game.p.x, game.p.y, bool(game.visible)))

        game.descend()

        self.assertEqual(calls, [(6, 5, True)])

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
        self.assertEqual([s.worth for s in rogue_sticks.STICKS], [250, 5, 330, 330, 330, 310, 170, 5, 350, 300, 5, 340, 50, 280])
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

    def test_rogue_544_zap_non_stick_direction_does_not_spend_turn(self):
        # Rogue 5.4.4 sticks.c:do_zap() sets after=FALSE when obj->o_type != STICK.
        game = new_game(seed=2011)
        potion = rogue.Item(rogue.CAT_POT, 0)
        game.zap_item = potion
        game.dact = "Zap"
        game.st = rogue.ST_DIR
        turn = game.turn

        game.dir_confirm(1, 0)

        self.assertEqual(game.turn, turn)
        self.assertIn("you can't zap with that!", game.msgs)

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

    def test_rogue_544_cancel_flytrap_releases_hold_without_resetting_vf_hit(self):
        # Rogue 5.4.4 sticks.c:do_zap() clears ISHELD for F but does not reset fight.c vf_hit.
        import rogue_sticks

        game = new_game(seed=204)
        set_open_floor(game)
        flytrap = monster_at(game.p.x + 2, game.p.y, sym="F", name="venus flytrap", flags="hold")
        flytrap.vf_hit = 3
        flytrap.damage_expr = "3x1"
        game.p.held_by = flytrap
        game.mons = [flytrap]

        cancel = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_CANCEL, charges=1)
        game.zap_stick(cancel, 1, 0)

        self.assertIsNone(game.p.held_by)
        self.assertEqual(flytrap.vf_hit, 3)
        self.assertEqual(flytrap.damage_expr, "3x1")

    def test_rogue_544_zap_any_flytrap_target_releases_player_hold(self):
        # Rogue 5.4.4 sticks.c:do_zap() clears player ISHELD when the target monster is F.
        import rogue_sticks

        game = new_game(seed=205)
        set_open_floor(game)
        holder = monster_at(game.p.x, game.p.y + 1, sym="F", name="venus flytrap", flags="hold")
        target = monster_at(game.p.x + 2, game.p.y, sym="F", name="venus flytrap", flags="hold")
        holder.vf_hit = 2
        game.p.held_by = holder
        game.mons = [holder, target]

        stick = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_INVIS, charges=1)
        game.zap_stick(stick, 1, 0)

        self.assertIsNone(game.p.held_by)
        self.assertEqual(holder.vf_hit, 2)
        self.assertIn("invis", target.flags)

    def test_rogue_544_cancelled_revealed_xeroc_keeps_disguise_as_type(self):
        # Rogue 5.4.4 sticks.c:do_zap() WS_CANCEL sets t_disguise = t_type.
        import rogue_sticks

        game = new_game(seed=305)
        set_open_floor(game)
        xeroc = monster_at(game.p.x + 2, game.p.y, sym="X", name="xeroc")
        xeroc.disguise = "X"
        game.mons = [xeroc]

        cancel = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_CANCEL, charges=1)
        game.zap_stick(cancel, 1, 0)

        self.assertEqual(xeroc.disguise, "X")
        self.assertEqual(game.visible_monster_sym(xeroc), "X")

    def test_rogue_544_cancel_passes_item_disguised_xeroc(self):
        # Rogue 5.4.4 sticks.c:do_zap() scans while step_ok(winat()), and winat() returns t_disguise.
        import rogue_sticks

        game = new_game(seed=306)
        set_open_floor(game)
        xeroc = monster_at(game.p.x + 2, game.p.y, sym="X", name="xeroc")
        xeroc.disguise = "?"
        game.mons = [xeroc]

        cancel = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_CANCEL, charges=1)
        game.zap_stick(cancel, 1, 0)

        self.assertEqual(cancel.charges, 0)
        self.assertEqual(xeroc.disguise, "?")
        self.assertNotIn("cancel", xeroc.flags)

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

    def test_rogue_544_polymorph_restores_mean_from_new_monster_spec(self):
        # Rogue 5.4.4 monsters.c:new_monster() rebuilds flags from extern.c:monsters[].
        game = new_game(seed=606)
        set_open_floor(game)
        monster = monster_at(game.p.x + 2, game.p.y, sym="H", name="hobgoblin", flags="mean")
        game.mons = [monster]
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            game.polymorph_monster(monster)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(monster.sym, "B")
        self.assertFalse(monster.mean)

    def test_rogue_544_zap_teleport_away_and_teleport_to_relocate_target(self):
        # Rogue 5.4.4 sticks.c:do_zap() WS_TELAWAY uses find_floor(!hero); WS_TELTO uses hero+delta.
        import rogue_sticks

        game = new_game(seed=204)
        set_open_floor(game)
        monster = monster_at(game.p.x + 3, game.p.y, sym="H", name="hobgoblin")
        game.mons = [monster]
        old_rnd = rogue.RNG.rnd
        try:
            rolls = iter([0, game.p.x + 4, game.p.y + 2])
            rogue.RNG.rnd = lambda n: next(rolls)
            away = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_TELAWAY, charges=1)
            game.zap_stick(away, 1, 0)
        finally:
            rogue.RNG.rnd = old_rnd

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

    def test_rogue_544_zap_teleport_away_uses_find_floor_rnd_pos_not_choice(self):
        # Rogue 5.4.4 sticks.c:WS_TELAWAY uses rooms.c:find_floor(NULL, ..., TRUE)
        # and retries only if the result is hero.
        import rogue_sticks

        game = new_game(seed=2041)
        set_two_room_floor(game)
        game.mons = []
        monster = monster_at(game.p.x + 3, game.p.y, sym="H", name="hobgoblin")
        game.mons = [monster]
        events = []

        class TeleAwayRng:
            def __init__(self):
                self.values = iter([1, 2, 3])

            def rnd(self, n):
                events.append(f"rnd:{n}")
                return next(self.values)

            def choice(self, seq):
                raise AssertionError("WS_TELAWAY should use rooms.c:find_floor(), not choice()")

            def roll(self, dice, sides):
                return dice

        old_rng = rogue.RNG
        try:
            rogue.RNG = TeleAwayRng()
            away = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_TELAWAY, charges=1)
            game.zap_stick(away, 1, 0)
        finally:
            rogue.RNG = old_rng

        self.assertEqual(events[:3], ["rnd:2", "rnd:8", "rnd:6"])
        self.assertEqual((monster.x, monster.y), (23, 5))

    def test_rogue_544_zap_teleport_target_does_not_clear_monster_hold(self):
        # Rogue 5.4.4 sticks.c:WS_TELAWAY/WS_TELTO set ISRUN directly, not through chase.c:runto().
        import rogue_sticks

        game = new_game(seed=206)
        set_open_floor(game)
        monster = monster_at(game.p.x + 3, game.p.y, sym="H", name="hobgoblin")
        monster.held = 4
        game.mons = [monster]
        old_rnd = rogue.RNG.rnd
        try:
            rolls = iter([0, game.p.x + 4, game.p.y + 2])
            rogue.RNG.rnd = lambda n: next(rolls)
            away = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_TELAWAY, charges=1)
            game.zap_stick(away, 1, 0)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertTrue(monster.running)
        self.assertEqual(monster.dest, rogue.DEST_PLAYER)
        self.assertEqual(monster.held, 4)

    def test_rogue_544_zap_teleport_away_find_floor_skips_plain_corridors(self):
        # Rogue 5.4.4 sticks.c:WS_TELAWAY uses rooms.c:find_floor(NULL, ..., monst=TRUE), which picks a room.
        game = new_game(seed=2061)
        set_two_room_floor(game)
        game.tm[12][12] = rogue.T_CORR
        old_rng = rogue.RNG
        try:
            rogue.RNG = SequenceRng([1, 1, 2])
            pos = game.random_monster_floor()
        finally:
            rogue.RNG = old_rng

        self.assertNotEqual(pos, (12, 12))
        self.assertEqual(pos, (22, 4))

    def test_rogue_544_zap_teleport_away_find_floor_allows_room_stairs_and_traps(self):
        # Rogue 5.4.4 rooms.c:find_floor(..., monst=TRUE) accepts step_ok(), not only FLOOR/PASSAGE.
        game = new_game(seed=2062)
        room_a, _ = set_two_room_floor(game)
        stair = (room_a.x + 2, room_a.y + 2)
        trap = (room_a.x + 3, room_a.y + 2)
        game.tm[stair[1]][stair[0]] = rogue.T_STAIR
        game.tm[trap[1]][trap[0]] = rogue.T_TRAP
        game.mons = []
        old_rng = rogue.RNG
        try:
            rogue.RNG = SequenceRng([0, 1, 1])
            stair_pos = game.random_monster_floor()
            rogue.RNG = SequenceRng([0, 2, 1])
            trap_pos = game.random_monster_floor()
        finally:
            rogue.RNG = old_rng

        self.assertEqual(stair_pos, stair)
        self.assertEqual(trap_pos, trap)

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

    def test_rogue_544_zap_haste_slow_flytrap_does_not_release_player(self):
        # Rogue 5.4.4 sticks.c:do_zap() clears ISHELD for the misc target group, not WS_HASTE_M/WS_SLOW_M.
        import rogue_sticks

        game = new_game(seed=206)
        set_open_floor(game)
        flytrap = monster_at(game.p.x + 2, game.p.y, sym="F", name="venus flytrap")
        game.p.held_by = flytrap
        game.mons = [flytrap]

        haste = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_HASTE_M, charges=1)
        game.zap_stick(haste, 1, 0)

        self.assertIs(game.p.held_by, flytrap)

        slow = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_SLOW_M, charges=1)
        game.zap_stick(slow, 1, 0)

        self.assertIs(game.p.held_by, flytrap)

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

    def test_rogue_544_magic_missile_hit_uses_fight_thrown_side_effects(self):
        # Rogue 5.4.4 sticks.c:WS_MISSILE calls weapons.c:hit_monster() -> fight(..., thrown=TRUE).
        game = new_game(seed=230)
        set_open_floor(game)
        game.p.quiet = 9
        game.p.can_confuse_monster = True
        monster = monster_at(game.p.x + 2, game.p.y, hp=20)
        game.mons = [monster]
        old_roll = rogue.RNG.roll
        try:
            rogue.RNG.roll = lambda number, sides: 1
            game.hit_monster_with_magic_missile(monster)
        finally:
            rogue.RNG.roll = old_roll

        self.assertEqual(game.p.quiet, 0)
        self.assertFalse(game.p.can_confuse_monster)
        self.assertEqual(monster.confused, 1)
        self.assertTrue(monster.running)

    def test_rogue_544_magic_missile_reveals_disguised_xeroc_and_continues_hit(self):
        # Rogue 5.4.4 fight.c:fight(..., thrown=TRUE) reveals Xeroc but continues thrown attack.
        game = new_game(seed=231)
        set_open_floor(game)
        xeroc = monster_at(game.p.x + 2, game.p.y, sym="X", name="xeroc", hp=40)
        xeroc.disguise = "?"
        game.mons = [xeroc]
        old_roll = rogue.RNG.roll
        try:
            rogue.RNG.roll = lambda number, sides: 4
            game.hit_monster_with_magic_missile(xeroc)
        finally:
            rogue.RNG.roll = old_roll

        self.assertEqual(xeroc.disguise, "X")
        self.assertLess(xeroc.hp, 40)
        self.assertIn("wait!  That's a xeroc!", game.msgs)

    def test_rogue_544_zap_magic_missile_passes_item_disguised_xeroc(self):
        # Rogue 5.4.4 sticks.c:do_motion() uses winat(); item-like Xeroc disguise is step_ok().
        import rogue_sticks

        game = new_game(seed=232)
        set_open_floor(game)
        xeroc = monster_at(game.p.x + 2, game.p.y, sym="X", name="xeroc", hp=40)
        xeroc.disguise = "?"
        game.mons = [xeroc]
        saves = []
        game.monster_save_throw = lambda versus, monster: saves.append((versus, monster)) or False

        stick = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_MISSILE, charges=1)
        game.zap_stick(stick, 1, 0)

        self.assertEqual(stick.charges, 0)
        self.assertEqual(saves, [])
        self.assertEqual(xeroc.disguise, "?")
        self.assertEqual(xeroc.hp, 40)
        self.assertIn("the missle vanishes with a puff of smoke", game.msgs)

    def test_rogue_544_sticks_helper_magic_missile_damage(self):
        # Rogue 5.4.4 sticks.c:WS_MISSILE uses 1x4 + o_dplus + cur_weapon o_dplus + strength damage.
        import rogue_sticks

        self.assertEqual(rogue_sticks.magic_missile_damage(4, 3, 1), 9)
        self.assertEqual(rogue_sticks.magic_missile_damage(1, -5, 0), 0)

    def test_rogue_544_sticks_helper_zap_flytrap_release_group(self):
        # Rogue 5.4.4 sticks.c:do_zap() clears ISHELD only for this target-effect case group.
        import rogue_sticks

        releasing = {
            rogue_sticks.WS_INVIS,
            rogue_sticks.WS_POLYMORPH,
            rogue_sticks.WS_TELAWAY,
            rogue_sticks.WS_TELTO,
            rogue_sticks.WS_CANCEL,
        }

        for kind in range(len(rogue_sticks.STICKS)):
            self.assertEqual(rogue_sticks.zap_releases_flytrap(kind), kind in releasing)

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

    def test_rogue_544_zap_magic_missile_stops_at_door_before_target(self):
        # Rogue 5.4.4 weapons.c:do_motion() stops WS_MISSILE on DOOR before moat().
        import rogue_sticks

        game = new_game(seed=212)
        set_open_floor(game)
        px, py = game.p.x, game.p.y
        game.tm[py][px + 1] = rogue.T_DOOR
        monster = monster_at(px + 2, py, hp=10)
        game.mons = [monster]
        game.monster_save_throw = lambda which, m: False
        stick = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_MISSILE, charges=1)

        game.zap_stick(stick, 1, 0)

        self.assertEqual(stick.charges, 0)
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
        for x in range(game.p.x, game.p.x + 5):
            game.tm[game.p.y][x] = rogue.T_CORR
        monster = monster_at(game.p.x + 4, game.p.y, hp=10)
        game.mons = [monster]
        stick = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_DRAIN, charges=1)

        game.zap_stick(stick, 1, 0)

        self.assertEqual(game.p.hp, 6)
        self.assertEqual(monster.hp, 4)

    def test_rogue_544_zap_drain_in_passage_skips_different_passage(self):
        # Rogue 5.4.4 sticks.c:drain() compares roomin()/F_PNUM passage identity.
        import rogue_sticks

        game = new_game(seed=210)
        set_open_floor(game)
        game.p.hp = 12
        for x in range(game.p.x, game.p.x + 5):
            game.tm[game.p.y][x] = rogue.T_CORR
        other_x = game.p.x + 8
        game.tm[game.p.y][other_x] = rogue.T_CORR
        same = monster_at(game.p.x + 4, game.p.y, hp=10)
        other = monster_at(other_x, game.p.y, hp=10)
        game.mons = [same, other]
        stick = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_DRAIN, charges=1)

        game.zap_stick(stick, 1, 0)

        self.assertEqual(game.p.hp, 6)
        self.assertEqual(same.hp, 4)
        self.assertEqual(other.hp, 10)

    def test_rogue_544_zap_drain_on_door_targets_room_and_passage(self):
        # Rogue 5.4.4 sticks.c:drain() uses proom plus corp when hero stands on DOOR.
        import rogue_sticks

        game = new_game(seed=211)
        set_open_floor(game)
        room = rogue.Room(10, 8, 8, 5)
        game.rooms = [room]
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for y in range(room.y + 1, room.y + room.h - 1):
            for x in range(room.x + 1, room.x + room.w - 1):
                game.tm[y][x] = rogue.T_FLOOR
        game.p.x, game.p.y = room.x, room.y + 2
        game.tm[game.p.y][game.p.x] = rogue.T_DOOR
        for x in range(game.p.x - 3, game.p.x):
            game.tm[game.p.y][x] = rogue.T_CORR
        game.tm[game.p.y][game.p.x - 6] = rogue.T_CORR
        room_monster = monster_at(game.p.x + 1, game.p.y, hp=10)
        passage_monster = monster_at(game.p.x - 3, game.p.y, hp=10)
        other_passage_monster = monster_at(game.p.x - 6, game.p.y, hp=10)
        game.mons = [room_monster, passage_monster, other_passage_monster]
        game.p.hp = 12
        stick = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_DRAIN, charges=1)

        game.zap_stick(stick, 1, 0)

        self.assertEqual(game.p.hp, 6)
        self.assertEqual(room_monster.hp, 7)
        self.assertEqual(passage_monster.hp, 7)
        self.assertEqual(other_passage_monster.hp, 10)

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
        game.p.quiet = 9
        game.p.can_confuse_monster = True
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
        self.assertEqual(game.p.quiet, 0)
        self.assertFalse(game.p.can_confuse_monster)
        self.assertEqual(monster.confused, 1)
        self.assertTrue(monster.running)
        self.assertIn("the bolt hits the hobgoblin", game.msgs)

    def test_rogue_544_bolt_reveals_disguised_xeroc_and_continues_hit(self):
        # Rogue 5.4.4 sticks.c:fire_bolt() hit_monster() uses fight(..., thrown=TRUE).
        import rogue_sticks

        game = new_game(seed=232)
        set_open_floor(game)
        xeroc = monster_at(game.p.x + 2, game.p.y, sym="X", name="xeroc", hp=40)
        xeroc.disguise = "?"
        game.mons = [xeroc]
        game.monster_save_throw = lambda which, m: False
        old_roll = rogue.RNG.roll
        try:
            rogue.RNG.roll = lambda number, sides: 6
            stick = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_FIRE, charges=1)
            game.zap_stick(stick, 1, 0)
        finally:
            rogue.RNG.roll = old_roll

        self.assertEqual(xeroc.disguise, "X")
        self.assertLess(xeroc.hp, 40)
        self.assertIn("wait!  That's a xeroc!", game.msgs)

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

    def test_rogue_544_unseen_bolt_miss_uses_something_name(self):
        # Rogue 5.4.4 sticks.c:fire_bolt() miss text uses fight.c:set_mname().
        game = new_game(seed=2191)
        set_open_floor(game)
        game.p.x, game.p.y = 10, 10
        orc = monster_at(12, 10, sym="O", name="orc")
        game.mons = [orc]
        game.visible = {(10, 10)}
        game.monster_save_throw = lambda which, monster: True

        hit = game.fire_bolt(1, 0, "flame")

        self.assertFalse(hit)
        self.assertIn("the flame whizzes past something", game.msgs)
        self.assertNotIn("the flame whizzes past the orc", game.msgs)

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

    def test_rogue_544_bolt_hits_monster_standing_on_door_before_door_bounce(self):
        # Rogue 5.4.4 sticks.c:fire_bolt() uses winat(); a monster on DOOR is seen before terrain bounce.
        import rogue_sticks

        game = new_game(seed=229)
        set_open_floor(game)
        game.p.hp = 30
        x, y = game.p.x + 2, game.p.y
        game.tm[y][x] = rogue.T_DOOR
        monster = monster_at(x, y, hp=40)
        game.mons = [monster]
        game.monster_save_throw = lambda which, m: False
        old_roll = rogue.RNG.roll
        try:
            rogue.RNG.roll = lambda number, sides: 12
            stick = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_FIRE, charges=1)
            game.zap_stick(stick, 1, 0)
        finally:
            rogue.RNG.roll = old_roll

        self.assertEqual(monster.hp, 28)
        self.assertEqual(game.p.hp, 30)
        self.assertIn("the flame hits the hobgoblin", game.msgs)

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

    def test_rogue_544_dragon_breath_clears_running_count_and_quiet(self):
        # Rogue 5.4.4 chase.c:do_chase() clears running/count/quiet after Dragon fire_bolt().
        game = new_game(seed=225)
        set_open_floor(game)
        game.p.x, game.p.y = 10, 10
        game.p.hp = 30
        game.p.quiet = 7
        game.dashing = True
        game.dash_steps = 6
        dragon = monster_at(game.p.x + rogue.BOLT_LENGTH, game.p.y, sym="D", name="dragon", flags="")
        dragon.running = True
        game.mons = [dragon]
        game.save_vs_magic = lambda: True
        old_rnd = rogue.RNG.rnd
        old_roll = rogue.RNG.roll
        try:
            rogue.RNG.rnd = lambda n: 0
            rogue.RNG.roll = lambda number, sides: 12
            game.do_chase(dragon)
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.RNG.roll = old_roll

        self.assertFalse(game.dashing)
        self.assertEqual(game.dash_steps, 0)
        self.assertEqual(game.p.quiet, 0)

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

    def test_rogue_544_dragon_breath_only_when_chaser_and_hero_same_room(self):
        # Rogue 5.4.4 chase.c:do_chase() checks Dragon breath only in the rer == ree branch.
        game = new_game(seed=226)
        room = rogue.Room(10, 8, 8, 5)
        game.rooms = [room]
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for y in range(room.y + 1, room.y + room.h - 1):
            for x in range(room.x + 1, room.x + room.w - 1):
                game.tm[y][x] = rogue.T_FLOOR
        for x in range(5, 11):
            game.tm[10][x] = rogue.T_CORR
        game.tm[10][10] = rogue.T_DOOR
        game.p.x, game.p.y = 11, 10
        dragon = monster_at(5, 10, sym="D", name="dragon", flags="")
        dragon.running = True
        game.mons = [dragon]
        breaths = []
        game.try_dragon_breath = lambda monster: breaths.append(monster) or True

        game.do_chase(dragon)

        self.assertEqual(breaths, [])

    def test_rogue_544_dragon_on_door_can_breathe_at_hero_in_same_room(self):
        # Rogue 5.4.4 chase.c:roomin() treats DOOR as room for do_chase() Dragon breath.
        game = new_game(seed=227)
        room = rogue.Room(10, 8, 10, 5)
        game.rooms = [room]
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for y in range(room.y + 1, room.y + room.h - 1):
            for x in range(room.x + 1, room.x + room.w - 1):
                game.tm[y][x] = rogue.T_FLOOR
        game.tm[10][10] = rogue.T_DOOR
        for x in range(7, 10):
            game.tm[10][x] = rogue.T_CORR
        game.p.x, game.p.y = 16, 10
        game.p.hp = 30
        dragon = monster_at(10, 10, sym="D", name="dragon", flags="")
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
        self.assertEqual((dragon.x, dragon.y), (10, 10))

    def test_rogue_544_dragon_breaths_at_hero_on_room_door(self):
        # Rogue 5.4.4 passages.c:numpass() numbers normal DOOR exits without F_PASS;
        # chase.c:do_chase() therefore sees a hero on a room door as in proom.
        game = new_game(seed=2271)
        room = rogue.Room(10, 8, 10, 5)
        game.rooms = [room]
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for y in range(room.y + 1, room.y + room.h - 1):
            for x in range(room.x + 1, room.x + room.w - 1):
                game.tm[y][x] = rogue.T_FLOOR
        game.tm[10][10] = rogue.T_DOOR
        game.p.x, game.p.y = 10, 10
        game.p.hp = 30
        dragon = monster_at(16, 10, sym="D", name="dragon", flags="")
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
        self.assertEqual((dragon.x, dragon.y), (16, 10))
        self.assertIn("you are hit by the flame", game.msgs)

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

    def test_rogue_544_bolt_saved_miss_suppresses_mismatched_magic_m_glyph(self):
        # Rogue 5.4.4 sticks.c:fire_bolt() saved-miss feedback is gated by
        # winat() != 'M' || t_disguise == 'M'.
        game = new_game(seed=2261)
        set_open_floor(game)
        game.p.x, game.p.y = 10, 10
        orc = monster_at(12, 10, sym="O", name="orc")
        game.mons = [orc]
        game.monster_save_throw = lambda which, monster: True
        game.zap_winat_char = lambda x, y: "M" if (x, y) == (orc.x, orc.y) else "."

        hit = game.fire_bolt(1, 0, "flame")

        self.assertFalse(hit)
        self.assertFalse(orc.running)
        self.assertNotIn("the flame whizzes past the orc", game.msgs)

    def test_rogue_544_bolt_miss_reports_disguised_xeroc_name(self):
        # Rogue 5.4.4 sticks.c:fire_bolt() uses winat(); item-disguised Xeroc still passes ch != 'M'.
        game = new_game(seed=227)
        set_open_floor(game)
        game.p.x, game.p.y = 10, 10
        xeroc = monster_at(12, 10, sym="X", name="xeroc")
        xeroc.disguise = "!"
        game.mons = [xeroc]
        game.monster_save_throw = lambda which, monster: True

        hit = game.fire_bolt(1, 0, "flame")

        self.assertFalse(hit)
        self.assertTrue(xeroc.running)
        self.assertIn("the flame whizzes past the xeroc", game.msgs)

    def test_rogue_544_sticks_helper_saved_monster_miss_feedback(self):
        # Rogue 5.4.4 sticks.c:fire_bolt() saved monster miss display/runto branch.
        import rogue_sticks

        self.assertEqual(rogue_sticks.saved_monster_miss_feedback(True), (True, True))
        self.assertEqual(rogue_sticks.saved_monster_miss_feedback(False), (False, True))
        self.assertEqual(rogue_sticks.saved_monster_miss_feedback(True, "M", "O"), (False, False))
        self.assertEqual(rogue_sticks.saved_monster_miss_feedback(True, "M", "M"), (True, True))

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

    def test_rogue_544_hallucination_prevents_medusa_gaze(self):
        # Rogue 5.4.4 monsters.c:wake_monster() gates Medusa gaze with !ISHALU.
        game = new_game(seed=208)
        set_open_floor(game)
        game.p.hallucinating = 10
        medusa = monster_at(game.p.x + 1, game.p.y, "M", "medusa", flags="confuse")
        medusa.running = True
        game.mons = [medusa]
        old_save = game.save_vs_magic
        try:
            game.save_vs_magic = lambda: False
            game.wake_monster(medusa)
        finally:
            game.save_vs_magic = old_save

        self.assertEqual(game.p.confused, 0)
        self.assertFalse(medusa.found)

    def test_rogue_544_dark_room_medusa_gaze_requires_lamp_distance(self):
        # Rogue 5.4.4 monsters.c:wake_monster() requires dist() < LAMPDIST in a dark room.
        game = new_game(seed=209)
        set_open_floor(game)
        dark = rogue.Room(1, 1, 12, 8, {rogue.ROOM_DARK})
        game.rooms = [dark]
        game.p.x, game.p.y = 5, 5
        medusa = monster_at(game.p.x + 2, game.p.y, "M", "medusa", flags="confuse")
        medusa.running = True
        game.mons = [medusa]
        old_save = game.save_vs_magic
        try:
            game.save_vs_magic = lambda: False
            game.wake_monster(medusa)
        finally:
            game.save_vs_magic = old_save

        self.assertEqual(game.p.confused, 0)
        self.assertFalse(medusa.found)

    def test_rogue_544_medusa_gaze_uses_unconfuse_fuse(self):
        # Rogue 5.4.4 monsters.c:wake_monster() uses fuse/lengthen(unconfuse, spread(HUHDURATION)).
        game = new_game(seed=211)
        set_open_floor(game)
        medusa = monster_at(game.p.x + 1, game.p.y, "M", "medusa", flags="confuse")
        medusa.running = True
        game.mons = [medusa]
        old_save = game.save_vs_magic
        old_rnd = rogue.RNG.rnd
        try:
            game.save_vs_magic = lambda: False
            rogue.RNG.rnd = lambda n: 1
            game.wake_monster(medusa)
        finally:
            game.save_vs_magic = old_save
            rogue.RNG.rnd = old_rnd

        duration = rogue.HUHDURATION - rogue.HUHDURATION // 20 + 1
        self.assertEqual(game.p.confused, duration)
        self.assertEqual(game.fuses.remaining("unconfuse"), duration)
        self.assertIn("the medusa's gaze has confused you", game.msgs)

    def test_rogue_544_levitation_prevents_mean_monster_wake(self):
        # Rogue 5.4.4 monsters.c:wake_monster() gates mean monster wake with !ISLEVIT.
        game = new_game(seed=207)
        set_open_floor(game)
        game.p.levitating = 10
        hobgoblin = monster_at(game.p.x + 1, game.p.y, "H", "hobgoblin", flags="mean")

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            game.wake_monster(hobgoblin)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertFalse(hobgoblin.running)

    def test_rogue_544_cancelled_monsters_do_not_use_special_attack(self):
        # Rogue 5.4.4 fight.c:attack() special switch is gated by !ISCANC.
        game = new_game(seed=207)
        set_open_floor(game)
        ice = monster_at(game.p.x + 1, game.p.y, "I", "ice monster", 10, 20, 100, "0x0", 5, "freeze,cancel")
        game.m_attack(ice)
        self.assertEqual(game.p.no_command, 0)

    def test_rogue_544_isregen_flag_does_not_heal_monsters(self):
        # Rogue 5.4.4 defines ISREGEN in rogue.h/extern.c but has no monster regen tick in chase.c.
        game = new_game(seed=208)
        set_open_floor(game)
        troll = monster_at(game.p.x + 4, game.p.y, "T", "troll", hp=10, level=6, armor=4, damage="1x8", exp=120, flags="regen,mean")
        troll.max_hp = 20
        troll.running = True
        old_random = rogue.RNG.random
        try:
            rogue.RNG.random = lambda: 0
            game.chase(troll, (game.p.x, game.p.y))
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
        self.assertEqual([r.worth for r in rogue_rings.RINGS], [400, 400, 280, 420, 310, 10, 10, 440, 400, 460, 240, 30, 470, 380])
        self.assertEqual(rogue_rings.STONES[:4], ["agate", "alexandrite", "amethyst", "carnelian"])
        self.assertEqual(rogue_rings.STONES[-2:], ["taaffeite", "zircon"])
        self.assertEqual(rogue_rings.STONE_VALUES[:4], [25, 40, 50, 40])
        self.assertEqual(rogue_rings.STONE_VALUES[-2:], [300, 80])

        ident = rogue.IdentTable()
        ring = rogue.Item(rogue.CAT_RING, rogue_rings.R_PROTECT, ench=2)
        self.assertEqual(ident.name(ring), f"{ident.rstones[rogue_rings.R_PROTECT]} ring")
        ident.rk[rogue_rings.R_PROTECT] = True
        self.assertEqual(ident.name(ring), "ring of protection [+2]")

    def test_rogue_544_init_stones_uses_rnd_unique_order_and_adds_worth(self):
        # Rogue 5.4.4 init.c:init_stones() retries rnd(NSTONES) and adds stone value to ring_info[].oi_worth.
        import rogue_rings

        class StoneRng:
            def __init__(self):
                self.rolls = iter([0, 0, 1, 4, 7, 2, 3, 5, 6, 8, 9, 10, 11, 12, 13])
                self.calls = []

            def rnd(self, n):
                self.calls.append(n)
                return next(self.rolls)

        rng = StoneRng()
        names, worths = rogue_rings.init_stones_and_worths(rng)

        self.assertEqual(rng.calls, [26] * 15)
        self.assertEqual(names[:5], ["agate", "alexandrite", "diamond", "granite", "amethyst"])
        self.assertEqual(worths[:5], [425, 440, 580, 425, 360])

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

    def test_rogue_544_sticks_helper_charge_str_matches_isknow_and_terse(self):
        # Rogue 5.4.4 sticks.c:charge_str() checks ISKNOW internally and has a terse branch.
        import rogue_sticks

        stick = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_LIGHT, charges=7, known=False)
        self.assertEqual(rogue_sticks.charge_str(stick), "")
        stick.known = True
        self.assertEqual(rogue_sticks.charge_str(stick), " [7 charges]")
        self.assertEqual(rogue_sticks.charge_str(stick, terse=True), " [7]")

    def test_rogue_544_nameit_guess_order_for_potion_ring_and_stick(self):
        # Rogue 5.4.4 things.c:nameit() formats guesses as "type called guess(material)".
        import rogue_rings
        import rogue_sticks

        ident = rogue.IdentTable()
        ident.pcol[0] = "red"
        ident.pg[0] = "heal"
        self.assertEqual(ident.name(rogue.Item(rogue.CAT_POT, 0), rogue.LANG_EN), "potion called heal(red)")

        ident.rstones[rogue_rings.R_PROTECT] = "agate"
        ident.rg[rogue_rings.R_PROTECT] = "guard"
        ring = rogue.Item(rogue.CAT_RING, rogue_rings.R_PROTECT)
        self.assertEqual(ident.name(ring, rogue.LANG_EN), "ring called guard(agate)")

        ident.wtypes[rogue_sticks.WS_LIGHT] = "wand"
        ident.wmades[rogue_sticks.WS_LIGHT] = "copper"
        ident.wg[rogue_sticks.WS_LIGHT] = "zap"
        stick = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_LIGHT)
        self.assertEqual(ident.name(stick, rogue.LANG_EN), "wand called zap(copper)")

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
        self.assertEqual([p["worth"] for p in rogue.POTIONS],
                         [5, 5, 5, 150, 100, 130, 130, 105, 250, 200, 190, 130, 5, 75])

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
        # Rogue 5.4.4 rings.c:ring_on/ring_off, misc.c:chg_str(), and things.c:dropcheck().
        import rogue_rings

        player = rogue.Player()
        add_str = rogue.Item(rogue.CAT_RING, rogue_rings.R_ADDSTR, ench=2)
        prot = rogue.Item(rogue.CAT_RING, rogue_rings.R_PROTECT, ench=1)
        player.arm = rogue.Item(rogue.CAT_ARM, 0, ench=1)
        player.recalc_ac()

        self.assertTrue(rogue_rings.put_on_ring(player, add_str, rogue_rings.LEFT))
        self.assertEqual(player.st, 18)
        self.assertEqual(player.max_st, 16)
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

    def test_rogue_544_melee_existing_confusion_does_not_print_appears_confused(self):
        # Rogue 5.4.4 fight.c:fight() prints appears confused only when CANHUH was consumed.
        game = new_game(seed=313)
        set_open_floor(game)
        monster = monster_at(game.p.x + 1, game.p.y, hp=20, armor=-100, exp=0)
        monster.confused = 2
        game.swing_hits = lambda at_lvl, op_arm, wplus: True

        game.p_attack(monster)

        self.assertNotIn("the hobgoblin appears confused", game.msgs)

    def test_rogue_544_blind_melee_confusion_hit_suppresses_appears_confused(self):
        # Rogue 5.4.4 fight.c:fight() gates the appears-confused message with !ISBLIND.
        game = new_game(seed=314)
        set_open_floor(game)
        game.p.blind = 5
        game.p.can_confuse_monster = True
        monster = monster_at(game.p.x + 1, game.p.y, hp=20, armor=-100, exp=0)
        game.swing_hits = lambda at_lvl, op_arm, wplus: True

        game.p_attack(monster)

        self.assertFalse(game.p.can_confuse_monster)
        self.assertEqual(monster.confused, 1)
        self.assertNotIn("the hobgoblin appears confused", game.msgs)

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

    def test_rogue_544_read_scroll_clears_guess_when_scroll_becomes_known(self):
        # Rogue 5.4.4 scrolls.c:read_scroll() calls misc.c:call_it(), which clears oi_guess if oi_know.
        game = new_game(seed=3141)
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "magic mapping")
        scroll = rogue.Item(rogue.CAT_SCR, kind)
        game.p.inv.append(scroll)
        game.ident.sk[kind] = False
        game.ident.sg[kind] = "old guess"

        game.use_scr(scroll)

        self.assertTrue(game.ident.sk[kind])
        self.assertIsNone(game.ident.sg[kind])

    def test_rogue_544_read_scroll_preserves_guess_when_scroll_remains_unknown(self):
        # Rogue 5.4.4 misc.c:call_it() leaves an existing oi_guess when oi_know is false.
        game = new_game(seed=3142)
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "monster confusion")
        scroll = rogue.Item(rogue.CAT_SCR, kind)
        game.p.inv.append(scroll)
        game.ident.sk[kind] = False
        game.ident.sg[kind] = "old guess"

        game.use_scr(scroll)

        self.assertFalse(game.ident.sk[kind])
        self.assertEqual(game.ident.sg[kind], "old guess")

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
        self.assertEqual(near.held, 1)
        self.assertTrue(far.running)
        self.assertEqual(sleeping.held, 0)

    def test_rogue_544_scroll_hold_monster_does_not_roll_duration(self):
        # Rogue 5.4.4 scrolls.c:S_HOLD sets ISHELD without a duration roll.
        import rogue_scrolls

        hero = rogue.Player()
        hero.x = 10
        hero.y = 10
        monster = monster_at(11, 10)
        monster.running = True

        held_count = rogue_scrolls.hold_monsters(
            hero,
            [monster],
            lambda n: (_ for _ in ()).throw(AssertionError("duration rolled")),
        )

        self.assertEqual(held_count, 1)
        self.assertEqual(monster.held, 1)

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
        # Rogue 5.4.4 scrolls.c:S_AGGR calls misc.c:aggravate(), which only runto()s all monsters.
        import rogue_scrolls

        first = monster_at(1, 1)
        second = monster_at(2, 2)
        first.held = 3
        second.scared = 4
        seen = []

        def fake_runto(monster):
            seen.append((monster, monster.held))
            monster.held = 0

        rogue_scrolls.aggravate_monsters([first, second], fake_runto)

        self.assertEqual(seen, [(first, 3), (second, 0)])
        self.assertEqual((first.held, second.scared), (0, 4))

    def test_rogue_544_scrolls_helper_teleport_identifies_on_room_change(self):
        # Rogue 5.4.4 scrolls.c:S_TELEP identifies only when cur_room changes.
        import rogue_scrolls

        room = object()
        self.assertFalse(rogue_scrolls.teleport_identifies(room, room))
        self.assertTrue(rogue_scrolls.teleport_identifies(room, object()))
        self.assertIsNone(rogue_scrolls.call_it_guess_after_read(True, "old"))
        self.assertEqual(rogue_scrolls.call_it_guess_after_read(False, "old"), "old")

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

    def test_rogue_544_wielded_enchant_weapon_scroll_clears_current_before_effect(self):
        # Rogue 5.4.4 scrolls.c:read_scroll() clears cur_weapon before S_ENCH.
        game = new_game(seed=325)
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "enchant weapon")
        scroll = rogue.Item(rogue.CAT_SCR, kind, qty=2)
        game.p.inv.append(scroll)
        game.p.wpn = scroll

        game.use_scr(scroll)

        self.assertIsNone(game.p.wpn)
        self.assertIn(scroll, game.p.inv)
        self.assertEqual(scroll.qty, 1)
        self.assertEqual(scroll.hit_plus, 0)
        self.assertEqual(scroll.dam_plus, 0)
        self.assertIn("you feel a strange sense of loss", game.msgs)

    def test_rogue_544_scrolls_helper_enchant_weapon_matches_s_ench(self):
        # Rogue 5.4.4 scrolls.c:S_ENCH clears ISCURSED and increments one weapon plus.
        import rogue_scrolls

        weapon = rogue.Item(rogue.CAT_WPN, 0, hit_plus=2, dam_plus=3, cursed=True)
        self.assertTrue(rogue_scrolls.enchant_weapon(weapon, lambda n: 1))
        self.assertFalse(weapon.cursed)
        self.assertEqual((weapon.hit_plus, weapon.dam_plus), (2, 4))
        self.assertFalse(rogue_scrolls.enchant_weapon(None, lambda n: 0))

    def test_rogue_544_enchant_armor_does_not_identify_on_read(self):
        # Rogue 5.4.4 scrolls.c:S_ARMOR enchants cur_armor but has no no-armor message
        # and does not set scr_info[].oi_know.
        game = new_game(seed=323)
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "enchant armor")
        empty_scroll = rogue.Item(rogue.CAT_SCR, kind)
        game.p.arm = None
        game.p.inv.append(empty_scroll)

        game.use_scr(empty_scroll)

        self.assertFalse(game.ident.sk[kind])
        self.assertNotIn("you feel a strange sense of loss", game.msgs)

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
        same_pos = room_a.inner()
        game.find_floor_pos = lambda *args, **kwargs: same_pos

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
        other_pos = room_b.inner()
        game.find_floor_pos = lambda *args, **kwargs: other_pos

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

    def test_rogue_544_teleport_scroll_uses_find_floor_not_room_choice(self):
        # Rogue 5.4.4 scrolls.c:S_TELEP calls wizard.c:teleport(),
        # which relocates the hero through rooms.c:find_floor(..., monst=TRUE).
        game = new_game(seed=326)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        room_a = rogue.Room(1, 1, 8, 6)
        room_b = rogue.Room(20, 1, 8, 6)
        game.rooms = [room_a, room_b]
        for room in game.rooms:
            for y in range(room.y + 1, room.y + room.h - 1):
                for x in range(room.x + 1, room.x + room.w - 1):
                    game.tm[y][x] = rogue.T_FLOOR
        game.p.x, game.p.y = room_a.inner()
        game.usable_rooms = lambda: [room_a]
        game.random_room_tile = lambda room, tiles: room.inner()
        calls = []
        target = room_b.inner()
        game.find_floor_pos = lambda *args, **kwargs: calls.append((args, kwargs)) or target
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "teleportation")
        scroll = rogue.Item(rogue.CAT_SCR, kind)
        game.p.inv.append(scroll)

        game.use_scr(scroll)

        self.assertEqual((game.p.x, game.p.y), target)
        self.assertEqual(calls[0][1]["monst"], True)
        self.assertTrue(game.ident.sk[kind])

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

    def test_rogue_544_create_monster_uses_winat_for_item_disguised_xeroc(self):
        # Rogue 5.4.4 scrolls.c:S_CREATE uses step_ok(winat()), then monsters.c:new_monster() attaches at mlist head.
        class CreateMonsterRng:
            def __init__(self):
                self.rolls = iter([0, 0, 2])

            def rnd(self, n):
                return next(self.rolls)

            def choice(self, seq):
                raise AssertionError("choice used")

            def roll(self, dice, sides):
                return dice

        game = new_game(seed=338)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        game.rooms = [rogue.Room(1, 1, 8, 8)]
        game.p.x, game.p.y = 4, 4
        game.tm[game.p.y][game.p.x] = rogue.T_FLOOR
        game.tm[game.p.y - 1][game.p.x - 1] = rogue.T_FLOOR
        xeroc = monster_at(game.p.x - 1, game.p.y - 1, sym="X", name="xeroc")
        xeroc.disguise = "?"
        game.mons = [xeroc]
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "create monster")
        scroll = rogue.Item(rogue.CAT_SCR, kind)
        game.p.inv.append(scroll)

        old_rng = rogue.RNG
        rogue.RNG = CreateMonsterRng()
        try:
            game.use_scr(scroll)
        finally:
            rogue.RNG = old_rng

        self.assertEqual([mo.sym for mo in game.mons], ["B", "X"])
        self.assertIs(game.mon_at(game.p.x - 1, game.p.y - 1), game.mons[0])

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
                self.rolls = iter([1, 2, 3, 9, 6])

            def rnd(self, n):
                return next(self.rolls)

            def choice(self, seq):
                return seq[0]

            def roll(self, dice, sides):
                return dice

        game = new_game(seed=339)
        set_two_room_floor(game)
        game.p.depth = 2
        game.mons = []
        old_rng = rogue.RNG
        rogue.RNG = WanderRng()
        try:
            self.assertTrue(game.spawn_wanderer())
        finally:
            rogue.RNG = old_rng

        self.assertEqual([mo.sym for mo in game.mons], ["B"])

    def test_rogue_544_spawn_wanderer_find_floor_retries_player_room_before_randmonster(self):
        # Rogue 5.4.4 monsters.c:wanderer() calls rooms.c:find_floor(NULL, ..., TRUE)
        # until roomin(cp) != proom, then randmonster(TRUE).
        game = new_game(seed=3391)
        room_a, _ = set_two_room_floor(game)
        game.p.depth = 2
        game.p.x, game.p.y = room_a.x + 2, room_a.y + 2
        game.mons = []
        events = []

        class WanderFloorRng:
            def __init__(self):
                self.values = iter([0, 1, 1, 1, 2, 3, 9, 6])

            def rnd(self, n):
                events.append(f"rnd:{n}")
                return next(self.values)

            def choice(self, seq):
                raise AssertionError("monsters.c:wanderer() should use find_floor(), not choice()")

            def roll(self, dice, sides):
                return dice

        old_rng = rogue.RNG
        try:
            rogue.RNG = WanderFloorRng()
            self.assertTrue(game.spawn_wanderer())
        finally:
            rogue.RNG = old_rng

        self.assertEqual(events[:8], ["rnd:2", "rnd:8", "rnd:6", "rnd:2", "rnd:8", "rnd:6", "rnd:10", "rnd:10"])
        self.assertEqual([(mo.x, mo.y, mo.sym) for mo in game.mons], [(23, 5, "B")])

    def test_rogue_544_wanderer_floor_pos_retries_player_room_without_fixed_cap(self):
        # Rogue 5.4.4 monsters.c:wanderer() has no fixed retry cap around the proom check.
        game = new_game(seed=3392)
        room_a, room_b = set_two_room_floor(game)
        player_room_pos = (room_a.x + 2, room_a.y + 2)
        other_room_pos = (room_b.x + 2, room_b.y + 2)
        game.p.x, game.p.y = player_room_pos
        positions = [player_room_pos, player_room_pos, other_room_pos]
        calls = []

        old_map_w = rogue.MAP_W
        old_map_h = rogue.MAP_H
        old_find_floor_pos = game.find_floor_pos
        try:
            rogue.MAP_W = 1
            rogue.MAP_H = 1

            def fake_find_floor_pos(*args, **kwargs):
                calls.append((args, kwargs))
                return positions.pop(0)

            game.find_floor_pos = fake_find_floor_pos
            self.assertEqual(game.wanderer_floor_pos(), other_room_pos)
        finally:
            game.find_floor_pos = old_find_floor_pos
            rogue.MAP_W = old_map_w
            rogue.MAP_H = old_map_h

        self.assertEqual(len(calls), 3)

    def test_rogue_544_wanderer_floor_candidates_skip_plain_corridors(self):
        # Rogue 5.4.4 monsters.c:wanderer() uses rooms.c:find_floor(NULL), which picks a room.
        game = new_game(seed=340)
        set_two_room_floor(game)
        game.tm[12][12] = rogue.T_CORR

        cands = game.wanderer_floor_candidates()

        self.assertIn((22, 4), cands)
        self.assertNotIn((20, 1), cands)
        self.assertNotIn((12, 12), cands)

    def test_rogue_544_wanderer_floor_candidates_allow_room_stairs_and_traps(self):
        # Rogue 5.4.4 monsters.c:wanderer() uses rooms.c:find_floor(..., monst=TRUE), which accepts step_ok().
        game = new_game(seed=341)
        room_a, room_b = set_two_room_floor(game)
        game.p.x, game.p.y = room_a.x + 2, room_a.y + 2
        stair = (room_b.x + 2, room_b.y + 2)
        trap = (room_b.x + 3, room_b.y + 2)
        game.tm[stair[1]][stair[0]] = rogue.T_STAIR
        game.tm[trap[1]][trap[0]] = rogue.T_TRAP

        cands = game.wanderer_floor_candidates()

        self.assertIn(stair, cands)
        self.assertIn(trap, cands)

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
        self.assertEqual([s["worth"] for s in rogue.SCROLLS],
                         [140, 150, 180, 5, 160, 80, 80, 80, 100, 115, 200, 60, 165, 150, 75, 105, 20, 250])

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
        self.assertEqual((damage, hplus, dplus), ("2x4", 3, 4))

        game.p.wpn = next(it for it in game.p.inv if it.cat == rogue.CAT_WPN and it.kind == 2)
        thrown = rogue.Item(rogue.CAT_WPN, 3, hit_plus=0, dam_plus=0)
        damage, hplus, dplus = game.player_weapon_profile(thrown, thrown=True)
        self.assertEqual((damage, hplus, dplus), ("2x3", 1, 0))

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

    def test_rogue_544_see_invisible_potion_while_wearing_ring_does_not_start_unsee(self):
        # Rogue 5.4.4 rings.c:ring_on() sets CANSEE; potions.c:do_pot(P_SEEINVIS) then lengthens no fuse.
        import rogue_rings

        game = new_game(seed=5034)
        potion_kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "see invisible")
        potion = rogue.Item(rogue.CAT_POT, potion_kind)
        game.p.inv.append(potion)
        game.p.ring_l = rogue.Item(rogue.CAT_RING, rogue_rings.R_SEEINVIS)

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 7
            game.use_pot(potion)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(game.p.see_invisible, 0)
        self.assertEqual(game.fuses.remaining("unsee"), 0)

    def test_rogue_544_taking_off_see_invisible_ring_extinguishes_unsee(self):
        # Rogue 5.4.4 things.c:dropcheck() calls unsee(); extinguish(unsee) for R_SEEINVIS.
        import rogue_rings

        game = new_game(seed=5035)
        ring = rogue.Item(rogue.CAT_RING, rogue_rings.R_SEEINVIS)
        game.p.inv.append(ring)
        game.p.ring_l = ring
        game.p.see_invisible = 20
        game.fuses.fuse("unsee", 20, rogue.rogue_daemons.AFTER)

        game.takeoff(ring)

        self.assertEqual(game.p.see_invisible, 0)
        self.assertEqual(game.fuses.remaining("unsee"), 0)

    def test_rogue_544_taking_off_unworn_ring_spends_turn(self):
        # Rogue 5.4.4 rings.c:ring_off() says "not wearing such a ring" without clearing after.
        import rogue_rings

        game = new_game(seed=5045)
        ring = rogue.Item(rogue.CAT_RING, rogue_rings.R_REGEN)
        game.p.inv.append(ring)
        game.cact = "Take off"
        game.fitems = [ring]
        game.icur = 0
        turn = game.turn

        game.item_confirm()

        self.assertIsNone(game.p.ring_l)
        self.assertIsNone(game.p.ring_r)
        self.assertEqual(game.turn, turn + 1)
        self.assertIn("not wearing such a ring", game.msgs)

    def test_rogue_544_taking_off_cursed_ring_spends_turn(self):
        # Rogue 5.4.4 rings.c:ring_off() uses things.c:dropcheck(), which does not clear after.
        import rogue_rings

        game = new_game(seed=5046)
        ring = rogue.Item(rogue.CAT_RING, rogue_rings.R_REGEN, cursed=True)
        game.p.inv.append(ring)
        game.p.ring_l = ring
        game.cact = "Take off"
        game.fitems = [ring]
        game.icur = 0
        turn = game.turn

        game.item_confirm()

        self.assertIs(game.p.ring_l, ring)
        self.assertEqual(game.turn, turn + 1)
        self.assertIn("appears to be cursed", game.msgs[-1])

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

    def test_rogue_544_quaff_clears_guess_when_potion_becomes_known(self):
        # Rogue 5.4.4 potions.c:quaff() calls misc.c:call_it(), which clears oi_guess if oi_know.
        game = new_game(seed=3181)
        set_open_floor(game)
        kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "healing")
        potion = rogue.Item(rogue.CAT_POT, kind)
        game.p.inv.append(potion)
        game.ident.pk[kind] = False
        game.ident.pg[kind] = "old guess"

        game.use_pot(potion)

        self.assertTrue(game.ident.pk[kind])
        self.assertIsNone(game.ident.pg[kind])

    def test_rogue_544_quaff_preserves_guess_when_potion_remains_unknown(self):
        # Rogue 5.4.4 misc.c:call_it() leaves an existing oi_guess when oi_know is false.
        game = new_game(seed=3182)
        set_open_floor(game)
        kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "monster detection")
        potion = rogue.Item(rogue.CAT_POT, kind)
        game.p.inv.append(potion)
        game.ident.pk[kind] = False
        game.ident.pg[kind] = "old guess"

        game.use_pot(potion)

        self.assertFalse(game.ident.pk[kind])
        self.assertEqual(game.ident.pg[kind], "old guess")

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

    def test_rogue_544_monster_detection_visible_monsters_use_feeling_message(self):
        # Rogue 5.4.4 potions.c:turn_see(FALSE) reports add_new only for monsters not already see_monst().
        game = new_game(seed=320)
        set_open_floor(game)
        kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "monster detection")
        potion = rogue.Item(rogue.CAT_POT, kind)
        game.p.inv.append(potion)
        monster = monster_at(game.p.x + 1, game.p.y, "O", "orc")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}

        game.use_pot(potion)

        self.assertIn("you have a strange feeling for a moment, then it passes", game.msgs)
        self.assertNotIn("You sense monsters.", game.msgs)

    def test_rogue_544_monster_detection_unseen_room_monster_senses_monsters(self):
        # Rogue 5.4.4 potions.c:turn_see(FALSE) sets add_new when chase.c:see_monst() is false.
        game = new_game(seed=3201)
        room_a, room_b = set_two_room_floor(game)
        kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "monster detection")
        potion = rogue.Item(rogue.CAT_POT, kind)
        game.p.inv.append(potion)
        monster = monster_at(room_b.x + 1, room_b.y + 1, "O", "orc")
        game.mons = [monster]
        game.visible = {(room_a.x + 1, room_a.y + 1)}

        game.use_pot(potion)

        self.assertIn("You sense monsters.", game.msgs)
        self.assertNotIn("you have a strange feeling for a moment, then it passes", game.msgs)

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

    def test_rogue_544_magic_detection_skips_monster_pack_when_no_level_objects(self):
        # Rogue 5.4.4 potions.c:P_TFIND scans monster packs only inside the lvl_obj != NULL block.
        import rogue_rings

        game = new_game(seed=323)
        set_open_floor(game)
        kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "magic detection")
        potion = rogue.Item(rogue.CAT_POT, kind)
        monster = monster_at(game.p.x + 4, game.p.y)
        monster.pack = [rogue.Item(rogue.CAT_RING, rogue_rings.R_PROTECT)]
        game.p.inv.append(potion)
        game.gitems = []
        game.mons = [monster]
        game.visible = set()
        game.explored = set()

        game.use_pot(potion)

        self.assertFalse(game.ident.pk[kind])
        self.assertNotIn((monster.x, monster.y), game.visible)
        self.assertIn("you have a strange feeling for a moment, then it passes", game.msgs)

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

    def test_rogue_544_magic_detection_ignores_plain_monster_pack_weapon(self):
        # Rogue 5.4.4 potions.c:P_TFIND uses is_magic(), so plain weapons in monster packs do not glow.
        game = new_game(seed=322)
        set_open_floor(game)
        kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "magic detection")
        potion = rogue.Item(rogue.CAT_POT, kind)
        monster = monster_at(game.p.x + 4, game.p.y)
        monster.pack = [rogue.Item(rogue.CAT_WPN, 0, hit_plus=0, dam_plus=0)]
        game.p.inv.append(potion)
        game.mons = [monster]
        game.visible = set()
        game.explored = set()

        game.use_pot(potion)

        self.assertFalse(game.ident.pk[kind])
        self.assertNotIn((monster.x, monster.y), game.visible)

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

    def test_rogue_544_new_blindness_potion_refreshes_look_to_hero_only(self):
        # Rogue 5.4.4 potions.c:do_pot(P_BLIND) calls look(FALSE) after setting ISBLIND.
        game = new_game(seed=346)
        room = rogue.Room(5, 5, 8, 6)
        game.rooms = [room]
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        rogue.DGen._room(game.tm, room)
        game.p.x, game.p.y = room.x + 2, room.y + 2
        game.visible = {(x, y) for y in range(room.y, room.y + room.h) for x in range(room.x, room.x + room.w)}
        game.explored = set(game.visible)
        potion_kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "blindness")

        game.use_pot(rogue.Item(rogue.CAT_POT, potion_kind))

        self.assertEqual(game.visible, {(game.p.x, game.p.y)})

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

    def test_rogue_544_daemon_table_reuses_first_empty_slot(self):
        # Rogue 5.4.4 daemon.c:d_slot() reuses the first EMPTY slot.
        import rogue_daemons

        daemons = rogue_daemons.DaemonList()
        daemons.start("first", rogue_daemons.AFTER)
        daemons.start("second", rogue_daemons.AFTER)
        daemons.kill("first")
        daemons.start("third", rogue_daemons.AFTER)

        self.assertEqual(daemons.tick(rogue_daemons.AFTER), ["third", "second"])

    def test_rogue_544_do_daemons_runs_each_daemon_immediately(self):
        # Rogue 5.4.4 daemon.c:do_daemons() skips slots killed by an earlier daemon.
        import rogue_daemons

        daemons = rogue_daemons.DaemonList()
        fired = []
        daemons.start("first", rogue_daemons.AFTER)
        daemons.start("second", rogue_daemons.AFTER)

        def run(name):
            fired.append(name)
            if name == "first":
                daemons.kill("second")

        daemons.tick_each(rogue_daemons.AFTER, run)

        self.assertEqual(fired, ["first"])
        self.assertFalse(daemons.running("second"))

    def test_rogue_544_do_daemons_does_not_run_daemon_started_in_current_slot(self):
        # Rogue 5.4.4 daemon.c:do_daemons() does not clear the current daemon slot before callback.
        import rogue_daemons

        daemons = rogue_daemons.DaemonList()
        fired = []
        daemons.start("first", rogue_daemons.BEFORE)
        daemons.start("second", rogue_daemons.BEFORE)

        def run(name):
            fired.append(name)
            if name == "first":
                daemons.kill("first")
                daemons.start("third", rogue_daemons.BEFORE)

        daemons.tick_each(rogue_daemons.BEFORE, run)

        self.assertEqual(fired, ["first", "second"])
        self.assertEqual(daemons.tick(rogue_daemons.BEFORE), ["third", "second"])

    def test_rogue_544_do_daemons_runs_daemon_started_in_later_empty_slot(self):
        # Rogue 5.4.4 daemon.c:do_daemons() scans d_list slots live, so new later slots can run.
        import rogue_daemons

        daemons = rogue_daemons.DaemonList()
        fired = []
        daemons.start("first", rogue_daemons.BEFORE)

        def run(name):
            fired.append(name)
            if name == "first":
                daemons.start("second", rogue_daemons.BEFORE)

        daemons.tick_each(rogue_daemons.BEFORE, run)

        self.assertEqual(fired, ["first", "second"])

    def test_rogue_544_do_daemons_skips_reused_current_slot_but_runs_new_later_slot(self):
        # Rogue 5.4.4 daemon.c:do_daemons() advances past the current slot after callback.
        import rogue_daemons

        daemons = rogue_daemons.DaemonList()
        fired = []
        daemons.start("first", rogue_daemons.BEFORE)

        def run(name):
            fired.append(name)
            if name == "first":
                daemons.kill("first")
                daemons.start("current", rogue_daemons.BEFORE)
                daemons.start("later", rogue_daemons.BEFORE)

        daemons.tick_each(rogue_daemons.BEFORE, run)

        self.assertEqual(fired, ["first", "later"])
        self.assertEqual(daemons.tick(rogue_daemons.BEFORE), ["current", "later"])

    def test_rogue_544_fuse_table_keeps_duplicate_slots(self):
        # Rogue 5.4.4 daemon.c:fuse()/extinguish() use slots, not a unique map.
        import rogue_daemons

        fuses = rogue_daemons.FuseList()
        fuses.fuse("swander", 1, rogue_daemons.BEFORE)
        fuses.fuse("swander", 1, rogue_daemons.BEFORE)
        fuses.extinguish("swander")

        self.assertEqual(fuses.tick(rogue_daemons.BEFORE), ["swander"])

    def test_rogue_544_fuse_table_reuses_first_empty_slot(self):
        # Rogue 5.4.4 daemon.c:d_slot() reuses the first EMPTY slot for fuses.
        import rogue_daemons

        fuses = rogue_daemons.FuseList()
        fuses.fuse("first", 1, rogue_daemons.AFTER)
        fuses.fuse("second", 1, rogue_daemons.AFTER)
        fuses.extinguish("first")
        fuses.fuse("third", 1, rogue_daemons.AFTER)

        self.assertEqual(fuses.tick(rogue_daemons.AFTER), ["third", "second"])

    def test_rogue_544_do_fuses_runs_each_fuse_immediately(self):
        # Rogue 5.4.4 daemon.c:do_fuses() empties and calls each fuse immediately.
        import rogue_daemons

        fuses = rogue_daemons.FuseList()
        fired = []
        fuses.fuse("first", 1, rogue_daemons.AFTER)
        fuses.fuse("second", 1, rogue_daemons.AFTER)

        def run(name):
            fired.append(name)
            if name == "first":
                fuses.extinguish("second")

        fuses.tick_each(rogue_daemons.AFTER, run)

        self.assertEqual(fired, ["first"])
        self.assertEqual(fuses.remaining("second"), 0)

    def test_rogue_544_do_fuses_clears_slot_before_callback(self):
        # Rogue 5.4.4 daemon.c:do_fuses() sets the slot EMPTY before calling d_func.
        import rogue_daemons

        fuses = rogue_daemons.FuseList()
        fired = []
        fuses.fuse("first", 1, rogue_daemons.AFTER)
        fuses.fuse("second", 1, rogue_daemons.AFTER)

        def run(name):
            fired.append(name)
            if name == "first":
                fuses.fuse("third", 1, rogue_daemons.AFTER)

        fuses.tick_each(rogue_daemons.AFTER, run)

        self.assertEqual(fired, ["first", "second"])
        self.assertEqual(fuses.tick(rogue_daemons.AFTER), ["third"])

    def test_rogue_544_do_fuses_runs_new_later_slot_but_not_reused_current_slot(self):
        # Rogue 5.4.4 daemon.c:do_fuses() scans d_list live after clearing the current slot.
        import rogue_daemons

        fuses = rogue_daemons.FuseList()
        fired = []
        fuses.fuse("first", 1, rogue_daemons.AFTER)

        def run(name):
            fired.append(name)
            if name == "first":
                fuses.fuse("current", 1, rogue_daemons.AFTER)
                fuses.fuse("later", 1, rogue_daemons.AFTER)

        fuses.tick_each(rogue_daemons.AFTER, run)

        self.assertEqual(fired, ["first", "later"])
        self.assertEqual(fuses.tick(rogue_daemons.AFTER), ["current"])

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

    def test_rogue_544_new_level_does_not_reset_wandering_daemon_state(self):
        # Rogue 5.4.4 main.c starts swander after the first new_level(); new_level.c does not reset it.
        game = new_game(seed=326)
        game.fuses.extinguish("swander")
        game.daemons.start("rollwand", rogue.rogue_daemons.BEFORE)
        game.wander_between = 2

        game.descend()

        self.assertTrue(game.daemons.running("rollwand", rogue.rogue_daemons.BEFORE))
        self.assertEqual(game.fuses.remaining("swander"), 0)
        self.assertEqual(game.wander_between, 2)

    def test_rogue_544_new_level_clears_flytrap_hold(self):
        # Rogue 5.4.4 new_level.c:new_level() clears player ISHELD before generating the level.
        game = new_game(seed=327)
        set_open_floor(game)
        flytrap = monster_at(game.p.x + 1, game.p.y, "F", "venus flytrap", flags="hold")
        game.p.held_by = flytrap
        game.mons = [flytrap]

        game.descend()

        self.assertIsNone(game.p.held_by)

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

    def test_rogue_544_chase_helper_move_monst_does_not_apply_held_gate(self):
        # Rogue 5.4.4 chase.c:move_monst() does not check ISHELD; runners() owns that gate.
        import rogue_chase

        monster = monster_at(3, 1)
        monster.held = 2
        calls = []

        rogue_chase.move_monst(
            monster,
            lambda m: calls.append(m) or 0,
            lambda m: 1,
            lambda m: None,
        )

        self.assertEqual(calls, [monster])
        self.assertEqual(monster.held, 2)

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
        self.assertIs(rogue_chase.roomin(16, 8, [room]), room)
        self.assertIs(rogue_chase.roomin(16, 9, [room]), room)
        self.assertIsNone(rogue_chase.roomin(17, 9, [room]))

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

    def test_rogue_544_game_find_dest_records_item_destination_coord(self):
        # Rogue 5.4.4 chase.c:find_dest() stores t_dest as the chosen object position.
        game = new_game(seed=509)
        set_two_room_floor(game)
        monster = monster_at(22, 4, "C", "centaur", hp=10, armor=100, exp=5)
        item = rogue.Item(rogue.CAT_POT, 0)
        item.x, item.y = 24, 4
        game.mons = [monster]
        game.gitems = [item]
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 0
            dest = game.find_dest(monster)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(dest, (24, 4))
        self.assertEqual(monster.dest, (24, 4))

    def test_rogue_544_game_find_dest_skips_other_monster_destination(self):
        # Rogue 5.4.4 chase.c:find_dest() skips lvl_obj positions already used as another t_dest.
        game = new_game(seed=511)
        set_two_room_floor(game)
        claimed = rogue.Item(rogue.CAT_POT, 0)
        claimed.x, claimed.y = 24, 4
        target = rogue.Item(rogue.CAT_POT, 1)
        target.x, target.y = 25, 4
        first = monster_at(22, 4, "C", "centaur", hp=10, armor=100, exp=5)
        first.dest = (24, 4)
        second = monster_at(23, 4, "N", "nymph", hp=10, armor=100, exp=5)
        game.mons = [first, second]
        game.gitems = [claimed, target]
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 0
            dest = game.find_dest(second)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(dest, (25, 4))
        self.assertEqual(second.dest, (25, 4))

    def test_rogue_544_game_find_dest_treats_own_destination_as_claimed(self):
        # Rogue 5.4.4 chase.c:find_dest() scans mlist including the caller's current t_dest.
        game = new_game(seed=527)
        set_two_room_floor(game)
        claimed = rogue.Item(rogue.CAT_POT, 0)
        claimed.x, claimed.y = 24, 4
        target = rogue.Item(rogue.CAT_POT, 1)
        target.x, target.y = 25, 4
        monster = monster_at(22, 4, "C", "centaur", hp=10, armor=100, exp=5)
        monster.dest = (24, 4)
        game.mons = [monster]
        game.gitems = [claimed, target]
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 0
            dest = game.find_dest(monster)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(dest, (25, 4))
        self.assertEqual(monster.dest, (25, 4))

    def test_rogue_544_game_find_dest_includes_room_gold_for_carry_monsters(self):
        # Rogue 5.4.4 rooms.c:do_rooms() attaches GOLD to lvl_obj; chase.c:find_dest() skips only S_SCARE.
        game = new_game(seed=514)
        set_two_room_floor(game)
        gold = rogue.Item(rogue.CAT_GOLD, 0)
        gold.x, gold.y = 24, 4
        potion = rogue.Item(rogue.CAT_POT, 0)
        potion.x, potion.y = 25, 4
        monster = monster_at(22, 4, "C", "centaur", hp=10, armor=100, exp=5)
        game.mons = [monster]
        game.gitems = [gold, potion]
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 0
            dest = game.find_dest(monster)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(dest, (24, 4))
        self.assertEqual(monster.dest, (24, 4))

    def test_rogue_544_aggravate_uses_runto_find_dest_for_carry_monster(self):
        # Rogue 5.4.4 misc.c:aggravate() calls chase.c:runto(), which sets t_dest = find_dest().
        game = new_game(seed=512)
        set_two_room_floor(game)
        monster = monster_at(22, 4, "C", "centaur", hp=10, armor=100, exp=5)
        item = rogue.Item(rogue.CAT_POT, 0)
        item.x, item.y = 24, 4
        game.mons = [monster]
        game.gitems = [item]
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 0
            game.aggravate_monsters()
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertTrue(monster.running)
        self.assertEqual(monster.dest, (24, 4))

    def test_rogue_544_do_chase_preserves_existing_hero_destination_for_carry_monster(self):
        # Rogue 5.4.4 chase.c:do_chase() uses existing t_dest; it does not call find_dest() every turn.
        game = new_game(seed=516)
        set_two_room_floor(game)
        monster = monster_at(22, 4, "C", "centaur", hp=10, armor=100, exp=5)
        monster.running = True
        monster.dest = rogue.DEST_PLAYER
        item = rogue.Item(rogue.CAT_POT, 0)
        item.x, item.y = 24, 4
        game.mons = [monster]
        game.gitems = [item]
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 0
            game.do_chase(monster)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(monster.dest, rogue.DEST_PLAYER)

    def test_rogue_544_do_chase_collects_reached_item_destination(self):
        # Rogue 5.4.4 chase.c:do_chase() moves reached lvl_obj into the monster pack.
        game = new_game(seed=510)
        set_two_room_floor(game)
        monster = monster_at(23, 4, "C", "centaur", hp=10, armor=100, exp=5)
        monster.running = True
        monster.dest = (24, 4)
        item = rogue.Item(rogue.CAT_POT, 0)
        item.x, item.y = 24, 4
        game.mons = [monster]
        game.gitems = [item]
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 0
            game.do_chase(monster)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual((monster.x, monster.y), (24, 4))
        self.assertNotIn(item, game.gitems)
        self.assertIn(item, monster.pack)
        self.assertEqual(monster.dest, rogue.DEST_PLAYER)

    def test_rogue_544_do_chase_keeps_stale_item_destination_until_reached(self):
        # Rogue 5.4.4 chase.c:do_chase() does not validate t_dest against lvl_obj before chase().
        game = new_game(seed=525)
        set_two_room_floor(game)
        game.p.x, game.p.y = 3, 4
        monster = monster_at(23, 4, "C", "centaur", hp=10, armor=100, exp=5)
        monster.running = True
        monster.dest = (24, 4)
        game.mons = [monster]
        game.gitems = []

        game.do_chase(monster)

        self.assertEqual((monster.x, monster.y), (24, 4))
        self.assertEqual(monster.dest, (24, 4))
        self.assertFalse(monster.running)

    def test_rogue_544_do_chase_greedy_stale_gold_destination_falls_back_to_hero(self):
        # Rogue 5.4.4 chase.c:do_chase() sends ISGREED monsters after hero when rer->r_goldval is 0.
        game = new_game(seed=526)
        set_two_room_floor(game)
        game.p.x, game.p.y = 3, 4
        monster = monster_at(23, 4, "O", "orc", hp=10, armor=100, exp=5, flags="greed")
        monster.running = True
        monster.dest = (24, 4)
        game.mons = [monster]
        game.gitems = []

        game.do_chase(monster)

        self.assertEqual((monster.x, monster.y), (22, 4))
        self.assertEqual(monster.dest, rogue.DEST_PLAYER)

    def test_rogue_544_do_chase_collecting_maze_item_restores_floor_tile(self):
        # Rogue 5.4.4 chase.c:do_chase() restores chat(obj->o_pos) to
        # FLOOR unless th->t_room has ISGONE, even when the item was on PASSAGE.
        game = new_game(seed=5101)
        room = rogue.Room(5, 5, 7, 7, flags={rogue.ROOM_MAZE})
        game.rooms = [room]
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for y in range(room.y + 1, room.y + room.h - 1):
            for x in range(room.x + 1, room.x + room.w - 1):
                game.tm[y][x] = rogue.T_CORR
        game.p.x, game.p.y = 20, 20
        game.tm[20][20] = rogue.T_FLOOR
        monster = monster_at(7, 7, "C", "centaur", hp=10, armor=100, exp=5)
        monster.running = True
        monster.dest = (8, 7)
        item = rogue.Item(rogue.CAT_POT, 0)
        item.x, item.y = monster.dest
        game.mons = [monster]
        game.gitems = [item]

        game.do_chase(monster)

        self.assertEqual((monster.x, monster.y), (8, 7))
        self.assertIn(item, monster.pack)
        self.assertEqual(game.tm[7][8], rogue.T_FLOOR)

    def test_rogue_544_collected_maze_floor_keeps_passage_identity_for_ai(self):
        # Rogue 5.4.4 chase.c:roomin() uses F_PASS before room bounds, so a
        # maze passage whose display char was restored to FLOOR remains in the passage.
        game = new_game(seed=5102)
        room = rogue.Room(5, 5, 7, 7, flags={rogue.ROOM_MAZE})
        game.rooms = [room]
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for y in range(room.y + 1, room.y + room.h - 1):
            for x in range(room.x + 1, room.x + room.w - 1):
                game.tm[y][x] = rogue.T_CORR
        monster = monster_at(7, 7, "C", "centaur", hp=10, armor=100, exp=5)
        monster.running = True
        monster.dest = (8, 7)
        first = rogue.Item(rogue.CAT_POT, 0)
        first.x, first.y = monster.dest
        second = rogue.Item(rogue.CAT_POT, 1)
        second.x, second.y = 9, 7
        game.mons = [monster]
        game.gitems = [first, second]

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 0
            game.do_chase(monster)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(game.tm[7][8], rogue.T_FLOOR)
        self.assertEqual(monster.dest, (9, 7))
        self.assertEqual(game.room_for_ai(monster.x, monster.y), game.room_for_ai(second.x, second.y))

    def test_rogue_544_do_chase_keeps_running_after_collecting_item_when_new_dest_differs(self):
        # Rogue 5.4.4 chase.c:do_chase() stops only if relocate() leaves the monster on the new t_dest.
        game = new_game(seed=515)
        set_two_room_floor(game)
        monster = monster_at(23, 4, "C", "centaur", hp=10, armor=100, exp=5)
        monster.running = True
        monster.dest = (24, 4)
        first = rogue.Item(rogue.CAT_POT, 0)
        first.x, first.y = 24, 4
        second = rogue.Item(rogue.CAT_POT, 1)
        second.x, second.y = 26, 4
        game.mons = [monster]
        game.gitems = [first, second]
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 0
            game.do_chase(monster)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual((monster.x, monster.y), (24, 4))
        self.assertIn(first, monster.pack)
        self.assertEqual(monster.dest, (26, 4))
        self.assertTrue(monster.running)

    def test_rogue_544_do_chase_collects_reached_gold_destination(self):
        # Rogue 5.4.4 chase.c:do_chase() attaches any reached lvl_obj, including GOLD, to t_pack.
        game = new_game(seed=513)
        set_two_room_floor(game)
        monster = monster_at(23, 4, "O", "orc", hp=10, armor=100, exp=5, flags="greed")
        monster.running = True
        monster.dest = (24, 4)
        gold = rogue.Item(rogue.CAT_GOLD, 0)
        gold.x, gold.y = 24, 4
        game.mons = [monster]
        game.gitems = [gold]

        game.do_chase(monster)

        self.assertEqual((monster.x, monster.y), (24, 4))
        self.assertNotIn(gold, game.gitems)
        self.assertIn(gold, monster.pack)
        self.assertEqual(monster.dest, rogue.DEST_PLAYER)

    def test_rogue_544_do_chase_venus_flytrap_does_not_relocate_while_chasing(self):
        # Rogue 5.4.4 chase.c:do_chase() returns before relocate() when chase() continues for 'F'.
        game = new_game(seed=517)
        set_open_floor(game)
        flytrap = monster_at(game.p.x + 3, game.p.y, "F", "venus flytrap", hp=10, damage="0x0", flags="hold")
        flytrap.running = True
        flytrap.dest = rogue.DEST_PLAYER
        game.mons = [flytrap]

        game.do_chase(flytrap)

        self.assertEqual((flytrap.x, flytrap.y), (game.p.x + 3, game.p.y))

    def test_rogue_544_do_chase_passage_chaser_aims_at_nearest_passage_exit(self):
        # Rogue 5.4.4 chase.c:do_chase() uses passages[F_PNUM].r_exit when chaser is in a passage.
        game = new_game(seed=519)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        room = rogue.Room(20, 5, 8, 8)
        game.rooms = [room]
        for y in range(room.y, room.y + room.h):
            for x in range(room.x, room.x + room.w):
                game.tm[y][x] = rogue.T_FLOOR
        for x in range(5, 16):
            game.tm[10][x] = rogue.T_CORR
        game.tm[10][5] = rogue.T_DOOR
        game.tm[10][15] = rogue.T_DOOR
        game.p.x, game.p.y = 23, 8
        monster = monster_at(10, 10, "H", "hobgoblin", hp=10)
        monster.running = True
        monster.dest = rogue.DEST_PLAYER
        game.mons = [monster]
        chased = []
        old_chase = game.chase
        try:
            game.chase = lambda m, dest: chased.append(dest) or "move"
            game.do_chase(monster)
        finally:
            game.chase = old_chase

        self.assertEqual(chased, [(15, 10)])

    def test_rogue_544_do_chase_door_chaser_keeps_room_exit_candidate(self):
        # Rogue 5.4.4 chase.c:do_chase() checks th->t_room exits before
        # switching a door chaser to passages[F_PNUM], without resetting mindist.
        game = new_game(seed=523)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        room = rogue.Room(10, 5, 10, 8)
        target_room = rogue.Room(24, 5, 8, 8)
        game.rooms = [room, target_room]
        for r in game.rooms:
            for y in range(r.y, r.y + r.h):
                for x in range(r.x, r.x + r.w):
                    game.tm[y][x] = rogue.T_FLOOR
        left_door = (room.x, 8)
        right_door = (room.x + room.w - 1, 8)
        game.tm[left_door[1]][left_door[0]] = rogue.T_DOOR
        game.tm[right_door[1]][right_door[0]] = rogue.T_DOOR
        for x in range(5, left_door[0]):
            game.tm[8][x] = rogue.T_CORR
        game.tm[8][5] = rogue.T_DOOR
        game.p.x, game.p.y = target_room.x + 2, 8
        monster = monster_at(left_door[0], left_door[1], "H", "hobgoblin", hp=10)
        monster.running = True
        monster.dest = rogue.DEST_PLAYER
        game.mons = [monster]
        chased = []
        old_chase = game.chase
        try:
            game.chase = lambda m, dest: chased.append(dest) or "move"
            game.do_chase(monster)
        finally:
            game.chase = old_chase

        self.assertEqual(chased, [right_door])

    def test_rogue_544_room_exits_include_hidden_secret_doors(self):
        # Rogue 5.4.4 passages.c:door() stores secret doors in room.r_exit before hiding them.
        game = new_game(seed=522)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        room = rogue.Room(10, 5, 8, 8)
        game.rooms = [room]
        for y in range(room.y, room.y + room.h):
            for x in range(room.x, room.x + room.w):
                game.tm[y][x] = rogue.T_FLOOR
        game.tm[9][room.x + room.w - 1] = rogue.T_VWALL
        game.hidden_tiles[(room.x + room.w - 1, 9)] = rogue.T_DOOR
        game.p.x, game.p.y = 25, 9
        monster = monster_at(12, 9, "H", "hobgoblin", hp=10)
        monster.running = True
        monster.dest = rogue.DEST_PLAYER
        game.mons = [monster]
        chased = []
        old_chase = game.chase
        try:
            game.chase = lambda m, dest: chased.append(dest) or "move"
            game.do_chase(monster)
        finally:
            game.chase = old_chase

        self.assertEqual(chased, [(room.x + room.w - 1, 9)])

    def test_rogue_544_passage_component_includes_hidden_passage_cells(self):
        # Rogue 5.4.4 passages.c:putpass()/numpass() keep hidden passages as F_PASS.
        game = new_game(seed=520)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        game.rooms = []
        for x in (5, 7):
            game.tm[10][x] = rogue.T_CORR
        game.hidden_tiles[(6, 10)] = rogue.T_CORR

        component = game.passage_component(5, 10)

        self.assertIn((5, 10), component[1])
        self.assertIn((6, 10), component[1])
        self.assertIn((7, 10), component[1])

    def test_rogue_544_passage_exits_include_hidden_secret_doors(self):
        # Rogue 5.4.4 passages.c:numpass() records non-F_REAL '|'/'-' as passage exits.
        game = new_game(seed=521)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        game.rooms = []
        game.tm[10][5] = rogue.T_CORR
        game.tm[10][6] = rogue.T_HWALL
        game.hidden_tiles[(6, 10)] = rogue.T_DOOR

        passage = game.passage_component(5, 10)

        self.assertIn((6, 10), game.passage_exits(passage))

    def test_rogue_544_passage_exits_keep_numpass_traversal_order(self):
        # Rogue 5.4.4 passages.c:numpass() stores exits during down/up/right/left recursion.
        game = new_game(seed=522)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        game.rooms = []
        game.tm[10][10] = rogue.T_CORR
        for x, y in ((10, 11), (10, 9), (11, 10), (9, 10)):
            game.tm[y][x] = rogue.T_DOOR

        passage = game.passage_component(10, 10)

        self.assertEqual(game.passage_exits(passage), [(10, 11), (10, 9), (11, 10), (9, 10)])

    def test_rogue_544_passage_exits_use_passnum_room_exit_root(self):
        # Rogue 5.4.4 passages.c:passnum() starts numpass() from rooms[].r_exit order.
        game = new_game(seed=523)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        game.rooms = [rogue.Room(0, 0, 4, 4)]
        game.rooms[0].exits = [(9, 10)]
        game.tm[10][10] = rogue.T_CORR
        for x, y in ((10, 11), (10, 9), (11, 10), (9, 10)):
            game.tm[y][x] = rogue.T_DOOR

        passage = game.passage_component(10, 10)

        self.assertEqual(game.passage_exits(passage), [(9, 10), (10, 11), (10, 9), (11, 10)])

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

    def test_rogue_544_taking_off_armor_wastes_time_for_doctor(self):
        # Rogue 5.4.4 armor.c:take_off() goes through things.c:dropcheck() -> waste_time().
        game = new_game(seed=5036)
        game.daemons.kill("runners")
        game.daemons.kill("stomach")
        armor = rogue.Item(rogue.CAT_ARM, 0)
        game.p.inv.append(armor)
        game.p.arm = armor
        game.p.level = 1
        game.p.hp = game.p.max_hp - 1
        game.p.quiet = 19

        game.takeoff(armor)

        self.assertIsNone(game.p.arm)
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

    def test_rogue_544_daemons_helper_doctor_natural_heal_delta_matches_source(self):
        # Rogue 5.4.4 daemons.c:doctor() low/high level natural heal branches.
        calls = []

        self.assertEqual(rogue.rogue_daemons.doctor_natural_heal_delta(1, 18, lambda n: 99), 0)
        self.assertEqual(rogue.rogue_daemons.doctor_natural_heal_delta(1, 19, lambda n: 99), 1)
        self.assertEqual(
            rogue.rogue_daemons.doctor_natural_heal_delta(10, 3, lambda n: calls.append(n) or 2),
            3,
        )
        self.assertEqual(calls, [3])

    def test_rogue_544_daemons_helper_doctor_finalize_caps_and_resets_on_hp_change(self):
        # Rogue 5.4.4 daemons.c:doctor() caps to max_hp and clears quiet only if HP changed.
        self.assertEqual(rogue.rogue_daemons.doctor_finalize_hp(12, 13, 12, 19), (12, 0))
        self.assertEqual(rogue.rogue_daemons.doctor_finalize_hp(12, 12, 12, 19), (12, 19))

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

    def test_rogue_544_daemons_helper_stomach_does_not_reset_state_without_threshold_cross(self):
        # Rogue 5.4.4 daemons.c:stomach() only changes hungry_state when crossing thresholds.
        player = rogue.Player()
        player.food = rogue.MORETIME + 10
        player.state = "hungry"

        msg = rogue.rogue_daemons.stomach_tick(
            player,
            SequenceRng([]),
            food_cost=0,
            moretime=rogue.MORETIME,
            starvetime=rogue.STARVETIME,
        )

        self.assertIsNone(msg)
        self.assertEqual(player.food, rogue.MORETIME + 10)
        self.assertEqual(player.state, "hungry")

    def test_rogue_544_daemons_helper_stomach_stops_running_only_on_state_change(self):
        # Rogue 5.4.4 daemons.c:stomach() clears running only when hungry_state changes.
        self.assertTrue(rogue.rogue_daemons.stomach_stops_running("normal", "hungry"))
        self.assertFalse(rogue.rogue_daemons.stomach_stops_running("hungry", "hungry"))

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

    def test_rogue_544_daemons_helper_stomach_faint_duration_matches_source(self):
        # Rogue 5.4.4 daemons.c:stomach() uses no_command += rnd(8) + 4.
        calls = []

        self.assertEqual(rogue.rogue_daemons.stomach_faint_duration(lambda n: calls.append(n) or 7), 11)
        self.assertEqual(calls, [8])

    def test_rogue_544_daemons_helper_stomach_starvation_tick_matches_postdecrement(self):
        # Rogue 5.4.4 daemons.c:stomach() checks food_left-- < -STARVETIME.
        self.assertEqual(
            rogue.rogue_daemons.stomach_starvation_tick(-rogue.STARVETIME - 1, rogue.STARVETIME),
            (-rogue.STARVETIME - 2, True),
        )
        self.assertEqual(
            rogue.rogue_daemons.stomach_starvation_tick(-rogue.STARVETIME, rogue.STARVETIME),
            (-rogue.STARVETIME - 1, False),
        )

    def test_rogue_544_daemons_helper_stomach_digest_tick_subtracts_food_cost(self):
        # Rogue 5.4.4 daemons.c:stomach() subtracts ring_eat + ring_eat + 1 - amulet.
        self.assertEqual(rogue.rogue_daemons.stomach_digest_tick(100, 3), 97)
        self.assertEqual(rogue.rogue_daemons.stomach_digest_tick(1, 2), -1)

    def test_rogue_544_daemons_helper_stomach_threshold_check_after_digest_even_below_zero(self):
        # Rogue 5.4.4 daemons.c:stomach() checks MORETIME thresholds after food_left subtraction.
        player = rogue.Player()
        player.food = rogue.MORETIME
        player.state = "normal"

        msg = rogue.rogue_daemons.stomach_tick(
            player,
            SequenceRng([]),
            food_cost=rogue.MORETIME + 1,
            moretime=rogue.MORETIME,
            starvetime=rogue.STARVETIME,
        )

        self.assertEqual(player.food, -1)
        self.assertEqual(player.state, "weak")
        self.assertEqual(msg, "pyxel.are_weak")

    def test_rogue_544_daemons_helper_stomach_hunger_state_uses_crossed_thresholds(self):
        # Rogue 5.4.4 daemons.c:stomach() uses oldfood/new food threshold crossings.
        self.assertEqual(
            rogue.rogue_daemons.stomach_hunger_state(rogue.MORETIME, rogue.MORETIME - 1, rogue.MORETIME),
            "weak",
        )
        self.assertEqual(
            rogue.rogue_daemons.stomach_hunger_state(2 * rogue.MORETIME, 2 * rogue.MORETIME - 1, rogue.MORETIME),
            "hungry",
        )
        self.assertIsNone(
            rogue.rogue_daemons.stomach_hunger_state(rogue.MORETIME + 10, rogue.MORETIME + 9, rogue.MORETIME)
        )

    def test_rogue_544_daemons_helper_unconfuse_message_value_matches_source(self):
        # Rogue 5.4.4 daemons.c:unconfuse() chooses "trippy" while hallucinating.
        self.assertEqual(rogue.rogue_daemons.unconfuse_message_value(hallucinating=True), "trippy")
        self.assertEqual(rogue.rogue_daemons.unconfuse_message_value(hallucinating=False), "confused")

    def test_rogue_544_daemons_helper_sight_result_matches_blind_gate_and_message(self):
        # Rogue 5.4.4 daemons.c:sight() only acts while ISBLIND and chooses LSD text while hallucinating.
        self.assertEqual(
            rogue.rogue_daemons.sight_result(blind=True, hallucinating=True),
            "daemons.far_out_everything_is_all_cosmic_again",
        )
        self.assertEqual(
            rogue.rogue_daemons.sight_result(blind=True, hallucinating=False),
            "daemons.the_veil_of_darkness_lifts",
        )
        self.assertIsNone(rogue.rogue_daemons.sight_result(blind=False, hallucinating=False))

    def test_rogue_544_daemons_helper_unsee_state_clears_cansee(self):
        # Rogue 5.4.4 daemons.c:unsee() clears CANSEE after repainting visible invisible monsters.
        self.assertEqual(rogue.rogue_daemons.unsee_state(), 0)

    def test_rogue_544_daemons_helper_nohaste_state_matches_source(self):
        # Rogue 5.4.4 daemons.c:nohaste() clears ISHASTE and reports slowing down.
        self.assertEqual(
            rogue.rogue_daemons.nohaste_state(),
            (0, False, "daemons.you_feel_yourself_slowing_down"),
        )

    def test_rogue_544_daemons_helper_come_down_result_matches_source(self):
        # Rogue 5.4.4 daemons.c:come_down() returns early if not hallucinating or while blind.
        self.assertEqual(rogue.rogue_daemons.come_down_result(hallucinating=False, blind=False), (False, None))
        self.assertEqual(rogue.rogue_daemons.come_down_result(hallucinating=True, blind=True), (True, None))
        self.assertEqual(
            rogue.rogue_daemons.come_down_result(hallucinating=True, blind=False),
            (True, "daemons.everything_looks_so_boring_now"),
        )

    def test_rogue_544_daemons_helper_land_state_matches_source(self):
        # Rogue 5.4.4 daemons.c:land() clears ISLEVIT and reports choose_str(pa_high, pa_straight).
        self.assertEqual(
            rogue.rogue_daemons.land_state(hallucinating=False),
            (0, "daemons.you_float_gently_to_the_ground"),
        )
        self.assertEqual(
            rogue.rogue_daemons.land_state(hallucinating=True),
            (0, "daemons.bummer_you_ve_hit_the_ground"),
        )

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

    def test_rogue_544_stomach_hunger_state_change_clears_running_count(self):
        # Rogue 5.4.4 daemons.c:stomach() clears ISRUN/running/count when hungry_state changes.
        game = new_game(seed=443)
        set_open_floor(game)
        game.p.food = rogue.MORETIME
        game.p.state = "normal"
        game.dashing = True
        game.dash_steps = 5

        game.run_stomach()

        self.assertFalse(game.dashing)
        self.assertEqual(game.dash_steps, 0)
        self.assertEqual(game.p.state, "weak")

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

    def test_rogue_544_run_stomach_does_not_reset_state_without_threshold_cross(self):
        # Rogue 5.4.4 daemons.c:stomach() leaves hungry_state unchanged without a threshold crossing.
        game = new_game(seed=5611)
        game.p.food = rogue.MORETIME + 10
        game.p.state = "hungry"
        game.p.ring_l = rogue.Item(rogue.CAT_RING, rogue.rogue_rings.R_DIGEST)
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 0
            game.run_stomach()
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(game.p.state, "hungry")

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

    def test_rogue_544_initial_daemon_fuse_slot_order_matches_main_c(self):
        # Rogue 5.4.4 main.c starts runners, doctor, swander fuse, then stomach in the shared d_list.
        game = new_game(seed=319)

        self.assertEqual(
            [
                (slot.get("kind"), slot.get("name"), slot.get("when"))
                for slot in game.delayed_actions._slots[:4]
            ],
            [
                ("daemon", "runners", rogue.rogue_daemons.AFTER),
                ("daemon", "doctor", rogue.rogue_daemons.AFTER),
                ("fuse", "swander", rogue.rogue_daemons.AFTER),
                ("daemon", "stomach", rogue.rogue_daemons.AFTER),
            ],
        )

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

    def test_rogue_544_rollwand_spreads_wandertime_only_on_success(self):
        # Rogue 5.4.4 daemons.c:rollwand() reaches WANDERTIME only after roll(1, 6) == 4.
        game = new_game(seed=313)
        old_roll = rogue.RNG.roll
        old_spread = rogue.RNG.spread
        try:
            rogue.RNG.spread = lambda n: (_ for _ in ()).throw(AssertionError("spread used early"))
            game.wander_between = 0
            game.roll_wanderer()
            self.assertEqual(game.wander_between, 1)

            rogue.RNG.roll = lambda number, sides: 1
            game.wander_between = 3
            game.roll_wanderer()
            self.assertEqual(game.wander_between, 0)
        finally:
            rogue.RNG.roll = old_roll
            rogue.RNG.spread = old_spread

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

    def test_rogue_544_hasted_no_command_decrements_on_both_command_iterations(self):
        # Rogue 5.4.4 command.c:command() sets ntimes++ for ISHASTE, then decrements no_command inside the loop.
        game = new_game(seed=321)
        game.daemons.kill("runners")
        game.daemons.kill("doctor")
        game.daemons.kill("stomach")
        game.p.haste = 5
        game.fuses.fuse("nohaste", 5, rogue.rogue_daemons.AFTER)
        game.p.no_command = 2
        turn = game.turn

        game.end_turn()

        self.assertEqual(game.p.no_command, 1)
        self.assertEqual(game.turn, turn)
        self.assertTrue(game.haste_half_turn)

        game.end_turn()

        self.assertEqual(game.p.no_command, 0)
        self.assertEqual(game.turn, turn + 1)
        self.assertIn("you can move again", game.msgs)

    def test_rogue_544_hasted_turn_runs_before_daemons_on_first_half_action(self):
        # Rogue 5.4.4 command.c:command() runs do_daemons(BEFORE) before the hasted two-action loop.
        game = new_game(seed=322)
        game.p.haste = 5
        seen = []
        game.daemons.start("rollwand", rogue.rogue_daemons.BEFORE)
        game.roll_wanderer = lambda: seen.append(game.turn)
        turn = game.turn

        game.end_turn()

        self.assertEqual(seen, [turn])
        self.assertEqual(game.turn, turn)
        self.assertTrue(game.haste_half_turn)

    def test_rogue_544_hasted_turn_runs_before_fuses_on_first_half_action(self):
        # Rogue 5.4.4 command.c:command() runs do_fuses(BEFORE) before the hasted two-action loop.
        game = new_game(seed=323)
        game.p.haste = 5
        seen = []
        game.fuses.fuse("swander", 1, rogue.rogue_daemons.BEFORE)
        game.swander = lambda: seen.append(game.turn)
        turn = game.turn

        game.end_turn()

        self.assertEqual(seen, [turn])
        self.assertEqual(game.turn, turn)
        self.assertTrue(game.haste_half_turn)

    def test_rogue_544_haste_self_does_not_spend_after_turn_from_item_confirm(self):
        # Rogue 5.4.4 potions.c:P_HASTE sets after=FALSE before add_haste(TRUE).
        game = new_game(seed=313)
        potion_kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "haste self")
        potion = rogue.Item(rogue.CAT_POT, potion_kind)
        game.p.inv.append(potion)
        game.cact = "Quaff"
        game.fitems = [potion]
        game.icur = 0
        old_rnd = rogue.RNG.rnd
        turn = game.turn
        try:
            rogue.RNG.rnd = lambda n: 1
            game.item_confirm()
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(game.turn, turn)
        self.assertFalse(game.haste_half_turn)

    def test_rogue_544_misc_helper_add_haste_potion_duration(self):
        # Rogue 5.4.4 misc.c:add_haste(TRUE) uses rnd(4)+4 for nohaste.
        import rogue_misc

        result = rogue_misc.add_haste_result(False, True, lambda n: 1)

        self.assertTrue(result.ok)
        self.assertEqual(result.duration, 5)
        self.assertEqual(result.no_command_add, 0)

    def test_rogue_544_misc_helper_add_haste_second_use_faints(self):
        # Rogue 5.4.4 misc.c:add_haste() adds rnd(8) no_command when already hasted.
        import rogue_misc

        result = rogue_misc.add_haste_result(True, True, lambda n: n - 1)

        self.assertFalse(result.ok)
        self.assertEqual(result.duration, 0)
        self.assertEqual(result.no_command_add, 7)

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

    def test_rogue_544_hallucinating_levitation_uses_high_message(self):
        # Rogue 5.4.4 potions.c:do_pot(P_LEVIT) prints choose_str(pa_high, pa_straight).
        game = new_game(seed=315)
        potion_kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "levitation")
        game.p.hallucinating = 10

        game.use_pot(rogue.Item(rogue.CAT_POT, potion_kind))

        self.assertIn("oh, wow!  You're floating in the air!", game.msgs)
        self.assertNotIn("you start to float in the air", game.msgs)

    def test_rogue_544_land_while_hallucinating_uses_high_message(self):
        # Rogue 5.4.4 daemons.c:land() uses choose_str("bummer!  You've hit the ground", ...).
        game = new_game(seed=316)
        game.p.levitating = 1
        game.p.hallucinating = 10

        game.land()

        self.assertEqual(game.p.levitating, 0)
        self.assertIn("bummer!  You've hit the ground", game.msgs)
        self.assertNotIn("you float gently to the ground", game.msgs)

    def test_rogue_544_legacy_levitation_counter_lands_with_high_message(self):
        # Rogue 5.4.4 daemons.c:land() message branch also applies if no land fuse is present.
        game = new_game(seed=317)
        game.daemons.kill("runners")
        game.daemons.kill("doctor")
        game.daemons.kill("stomach")
        game.p.levitating = 1
        game.p.hallucinating = 10

        game.end_turn()

        self.assertEqual(game.p.levitating, 0)
        self.assertIn("bummer!  You've hit the ground", game.msgs)
        self.assertNotIn("you float gently to the ground", game.msgs)

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

    def test_rogue_544_hallucination_starts_visuals_before_daemon(self):
        # Rogue 5.4.4 potions.c:P_LSD starts daemons.c:visuals as a BEFORE daemon on first trip.
        game = new_game(seed=2141)
        potion_kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "hallucination")
        potion = rogue.Item(rogue.CAT_POT, potion_kind)
        game.p.inv.append(potion)

        game.use_pot(potion)

        self.assertTrue(game.daemons.running("visuals", rogue.rogue_daemons.BEFORE))

    def test_rogue_544_come_down_kills_visuals_daemon(self):
        # Rogue 5.4.4 daemons.c:come_down() calls kill_daemon(visuals).
        game = new_game(seed=2142)
        game.p.hallucinating = 10
        game.daemons.start("visuals", rogue.rogue_daemons.BEFORE)
        game.hallu_item_syms = {1: "!"}

        game.come_down()

        self.assertFalse(game.daemons.running("visuals"))
        self.assertEqual(game.hallu_item_syms, {})

    def test_rogue_544_hallucination_preserves_detect_monster_display(self):
        # Rogue 5.4.4 potions.c:P_LSD calls turn_see(FALSE), which keeps SEEMONST on.
        game = new_game(seed=216)
        potion_kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "hallucination")
        potion = rogue.Item(rogue.CAT_POT, potion_kind)
        game.p.inv.append(potion)
        game.p.see_monsters = rogue.HUHDURATION
        game.fuses.fuse("turn_see", rogue.HUHDURATION, rogue.rogue_daemons.AFTER)

        game.use_pot(potion)

        self.assertEqual(game.p.see_monsters, rogue.HUHDURATION)
        self.assertEqual(game.fuses.remaining("turn_see"), rogue.HUHDURATION)

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

    def test_rogue_544_visuals_daemon_refreshes_hallucination_cache_in_source_order(self):
        # Rogue 5.4.4 daemons.c:visuals() randomizes visible objects, stairs, then monsters.
        game = new_game(seed=2161)
        set_open_floor(game)
        px, py = game.p.x, game.p.y
        potion = rogue.Item(rogue.CAT_POT, 0)
        potion.x, potion.y = px + 1, py
        game.gitems = [potion]
        visible_monster = monster_at(px + 2, py, "O", "orc")
        detected_monster = monster_at(px + 5, py, "B", "bat")
        game.mons = [visible_monster, detected_monster]
        game.tm[py][px - 1] = rogue.T_STAIR
        game.visible.update({(px + 1, py), (px + 2, py), (px - 1, py)})
        game.visible.discard((px + 5, py))
        game.p.hallucinating = 10
        game.p.see_monsters = 10
        rng = SequenceRng([1, 2, 3, 4])
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = rng.rnd
            game.run_visuals()
            rogue.RNG.rnd = lambda n: (_ for _ in ()).throw(AssertionError("draw-time RNG"))
            self.assertEqual(game.visible_item_sym(potion), rogue.HALLU_THINGS[1])
            self.assertEqual(game.visible_tile_sym(px - 1, py, rogue.T_STAIR), rogue.HALLU_THINGS[2])
            self.assertEqual(game.visible_monster_sym(visible_monster), "D")
            self.assertEqual(game.detected_monster_sym(detected_monster), "E")
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(rng.calls, [len(rogue.HALLU_THINGS) - 1, len(rogue.HALLU_THINGS) - 1, 26, 26])

    def test_rogue_544_visuals_blind_still_randomizes_detected_monsters(self):
        # Rogue 5.4.4 daemons.c:visuals() skips cansee() cells while blind but still uses SEEMONST.
        game = new_game(seed=2162)
        set_open_floor(game)
        px, py = game.p.x, game.p.y
        potion = rogue.Item(rogue.CAT_POT, 0)
        potion.x, potion.y = px + 1, py
        monster = monster_at(px + 5, py, "B", "bat")
        game.gitems = [potion]
        game.mons = [monster]
        game.visible.update({(px + 1, py)})
        game.p.hallucinating = 10
        game.p.blind = 10
        game.p.see_monsters = 10
        rng = SequenceRng([5])
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = rng.rnd
            game.run_visuals()
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(game.hallu_item_syms, {})
        self.assertEqual(game.detected_monster_sym(monster), "F")
        self.assertEqual(rng.calls, [26])

    def test_rogue_544_hallucination_keeps_seen_stairs_real(self):
        # Rogue 5.4.4 misc.c:trip_ch() leaves STAIRS real while ISHALU if seenstairs is true.
        game = new_game(seed=3162)
        set_open_floor(game)
        px, py = game.p.x, game.p.y
        game.tm[py][px + 1] = rogue.T_STAIR
        game.p.hallucinating = 10
        game.seen_stairs = True

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 0
            self.assertEqual(game.visible_tile_sym(px + 1, py, rogue.T_STAIR), rogue.TILE_CH[rogue.T_STAIR][0])
        finally:
            rogue.RNG.rnd = old_rnd

    def test_rogue_544_stepping_on_stairs_marks_seenstairs_and_new_level_resets_it(self):
        # Rogue 5.4.4 move.c:do_move() sets seenstairs on STAIRS; new_level.c:new_level() clears it.
        game = new_game(seed=3163)
        set_open_floor(game)
        px, py = game.p.x, game.p.y
        game.tm[py][px + 1] = rogue.T_STAIR
        game.seen_stairs = False

        game.try_move(1, 0)
        self.assertTrue(game.seen_stairs)

        game.descend()
        self.assertFalse(game.seen_stairs)

    def test_rogue_544_hallucination_potion_records_seen_stairs(self):
        # Rogue 5.4.4 potions.c:P_LSD records seenstairs = seen_stairs() before visuals starts.
        game = new_game(seed=3164)
        set_open_floor(game)
        px, py = game.p.x, game.p.y
        game.tm[py][px + 1] = rogue.T_STAIR
        game.visible.add((px + 1, py))
        potion_kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "hallucination")

        game.use_pot(rogue.Item(rogue.CAT_POT, potion_kind))

        self.assertTrue(game.seen_stairs)
        self.assertEqual(game.visible_tile_sym(px + 1, py, rogue.T_STAIR), rogue.TILE_CH[rogue.T_STAIR][0])

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

    def test_rogue_544_new_monster_runs_when_aggravate_ring_worn(self):
        # Rogue 5.4.4 monsters.c:new_monster() calls runto() when ISWEARING(R_AGGR).
        import rogue_rings

        game = new_game(seed=310)
        set_open_floor(game)
        game.p.ring_l = rogue.Item(rogue.CAT_RING, rogue_rings.R_AGGR)
        spec = next(s for s in rogue.BESTIARY if s.sym == "C")
        monster = game.new_monster_from_spec(game.p.x + 1, game.p.y, spec)

        self.assertTrue(monster.running)
        self.assertEqual(monster.dest, rogue.DEST_PLAYER)

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

    def test_rogue_544_bonus_ring_on_does_not_identify_type(self):
        # Rogue 5.4.4 rings.c:ring_on() uses misc.c:chg_str() but does not set ring_info[].oi_know.
        import rogue_rings

        game = new_game(seed=2101)
        ring = rogue.Item(rogue.CAT_RING, rogue_rings.R_ADDSTR, ench=2)
        game.p.inv.append(ring)
        game.ident.rk[rogue_rings.R_ADDSTR] = False

        game.put_on_ring(ring)

        self.assertIs(game.p.ring_l, ring)
        self.assertEqual(game.p.st, 18)
        self.assertEqual(game.p.max_st, 16)
        self.assertFalse(game.ident.rk[rogue_rings.R_ADDSTR])

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

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            game.use_pot(potion)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(game.p.st, 8)
        self.assertTrue(game.ident.pk[poison])
        self.assertIn("you feel very sick now", game.msgs)
        self.assertNotIn("You feel sick. (Str -2)", game.msgs)

    def test_rogue_544_poison_potion_strength_loss_uses_rnd_3_plus_one(self):
        # Rogue 5.4.4 potions.c:P_POISON calls chg_str(-(rnd(3) + 1)).
        game = new_game(seed=215)
        poison = next(i for i, spec in enumerate(rogue.POTIONS) if spec["name"] == "poison")
        potion = rogue.Item(rogue.CAT_POT, poison)
        game.p.inv.append(potion)
        game.p.st = 10
        calls = []
        old_rnd = rogue.RNG.rnd
        old_randint = rogue.RNG.randint
        try:
            rogue.RNG.rnd = lambda n: calls.append(n) or 1
            rogue.RNG.randint = lambda a, b: (_ for _ in ()).throw(AssertionError("randint used"))
            game.use_pot(potion)
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.RNG.randint = old_randint

        self.assertEqual(calls, [3])
        self.assertEqual(game.p.st, 8)

    def test_rogue_544_poison_potion_strength_floor_is_three(self):
        # Rogue 5.4.4 misc.c:add_str() floors Strength at 3.
        game = new_game(seed=216)
        poison = next(i for i, spec in enumerate(rogue.POTIONS) if spec["name"] == "poison")
        potion = rogue.Item(rogue.CAT_POT, poison)
        game.p.inv.append(potion)
        game.p.st = 4
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 2
            game.use_pot(potion)
        finally:
            rogue.RNG.rnd = old_rnd

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

    def test_rogue_544_potions_helper_turn_see_state_matches_source(self):
        # Rogue 5.4.4 potions.c:turn_see(TRUE) clears SEEMONST; turn_see(FALSE) sets it.
        import rogue_potions

        self.assertEqual(rogue_potions.turn_see_state(True, rogue.HUHDURATION), 0)
        self.assertEqual(rogue_potions.turn_see_state(False, rogue.HUHDURATION), rogue.HUHDURATION)
        self.assertEqual(rogue_potions.turn_see_state(False, 7), 7)
        self.assertTrue(rogue_potions.turn_see_adds_new([False]))
        self.assertFalse(rogue_potions.turn_see_adds_new([True]))
        self.assertFalse(rogue_potions.turn_see_adds_new([]))

    def test_rogue_544_potions_helper_do_pot_state_matches_source(self):
        # Rogue 5.4.4 potions.c:do_pot() sets oi_know from knowit and fuses or lengthens by flag state.
        import rogue_potions

        self.assertFalse(rogue_potions.do_pot_known(False, False))
        self.assertTrue(rogue_potions.do_pot_known(False, True))
        self.assertTrue(rogue_potions.do_pot_known(True, False))
        self.assertEqual(rogue_potions.do_pot_fuse_action(False), "fuse")
        self.assertEqual(rogue_potions.do_pot_fuse_action(True), "lengthen")
        self.assertIsNone(rogue_potions.call_it_guess_after_use(True, "old"))
        self.assertEqual(rogue_potions.call_it_guess_after_use(False, "old"), "old")
        self.assertFalse(rogue_potions.magic_detection_can_scan(False))
        self.assertTrue(rogue_potions.magic_detection_can_scan(True))

    def test_rogue_544_potions_helper_see_invisible_duration_matches_source(self):
        # Rogue 5.4.4 potions.c:P_SEEINVIS do_pot() lengthens existing CANSEE but ring-only CANSEE has no potion fuse.
        import rogue_potions

        self.assertEqual(rogue_potions.see_invisible_duration(0, 10, wearing_ring=False), 10)
        self.assertEqual(rogue_potions.see_invisible_duration(5, 10, wearing_ring=False), 15)
        self.assertEqual(rogue_potions.see_invisible_duration(0, 10, wearing_ring=True), 0)
        self.assertEqual(rogue_potions.see_invisible_duration(5, 10, wearing_ring=True), 15)

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
                "Hello {name}, welcome to the Dungeons of Doom!",
            )
        finally:
            builtins.open = original_open
            rogue.__file__ = original_file
            rogue.TextCatalog._catalogs = original_catalogs

    def test_module_loads_and_new_game_emits_rogue_544_start_message(self):
        game = new_game(seed=7)
        self.assertEqual(game.p.depth, 1)
        self.assertEqual(game.st, rogue.ST_PLAY)
        self.assertEqual(game.msgs[-1], "Hello rogue54, welcome to the Dungeons of Doom!")

    def test_rogue_544_player_initial_stats_use_init_stats(self):
        # Rogue 5.4.4 extern.c:INIT_STATS is {16, 0, 1, 10, 12, "1x4", 12}.
        player = rogue.Player()

        self.assertEqual((player.st, player.exp, player.level, player.ac), (16, 0, 1, 10))
        self.assertEqual((player.hp, player.max_hp), (12, 12))

    def test_initial_inventory_baseline(self):
        # Rogue 5.4.4 init.c:init_player() adds food, ring mail, mace, bow, arrows.
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 4
            inv, weapon, armor = rogue.start_inv()
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual([it.data["name"] for it in inv], [
            "food ration", "ring mail", "mace", "short bow", "arrow"
        ])
        self.assertIs(weapon, inv[2])
        self.assertIs(armor, inv[1])
        self.assertEqual((weapon.hit_plus, weapon.dam_plus), (1, 1))
        self.assertEqual((inv[3].hit_plus, inv[3].dam_plus), (1, 0))
        self.assertEqual((inv[4].hit_plus, inv[4].dam_plus, inv[4].qty), (0, 0, 29))
        self.assertTrue(all(it.known for it in inv[1:5]))
        self.assertEqual(armor.cat, rogue.CAT_ARM)
        self.assertEqual(armor.data["name"], "ring mail")
        self.assertEqual(armor.ench, 1)

    def test_rogue_544_init_helpers_match_init_player(self):
        # Rogue 5.4.4 init.c:init_player() uses rnd(15)+25 and add_pack order.
        import rogue_init

        self.assertEqual(rogue_init.initial_arrow_count(lambda n: 6), 31)
        self.assertEqual(rogue_init.initial_pack_order("food", "armor", "mace", "bow", "arrows"),
                         ["food", "armor", "mace", "bow", "arrows"])

    def test_rogue_544_init_scroll_title_uses_source_word_and_syllable_rolls(self):
        # Rogue 5.4.4 init.c:init_names() uses nwords=rnd(3)+2 and nsyl=rnd(3)+1.
        import rogue_init

        syllables = ["aa", "bb", "cc", "dd"]
        rolls = iter([1, 0, 0, 1, 2, 0, 1, 3, 2])
        calls = []

        title = rogue_init.scroll_title(syllables, lambda n: calls.append(n) or next(rolls))

        self.assertEqual(calls, [3, 3, 4, 3, 4, 4, 3, 4, 4])
        self.assertEqual(title, "aa ccaa ddcc")

    def test_rogue_544_init_scroll_title_maxname_limits_whole_title(self):
        # Rogue 5.4.4 init.c:init_names() checks cp against prbuf[MAXNAME], not each word.
        import rogue_init

        syllables = ["aaaa", "bbbb"]
        rolls = iter([0, 0, 0, 0, 1])
        calls = []

        title = rogue_init.scroll_title(syllables, lambda n: calls.append(n) or next(rolls), max_name=7)

        self.assertEqual(calls, [3, 3, 2, 3, 2])
        self.assertEqual(title, "aaaa ")

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

    def test_rogue_544_wear_reject_does_not_spend_turn_from_item_confirm(self):
        # Rogue 5.4.4 armor.c:wear() sets after=FALSE when cur_armor != NULL.
        game = new_game(seed=5040)
        replacement = rogue.Item(rogue.CAT_ARM, 1)
        game.p.inv.append(replacement)
        game.cact = "Wear"
        game.fitems = [replacement]
        game.icur = 0
        turn = game.turn

        game.item_confirm()

        self.assertEqual(game.turn, turn)
        self.assertEqual(game.st, rogue.ST_PLAY)

    def test_rogue_544_wear_rejects_non_armor_items(self):
        # Rogue 5.4.4 armor.c:wear() rejects obj->o_type != ARMOR.
        game = new_game(seed=5037)
        game.p.arm = None
        weapon = rogue.Item(rogue.CAT_WPN, 0)
        game.p.inv.append(weapon)

        game.wear(weapon)

        self.assertIsNone(game.p.arm)
        self.assertIn("you can't wear that", game.msgs)

    def test_rogue_544_wear_rejects_non_armor_and_spends_turn_from_item_confirm(self):
        # Rogue 5.4.4 armor.c:wear() does not clear after for obj->o_type != ARMOR.
        game = new_game(seed=5047)
        game.p.arm = None
        weapon = rogue.Item(rogue.CAT_WPN, 0)
        game.p.inv.append(weapon)
        game.cact = "Wear"
        game.fitems = [weapon]
        game.icur = 0
        turn = game.turn

        game.item_confirm()

        self.assertIsNone(game.p.arm)
        self.assertEqual(game.turn, turn + 1)
        self.assertIn("you can't wear that", game.msgs)

    def test_rogue_544_armor_helper_wear_result_matches_wear_gates(self):
        # Rogue 5.4.4 armor.c:wear() only clears after when already wearing armor.
        self.assertEqual(rogue.rogue_armor.wear_result(has_current_armor=True, item_is_armor=True), "already-wearing")
        self.assertEqual(rogue.rogue_armor.wear_result(has_current_armor=False, item_is_armor=False), "not-armor")
        self.assertEqual(rogue.rogue_armor.wear_result(has_current_armor=False, item_is_armor=True), "wear")

    def test_rogue_544_wield_rejects_armor(self):
        # Rogue 5.4.4 weapons.c:wield() rejects obj->o_type == ARMOR.
        game = new_game(seed=5038)
        current = game.p.wpn
        armor = rogue.Item(rogue.CAT_ARM, 0)
        game.p.inv.append(armor)

        game.wield(armor)

        self.assertIs(game.p.wpn, current)
        self.assertIn("you can't wield armor", game.msgs)

    def test_rogue_544_wield_current_weapon_uses_is_current_message(self):
        # Rogue 5.4.4 weapons.c:wield() sends is_current(obj) to the no-action path.
        game = new_game(seed=5039)
        current = game.p.wpn

        game.wield(current)

        self.assertIs(game.p.wpn, current)
        self.assertIn("That's already in use", game.msgs)

    def test_rogue_544_wield_rejects_do_not_spend_turn_from_item_confirm(self):
        # Rogue 5.4.4 weapons.c:wield() bad path sets after=FALSE.
        game = new_game(seed=5041)
        armor = rogue.Item(rogue.CAT_ARM, 0)
        game.p.inv.append(armor)
        game.cact = "Wield"
        game.fitems = [armor]
        game.icur = 0
        turn = game.turn

        game.item_confirm()

        self.assertEqual(game.turn, turn)
        self.assertEqual(game.st, rogue.ST_PLAY)

    def test_rogue_544_wield_prompt_allows_non_weapon_items(self):
        # Rogue 5.4.4 pack.c:get_item("wield", WEAPON) returns any chosen pack item;
        # weapons.c:wield() rejects armor only after selection.
        game = new_game(seed=5042)
        weapon = rogue.Item(rogue.CAT_WPN, 1)
        potion = rogue.Item(rogue.CAT_POT, 0)
        armor = rogue.Item(rogue.CAT_ARM, 0)
        game.p.inv = [weapon, potion, armor]

        game.start_item_action("Wield")

        self.assertEqual(game.st, rogue.ST_ITEM)
        self.assertEqual(game.fitems, [weapon, potion, armor])

    def test_rogue_544_wield_cursed_current_weapon_failure_spends_turn(self):
        # Rogue 5.4.4 weapons.c:wield() dropcheck(cur_weapon) failure does not clear after.
        game = new_game(seed=5048)
        current = game.p.wpn
        current.cursed = True
        replacement = rogue.Item(rogue.CAT_WPN, 1)
        game.p.inv.append(replacement)
        game.cact = "Wield"
        game.fitems = [replacement]
        game.icur = 0
        turn = game.turn

        game.item_confirm()

        self.assertIs(game.p.wpn, current)
        self.assertEqual(game.turn, turn + 1)
        self.assertIn("cursed", game.msgs[-1])

    def test_rogue_544_throw_cursed_equipped_ring_failure_spends_turn(self):
        # Rogue 5.4.4 weapons.c:missile() calls things.c:dropcheck(obj) before is_current(obj).
        import rogue_rings

        game = new_game(seed=5049)
        ring = rogue.Item(rogue.CAT_RING, rogue_rings.R_REGEN, cursed=True)
        game.p.inv.append(ring)
        game.p.ring_l = ring
        game.cact = "Throw"
        game.throw_dir = (1, 0)
        game.fitems = [ring]
        game.icur = 0
        turn = game.turn

        game.item_confirm()

        self.assertIs(game.p.ring_l, ring)
        self.assertIn(ring, game.p.inv)
        self.assertEqual(game.turn, turn + 1)
        self.assertIn("cursed", game.msgs[-1])

    def test_rogue_544_throw_stack_copy_preserves_item_flags_and_label(self):
        # Rogue 5.4.4 pack.c:leave_pack(newobj=TRUE) copies the object before setting o_count=1.
        game = new_game(seed=5064)
        set_open_floor(game)
        arrows = rogue.Item(rogue.CAT_WPN, 3, qty=3, known=False)
        arrows.o_label = "marked"
        arrows.protected = True
        game.p.inv.append(arrows)

        game.throw(arrows, 1, 0)

        thrown = game.throw_anim["outcome"]["item"]
        self.assertIsNot(thrown, arrows)
        self.assertEqual(arrows.qty, 2)
        self.assertEqual(thrown.qty, 1)
        self.assertFalse(thrown.known)
        self.assertEqual(thrown.o_label, "marked")
        self.assertTrue(thrown.protected)

    def test_rogue_544_throw_wielded_weapon_stack_clears_current_weapon(self):
        # Rogue 5.4.4 weapons.c:missile() calls dropcheck(obj), which clears cur_weapon before leave_pack().
        game = new_game(seed=5065)
        set_open_floor(game)
        arrows = rogue.Item(rogue.CAT_WPN, 3, qty=3)
        game.p.inv.append(arrows)
        game.p.wpn = arrows

        game.throw(arrows, 1, 0)

        self.assertIsNone(game.p.wpn)
        self.assertIn(arrows, game.p.inv)
        self.assertEqual(arrows.qty, 2)

    def test_rogue_544_throw_see_invisible_ring_extinguishes_unsee(self):
        # Rogue 5.4.4 weapons.c:missile() calls things.c:dropcheck(); ring branch calls unsee()/extinguish().
        import rogue_rings

        game = new_game(seed=5059)
        set_open_floor(game)
        ring = rogue.Item(rogue.CAT_RING, rogue_rings.R_SEEINVIS)
        game.p.inv.append(ring)
        game.p.ring_l = ring
        game.p.see_invisible = 20
        game.fuses.fuse("unsee", 20, rogue.rogue_daemons.AFTER)

        game.throw(ring, 1, 0)

        self.assertIsNone(game.p.ring_l)
        self.assertEqual(game.p.see_invisible, 0)
        self.assertEqual(game.fuses.remaining("unsee"), 0)

    def test_rogue_544_throw_worn_armor_wastes_time_for_doctor(self):
        # Rogue 5.4.4 weapons.c:missile() calls things.c:dropcheck(); armor branch calls waste_time().
        game = new_game(seed=5060)
        set_open_floor(game)
        game.daemons.kill("runners")
        game.daemons.kill("stomach")
        armor = game.p.arm
        game.p.level = 1
        game.p.hp = game.p.max_hp - 1
        game.p.quiet = 19

        game.throw(armor, 1, 0)

        self.assertIsNone(game.p.arm)
        self.assertEqual(game.p.hp, game.p.max_hp)
        self.assertEqual(game.p.quiet, 0)

    def test_rogue_544_things_helper_dropcheck_result_matches_dropcheck_gate(self):
        # Rogue 5.4.4 things.c:dropcheck() only rejects current cursed equipment.
        self.assertEqual(rogue.rogue_things.dropcheck_result(is_current=False, is_cursed=True), "ok")
        self.assertEqual(rogue.rogue_things.dropcheck_result(is_current=True, is_cursed=True), "cursed")
        self.assertEqual(rogue.rogue_things.dropcheck_result(is_current=True, is_cursed=False), "unequip")

    def test_rogue_544_drop_on_occupied_floor_is_rejected_without_turn(self):
        # Rogue 5.4.4 things.c:drop() clears after when chat(hero) is not FLOOR/PASSAGE.
        game = new_game(seed=5050)
        set_open_floor(game)
        carried = rogue.Item(rogue.CAT_FOOD, 0)
        floor_item = rogue.Item(rogue.CAT_POT, 0)
        floor_item.x, floor_item.y = game.p.x, game.p.y
        game.p.inv.append(carried)
        game.gitems.append(floor_item)
        game.cact = "Drop"
        game.fitems = [carried]
        game.icur = 0
        turn = game.turn

        game.item_confirm()

        self.assertIn(carried, game.p.inv)
        self.assertEqual(game.gitems.count(floor_item), 1)
        self.assertEqual(game.turn, turn)
        self.assertIn("there is something there already", game.msgs[-1])

    def test_rogue_544_drop_on_stairs_is_rejected_without_turn(self):
        # Rogue 5.4.4 things.c:drop() only allows FLOOR/PASSAGE under the hero.
        game = new_game(seed=5051)
        set_open_floor(game)
        carried = rogue.Item(rogue.CAT_FOOD, 0)
        game.p.inv.append(carried)
        game.tm[game.p.y][game.p.x] = rogue.T_STAIR
        game.cact = "Drop"
        game.fitems = [carried]
        game.icur = 0
        turn = game.turn

        game.item_confirm()

        self.assertIn(carried, game.p.inv)
        self.assertEqual(game.turn, turn)
        self.assertIn("there is something there already", game.msgs[-1])

    def test_rogue_544_drop_cursed_current_weapon_failure_spends_turn(self):
        # Rogue 5.4.4 things.c:drop() uses dropcheck(); cursed failure does not clear after.
        game = new_game(seed=5052)
        set_open_floor(game)
        weapon = game.p.wpn
        weapon.cursed = True
        game.cact = "Drop"
        game.fitems = [weapon]
        game.icur = 0
        turn = game.turn

        game.item_confirm()

        self.assertIs(game.p.wpn, weapon)
        self.assertIn(weapon, game.p.inv)
        self.assertEqual(game.turn, turn + 1)
        self.assertIn("you can't.  It appears to be cursed", game.msgs[-1])

    def test_rogue_544_drop_amulet_clears_amulet_flag(self):
        # Rogue 5.4.4 things.c:drop() sets amulet = FALSE when dropping AMULET.
        game = new_game(seed=5054)
        set_open_floor(game)
        amulet = rogue.Item(rogue.CAT_AMULET, 0)
        game.p.inv.append(amulet)
        game.p.has_amulet = True
        game.cact = "Drop"
        game.fitems = [amulet]
        game.icur = 0

        game.item_confirm()

        self.assertFalse(game.p.has_amulet)
        self.assertNotIn(amulet, game.p.inv)
        self.assertIn(amulet, game.gitems)

    def test_rogue_544_drop_current_weapon_clears_cur_weapon(self):
        # Rogue 5.4.4 things.c:drop() calls dropcheck(), which clears cur_weapon.
        game = new_game(seed=5065)
        set_open_floor(game)
        weapon = game.p.wpn
        game.cact = "Drop"
        game.fitems = [weapon]
        game.icur = 0

        game.item_confirm()

        self.assertIsNone(game.p.wpn)
        self.assertNotIn(weapon, game.p.inv)
        self.assertIn(weapon, game.gitems)

    def test_rogue_544_drop_current_armor_clears_cur_armor_and_recalculates_ac(self):
        # Rogue 5.4.4 things.c:dropcheck() armor branch calls waste_time() and clears cur_armor.
        game = new_game(seed=5066)
        set_open_floor(game)
        armor = game.p.arm
        self.assertIsNotNone(armor)
        game.cact = "Drop"
        game.fitems = [armor]
        game.icur = 0

        game.item_confirm()

        self.assertIsNone(game.p.arm)
        self.assertEqual(game.p.ac, 10)
        self.assertNotIn(armor, game.p.inv)
        self.assertIn(armor, game.gitems)

    def test_rogue_544_drop_food_stack_leaves_rest_in_pack(self):
        # Rogue 5.4.4 things.c:drop() calls pack.c:leave_pack(..., all=!ISMULT), so FOOD drops one.
        game = new_game(seed=5055)
        set_open_floor(game)
        food = rogue.Item(rogue.CAT_FOOD, 0, qty=3)
        game.p.inv.append(food)
        game.cact = "Drop"
        game.fitems = [food]
        game.icur = 0

        game.item_confirm()

        self.assertIn(food, game.p.inv)
        self.assertEqual(food.qty, 2)
        dropped = [item for item in game.gitems if item.cat == rogue.CAT_FOOD and item.kind == 0]
        self.assertEqual(len(dropped), 1)
        self.assertEqual(dropped[0].qty, 1)

    def test_rogue_544_eat_food_stack_consumes_one(self):
        # Rogue 5.4.4 misc.c:eat() calls pack.c:leave_pack(obj, FALSE, FALSE).
        game = new_game(seed=5056)
        food = rogue.Item(rogue.CAT_FOOD, 0, qty=3)
        game.p.inv.append(food)

        game.eat(food)

        self.assertIn(food, game.p.inv)
        self.assertEqual(food.qty, 2)

    def test_rogue_544_eating_wielded_food_stack_clears_current_weapon(self):
        # Rogue 5.4.4 misc.c:eat() clears cur_weapon before leave_pack().
        game = new_game(seed=5061)
        food = rogue.Item(rogue.CAT_FOOD, 0, qty=2)
        game.p.inv.append(food)
        game.p.wpn = food

        game.eat(food)

        self.assertIsNone(game.p.wpn)
        self.assertIn(food, game.p.inv)
        self.assertEqual(food.qty, 1)

    def test_rogue_544_eat_clears_current_weapon_before_food_message(self):
        # Rogue 5.4.4 misc.c:eat() clears cur_weapon before food messages/check_level().
        game = new_game(seed=5066)
        food = rogue.Item(rogue.CAT_FOOD, 0, qty=1)
        game.p.inv.append(food)
        game.p.wpn = food
        seen = []
        rolls = iter([0, 0])
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: next(rolls)
            game.msg = lambda *args, **kwargs: seen.append(game.p.wpn)
            game.eat(food)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(seen, [None])
        self.assertIsNone(game.p.wpn)

    def test_rogue_544_eat_non_food_does_not_consume_pack_item(self):
        # Rogue 5.4.4 misc.c:eat() rejects obj->o_type != FOOD before leave_pack().
        game = new_game(seed=5062)
        potion = rogue.Item(rogue.CAT_POT, 0)
        game.p.inv.append(potion)
        game.p.food = 100

        game.eat(potion)

        self.assertIn(potion, game.p.inv)
        self.assertEqual(game.p.food, 100)
        self.assertIn("ugh, you would get ill if you ate that", game.msgs)

    def test_rogue_544_quaff_non_potion_does_not_consume_pack_item(self):
        # Rogue 5.4.4 potions.c:quaff() rejects obj->o_type != POTION before leave_pack().
        game = new_game(seed=5063)
        scroll = rogue.Item(rogue.CAT_SCR, 0)
        game.p.inv.append(scroll)
        game.p.hp = 1

        game.use_pot(scroll)

        self.assertIn(scroll, game.p.inv)
        self.assertEqual(game.p.hp, 1)
        self.assertIn("yuk! Why would you want to drink that?", game.msgs)

    def test_rogue_544_read_non_scroll_does_not_consume_pack_item(self):
        # Rogue 5.4.4 scrolls.c:read_scroll() rejects obj->o_type != SCROLL before leave_pack().
        game = new_game(seed=5064)
        potion = rogue.Item(rogue.CAT_POT, 0)
        game.p.inv.append(potion)

        game.use_scr(potion)

        self.assertIn(potion, game.p.inv)
        self.assertIn("there is nothing on it to read", game.msgs)

    def test_rogue_544_quaff_potion_stack_consumes_one(self):
        # Rogue 5.4.4 potions.c:quaff() calls pack.c:leave_pack(obj, FALSE, FALSE).
        kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "healing")
        game = new_game(seed=5057)
        potion = rogue.Item(rogue.CAT_POT, kind, qty=2)
        game.p.inv.append(potion)

        game.use_pot(potion)

        self.assertIn(potion, game.p.inv)
        self.assertEqual(potion.qty, 1)

    def test_rogue_544_quaff_wielded_potion_stack_clears_current_weapon(self):
        # Rogue 5.4.4 potions.c:quaff() clears cur_weapon before leave_pack().
        kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "healing")
        game = new_game(seed=5062)
        potion = rogue.Item(rogue.CAT_POT, kind, qty=2)
        game.p.inv.append(potion)
        game.p.wpn = potion

        game.use_pot(potion)

        self.assertIsNone(game.p.wpn)
        self.assertIn(potion, game.p.inv)
        self.assertEqual(potion.qty, 1)

    def test_rogue_544_quaff_clears_current_weapon_before_effect_branch(self):
        # Rogue 5.4.4 potions.c:quaff() clears cur_weapon before the switch effects run.
        kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "healing")
        game = new_game(seed=5065)
        potion = rogue.Item(rogue.CAT_POT, kind, qty=1)
        game.p.inv.append(potion)
        game.p.wpn = potion
        seen = []
        game.sight = lambda: seen.append(game.p.wpn)

        game.use_pot(potion)

        self.assertEqual(seen, [None])
        self.assertIsNone(game.p.wpn)

    def test_rogue_544_quaff_leaves_pack_before_effect_branch(self):
        # Rogue 5.4.4 potions.c:quaff() calls leave_pack() before the switch effects run.
        kind = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "healing")
        game = new_game(seed=5067)
        potion = rogue.Item(rogue.CAT_POT, kind, qty=1)
        game.p.inv.append(potion)
        seen = []
        game.sight = lambda: seen.append(potion in game.p.inv)

        game.use_pot(potion)

        self.assertEqual(seen, [False])
        self.assertNotIn(potion, game.p.inv)

    def test_rogue_544_read_scroll_stack_consumes_one(self):
        # Rogue 5.4.4 scrolls.c:read_scroll() calls pack.c:leave_pack(obj, FALSE, FALSE).
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "remove curse")
        game = new_game(seed=5058)
        scroll = rogue.Item(rogue.CAT_SCR, kind, qty=2)
        game.p.inv.append(scroll)

        game.use_scr(scroll)

        self.assertIn(scroll, game.p.inv)
        self.assertEqual(scroll.qty, 1)

    def test_rogue_544_identify_scroll_without_targets_consumes_one(self):
        # Rogue 5.4.4 scrolls.c:read_scroll() calls leave_pack() once before whatis().
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "identify potion")
        game = new_game(seed=5059)
        scroll = rogue.Item(rogue.CAT_SCR, kind, qty=2)
        game.p.inv.append(scroll)

        game.use_scr(scroll)

        self.assertIn(scroll, game.p.inv)
        self.assertEqual(scroll.qty, 1)

    def test_rogue_544_read_wielded_scroll_stack_clears_current_weapon(self):
        # Rogue 5.4.4 scrolls.c:read_scroll() clears cur_weapon before leave_pack().
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "remove curse")
        game = new_game(seed=5063)
        scroll = rogue.Item(rogue.CAT_SCR, kind, qty=2)
        game.p.inv.append(scroll)
        game.p.wpn = scroll

        game.use_scr(scroll)

        self.assertIsNone(game.p.wpn)
        self.assertIn(scroll, game.p.inv)
        self.assertEqual(scroll.qty, 1)

    def test_rogue_544_read_scroll_leaves_pack_before_effect_branch(self):
        # Rogue 5.4.4 scrolls.c:read_scroll() calls leave_pack() before the switch effects run.
        kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "aggravate monsters")
        game = new_game(seed=5068)
        scroll = rogue.Item(rogue.CAT_SCR, kind, qty=1)
        game.p.inv.append(scroll)
        seen = []
        game.aggravate_monsters = lambda: seen.append(scroll in game.p.inv)

        game.use_scr(scroll)

        self.assertEqual(seen, [False])
        self.assertNotIn(scroll, game.p.inv)

    def test_rogue_544_pack_helper_leave_pack_counts_split_mult_items(self):
        # Rogue 5.4.4 pack.c:leave_pack() splits one object only for count > 1 && !all.
        self.assertEqual(rogue.rogue_pack.leave_pack_counts(3, is_mult=True, all_items=False), (2, 1))
        self.assertEqual(rogue.rogue_pack.leave_pack_counts(3, is_mult=True, all_items=True), (0, 3))
        self.assertEqual(rogue.rogue_pack.leave_pack_counts(1, is_mult=True, all_items=False), (0, 1))

    def test_rogue_544_put_on_ring_rejects_non_ring_and_spends_turn(self):
        # Rogue 5.4.4 rings.c:ring_on() rejects obj->o_type != RING without clearing after.
        game = new_game(seed=5042)
        game.p.ring_l = None
        armor = rogue.Item(rogue.CAT_ARM, 0)
        game.p.inv.append(armor)
        game.cact = "Put on"
        game.fitems = [armor]
        game.icur = 0
        turn = game.turn

        game.item_confirm()

        self.assertIsNone(game.p.ring_l)
        self.assertEqual(game.turn, turn + 1)
        self.assertIn("it would be difficult to wrap that around a finger", game.msgs)

    def test_rogue_544_put_on_current_ring_uses_is_current_before_two_ring_check(self):
        # Rogue 5.4.4 rings.c:ring_on() checks misc.c:is_current() before "wearing two".
        import rogue_rings

        game = new_game(seed=5043)
        left = rogue.Item(rogue.CAT_RING, rogue_rings.R_PROTECT)
        right = rogue.Item(rogue.CAT_RING, rogue_rings.R_ADDSTR)
        game.p.inv.extend([left, right])
        game.p.ring_l = left
        game.p.ring_r = right
        game.cact = "Put on"
        game.fitems = [left]
        game.icur = 0
        turn = game.turn

        game.item_confirm()

        self.assertIs(game.p.ring_l, left)
        self.assertIs(game.p.ring_r, right)
        self.assertEqual(game.turn, turn + 1)
        self.assertIn("That's already in use", game.msgs)

    def test_rogue_544_put_on_third_ring_spends_turn(self):
        # Rogue 5.4.4 rings.c:ring_on() "wearing two" path does not clear after.
        import rogue_rings

        game = new_game(seed=5044)
        left = rogue.Item(rogue.CAT_RING, rogue_rings.R_PROTECT)
        right = rogue.Item(rogue.CAT_RING, rogue_rings.R_ADDSTR)
        third = rogue.Item(rogue.CAT_RING, rogue_rings.R_REGEN)
        game.p.inv.extend([left, right, third])
        game.p.ring_l = left
        game.p.ring_r = right
        game.cact = "Put on"
        game.fitems = [third]
        game.icur = 0
        turn = game.turn

        game.item_confirm()

        self.assertIs(game.p.ring_l, left)
        self.assertIs(game.p.ring_r, right)
        self.assertEqual(game.turn, turn + 1)
        self.assertIn("You already have a ring on each hand.", game.msgs)

    def test_rogue_544_rings_helper_ring_on_result_matches_ring_on_gates(self):
        # Rogue 5.4.4 rings.c:ring_on() gates non-ring, current ring, and wearing-two.
        import rogue_rings

        self.assertEqual(rogue_rings.ring_on_result(item_is_ring=False, is_current=False, both_hands_full=False), "not-ring")
        self.assertEqual(rogue_rings.ring_on_result(item_is_ring=True, is_current=True, both_hands_full=True), "current")
        self.assertEqual(rogue_rings.ring_on_result(item_is_ring=True, is_current=False, both_hands_full=True), "full")
        self.assertEqual(rogue_rings.ring_on_result(item_is_ring=True, is_current=False, both_hands_full=False), "put-on")

    def test_rogue_544_rings_helper_ring_off_result_matches_ring_off_gates(self):
        # Rogue 5.4.4 rings.c:ring_off() and things.c:dropcheck() gate unworn/cursed rings.
        import rogue_rings

        self.assertEqual(rogue_rings.ring_off_result(is_wearing=False, is_cursed=False), "not-wearing")
        self.assertEqual(rogue_rings.ring_off_result(is_wearing=True, is_cursed=True), "cursed")
        self.assertEqual(rogue_rings.ring_off_result(is_wearing=True, is_cursed=False), "take-off")

    def test_rogue_544_weapons_helper_wield_result_matches_wield_gates(self):
        # Rogue 5.4.4 weapons.c:wield() gates dropcheck(), armor, and is_current().
        import rogue_weapons

        self.assertEqual(rogue_weapons.wield_result(current_cursed=True, item_is_armor=False, is_current=False), "cursed")
        self.assertEqual(rogue_weapons.wield_result(current_cursed=False, item_is_armor=True, is_current=False), "armor")
        self.assertEqual(rogue_weapons.wield_result(current_cursed=False, item_is_armor=False, is_current=True), "current")
        self.assertEqual(rogue_weapons.wield_result(current_cursed=False, item_is_armor=False, is_current=False), "wield")

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

    def test_rogue_544_monster_mean_flags_match_extern_table(self):
        # Rogue 5.4.4 extern.c:monsters[] gives ISMEAN to H but not B.
        specs = {m.sym: m for m in rogue.BESTIARY}
        self.assertIn("mean", specs["H"].flags)
        self.assertNotIn("mean", specs["B"].flags)
        self.assertTrue(rogue.Monster(1, 1, "H", "hobgoblin", 3, 1, 5, "1x8", 3, specs["H"].flags).mean)
        self.assertFalse(rogue.Monster(1, 1, "B", "bat", 1, 1, 3, "1x2", 1, specs["B"].flags).mean)

    def test_rogue_544_medusa_table_has_no_melee_confuse_flag(self):
        # Rogue 5.4.4 extern.c:monsters[] gives Medusa ISMEAN; gaze confusion lives in monsters.c:wake_monster().
        specs = {m.sym: m for m in rogue.BESTIARY}
        self.assertIn("mean", specs["M"].flags)
        self.assertNotIn("confuse", specs["M"].flags)

    def test_rogue_544_monster_attack_has_no_melee_confuse_special(self):
        # Rogue 5.4.4 fight.c:attack() has no CANHUH melee branch for monsters.
        game = new_game(seed=5033)
        set_open_floor(game)
        monster = monster_at(game.p.x + 1, game.p.y, "O", "orc", 1, 8, 5, "1x1", 1, "confuse")
        game.roll_monster_attack = lambda m: (True, 0)
        game.save_vs_magic = lambda: False

        game.m_attack(monster)

        self.assertEqual(game.p.confused, 0)
        self.assertNotIn("You feel confused!", game.msgs)

    def test_rogue_544_monster_greed_flag_is_not_gold_steal(self):
        # Rogue 5.4.4 extern.c:monsters[] uses ISGREED for orcs; Leprechauns steal purse in fight.c.
        specs = {m.sym: m for m in rogue.BESTIARY}
        self.assertIn("greed", specs["O"].flags)
        self.assertNotIn("steal_gold", specs["O"].flags)
        self.assertIn("steal_gold", specs["L"].flags)

    def test_rogue_544_monsters_helper_parse_flags_and_mean(self):
        # Rogue 5.4.4 extern.c:monsters[] flags are rebuilt on new_monster().
        self.assertEqual(rogue.rogue_monsters.parse_flags("fly,mean"), {"fly", "mean"})
        self.assertEqual(rogue.rogue_monsters.parse_flags(""), set())
        self.assertTrue(rogue.rogue_monsters.is_mean({"mean"}))
        self.assertFalse(rogue.rogue_monsters.is_mean({"fly"}))

    def test_rogue_544_monsters_helper_has_special_obeys_cancel(self):
        # Rogue 5.4.4 fight.c:attack() gates specials with !ISCANC.
        monster = monster_at(1, 1, flags="poison")
        self.assertTrue(rogue.rogue_monsters.has_special(monster, "poison"))
        monster.flags.add("cancel")
        self.assertFalse(rogue.rogue_monsters.has_special(monster, "poison"))

    def test_rogue_544_monsters_helper_force_mean_for_treasure_room(self):
        # Rogue 5.4.4 new_level.c:treas_room() adds ISMEAN to room monsters.
        monster = monster_at(1, 1, "B", "bat", flags="fly")

        rogue.rogue_monsters.force_mean(monster)

        self.assertTrue(monster.mean)
        self.assertIn("mean", monster.flags)

    def test_rogue_544_monsters_helper_is_greedy_matches_isgreed(self):
        # Rogue 5.4.4 rogue.h:ISGREED is a gold-guard chase flag, not an ISCANC special attack.
        monster = monster_at(1, 1, "O", "orc", flags="greed,cancel")
        self.assertTrue(rogue.rogue_monsters.is_greedy(monster))

    def test_rogue_544_monsters_helper_is_flying_matches_isfly(self):
        # Rogue 5.4.4 rogue.h:ISFLY drives chase.c:runners() extra movement.
        monster = monster_at(1, 1, "K", "kestrel", flags="fly")
        self.assertTrue(rogue.rogue_monsters.is_flying(monster))

    def test_rogue_544_monsters_helper_is_invisible_matches_isinvis(self):
        # Rogue 5.4.4 rogue.h:ISINVIS is checked by see_monst()/look() visibility.
        monster = monster_at(1, 1, "P", "phantom", flags="invis")
        self.assertTrue(rogue.rogue_monsters.is_invisible(monster))

    def test_rogue_544_monsters_helper_make_invisible_matches_ws_invis(self):
        # Rogue 5.4.4 sticks.c:WS_INVIS sets ISINVIS on the target monster.
        monster = monster_at(1, 1, "O", "orc")
        rogue.rogue_monsters.make_invisible(monster)
        self.assertTrue(rogue.rogue_monsters.is_invisible(monster))

    def test_rogue_544_monsters_helper_medusa_gaze_matches_wake_monster_gate(self):
        # Rogue 5.4.4 monsters.c:wake_monster() uses ch == 'M' and !ISCANC for Medusa gaze.
        medusa = monster_at(1, 1, "M", "medusa")
        orc = monster_at(1, 1, "O", "orc", flags="confuse")
        self.assertTrue(rogue.rogue_monsters.medusa_gaze_active(medusa))
        self.assertFalse(rogue.rogue_monsters.medusa_gaze_active(orc))
        medusa.flags.add("cancel")
        self.assertFalse(rogue.rogue_monsters.medusa_gaze_active(medusa))

    def test_rogue_544_monsters_helper_medusa_gaze_can_try_matches_wake_monster(self):
        # Rogue 5.4.4 monsters.c:wake_monster() gates Medusa gaze by ISRUN/ISBLIND/ISHALU/ISFOUND.
        medusa = monster_at(1, 1, "M", "medusa")
        medusa.running = True
        self.assertTrue(rogue.rogue_monsters.medusa_gaze_can_try(medusa, blind=False, hallucinating=False))
        self.assertFalse(rogue.rogue_monsters.medusa_gaze_can_try(medusa, blind=True, hallucinating=False))
        self.assertFalse(rogue.rogue_monsters.medusa_gaze_can_try(medusa, blind=False, hallucinating=True))
        medusa.found = True
        self.assertFalse(rogue.rogue_monsters.medusa_gaze_can_try(medusa, blind=False, hallucinating=False))

    def test_rogue_544_monsters_helper_medusa_gaze_visibility_gate(self):
        # Rogue 5.4.4 monsters.c:wake_monster() requires lit proom or dist() < LAMPDIST.
        self.assertTrue(rogue.rogue_monsters.medusa_gaze_visible(player_room_lit=True, distance2=99, lampdist=3))
        self.assertTrue(rogue.rogue_monsters.medusa_gaze_visible(player_room_lit=False, distance2=2, lampdist=3))
        self.assertFalse(rogue.rogue_monsters.medusa_gaze_visible(player_room_lit=False, distance2=3, lampdist=3))

    def test_rogue_544_monsters_helper_mark_medusa_gaze_found(self):
        # Rogue 5.4.4 monsters.c:wake_monster() sets ISFOUND before saving vs Medusa gaze.
        medusa = monster_at(1, 1, "M", "medusa")
        self.assertFalse(medusa.found)
        rogue.rogue_monsters.mark_found(medusa)
        self.assertTrue(medusa.found)

    def test_rogue_544_monsters_helper_mean_wake_matches_wake_monster_gate(self):
        # Rogue 5.4.4 monsters.c:wake_monster() gates ISMEAN wake by ISRUN/ISHELD/stealth/ISLEVIT.
        monster = monster_at(1, 1, "H", "hobgoblin", flags="mean")
        self.assertTrue(rogue.rogue_monsters.mean_wake_active(monster, stealth=False, levitating=False))
        self.assertFalse(rogue.rogue_monsters.mean_wake_active(monster, stealth=True, levitating=False))
        self.assertFalse(rogue.rogue_monsters.mean_wake_active(monster, stealth=False, levitating=True))
        monster.running = True
        self.assertFalse(rogue.rogue_monsters.mean_wake_active(monster, stealth=False, levitating=False))

    def test_rogue_544_monsters_helper_apply_deep_haste_matches_new_monster(self):
        # Rogue 5.4.4 monsters.c:new_monster() sets ISHASTE when level > 29.
        monster = monster_at(1, 1, "O", "orc")
        rogue.rogue_monsters.apply_deep_haste(monster, 29)
        self.assertNotIn("haste", monster.flags)

        rogue.rogue_monsters.apply_deep_haste(monster, 30)
        self.assertIn("haste", monster.flags)

    def test_rogue_544_monsters_helper_cancel_matches_ws_cancel_flags(self):
        # Rogue 5.4.4 sticks.c:WS_CANCEL sets ISCANC, clears ISINVIS/CANHUH, and reveals disguise.
        monster = monster_at(1, 1, "X", "xeroc", flags="invis,confuse")
        monster.disguise = "?"

        rogue.rogue_monsters.cancel_monster(monster)

        self.assertIn("cancel", monster.flags)
        self.assertNotIn("invis", monster.flags)
        self.assertNotIn("confuse", monster.flags)
        self.assertEqual(monster.disguise, "X")

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

    def test_rogue_544_nymph_steal_ignores_non_magic_weapons_and_armor(self):
        # Rogue 5.4.4 fight.c:attack() filters pack with potions.c:is_magic().
        game = new_game(seed=305)
        plain_weapon = rogue.Item(rogue.CAT_WPN, 0, hit_plus=0, dam_plus=0)
        plain_armor = rogue.Item(rogue.CAT_ARM, 0, ench=0)
        potion = rogue.Item(rogue.CAT_POT, 0)
        game.p.inv = [plain_weapon, plain_armor, potion]

        self.assertIs(game.monster_has_magic_item_to_steal(), potion)

    def test_rogue_544_potions_helper_is_magic_matches_source(self):
        # Rogue 5.4.4 potions.c:is_magic() treats only enchanted/protected weapon and armor as magic.
        import rogue_potions

        self.assertTrue(rogue_potions.is_magic_item("potion", False, False))
        self.assertFalse(rogue_potions.is_magic_item("weapon", False, False))
        self.assertTrue(rogue_potions.is_magic_item("weapon", True, False))
        self.assertFalse(rogue_potions.is_magic_item("armor", False, False))
        self.assertTrue(rogue_potions.is_magic_item("armor", False, True))

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

    def test_rogue_544_nymph_steal_message_matches_fight_c(self):
        # Rogue 5.4.4 fight.c:attack() prints "she stole %s!" after leave_pack().
        game = new_game(seed=306)
        set_open_floor(game)
        potion = rogue.Item(rogue.CAT_POT, 0)
        game.p.inv = [potion]
        nymph = monster_at(game.p.x + 1, game.p.y, "N", "nymph", damage="1x1", flags="steal_item")
        game.mons = [nymph]
        game.swing_hits = lambda at_lvl, op_arm, wplus: True

        game.m_attack(nymph)

        self.assertIn("she stole purple potion!", game.msgs)
        self.assertNotIn("She stole your purple potion!", game.msgs)

    def test_rogue_544_monster_attack_death_stops_before_special_effect(self):
        # Rogue 5.4.4 fight.c:attack() calls rip.c:death(), which exits before the special switch.
        game = new_game(seed=307)
        set_open_floor(game)
        potion = rogue.Item(rogue.CAT_POT, 0)
        game.p.inv = [potion]
        game.p.hp = 1
        nymph = monster_at(game.p.x + 1, game.p.y, "N", "nymph", damage="1x1", flags="steal_item")
        game.mons = [nymph]
        game.roll_monster_attack = lambda m: (True, 1)

        game.m_attack(nymph)

        self.assertEqual(game.p.hp, 0)
        self.assertIn(potion, game.p.inv)
        self.assertIn(nymph, game.mons)
        self.assertNotIn("she stole", " ".join(game.msgs))

    def test_rogue_544_rattlesnake_poison_reports_weakened_at_strength_floor(self):
        # Rogue 5.4.4 fight.c:attack() calls chg_str(-1), which clamps at 3, then still prints weakened text.
        import rogue_fight

        self.assertEqual(
            rogue_fight.poison_bite_strength(3, poison_saved=False, sustain_strength=False),
            (3, "weakened"),
        )

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

    def test_rogue_544_leprechaun_steal_rolls_goldcalc_before_magic_save(self):
        # Rogue 5.4.4 fight.c:attack() does purse -= GOLDCALC before save(VS_MAGIC).
        game = new_game(seed=304)
        set_open_floor(game)
        game.p.depth = 3
        game.p.gold = 100
        leprechaun = monster_at(game.p.x + 1, game.p.y, "L", "leprechaun", damage="0x0", flags="steal_gold")
        game.mons = [leprechaun]
        game.roll_monster_attack = lambda m: (True, 0)
        game.monster_hit_message = lambda name: "hit"
        events = []
        old_rnd = rogue.RNG.rnd
        old_save = game.save_vs_magic
        try:
            rogue.RNG.rnd = lambda n: events.append(f"rnd:{n}") or 0
            game.save_vs_magic = lambda: events.append("save") or True
            game.m_attack(leprechaun)
        finally:
            rogue.RNG.rnd = old_rnd
            game.save_vs_magic = old_save

        self.assertEqual(events[:2], ["rnd:80", "save"])

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

    def test_rogue_544_fight_helper_leprechaun_gold_loss_after_first(self):
        # Rogue 5.4.4 fight.c:attack() rolls save after the first purse -= GOLDCALC.
        import rogue_fight

        rolls = []
        self.assertEqual(
            rogue_fight.leprechaun_gold_loss_after_first(2, 3, magic_saved=False, goldcalc=lambda level: rolls.append(level) or 2),
            10,
        )
        self.assertEqual(rolls, [3, 3, 3, 3])

    def test_rogue_544_fight_helper_leprechaun_kill_gold_rolls_extra_on_saved_magic(self):
        # Rogue 5.4.4 fight.c:killed() gives GOLDCALC, plus four more when save(VS_MAGIC) succeeds.
        import rogue_fight

        rolls = []

        self.assertEqual(
            rogue_fight.leprechaun_kill_gold(3, magic_saved=True, goldcalc=lambda level: rolls.append(level) or 2),
            10,
        )
        self.assertEqual(rolls, [3, 3, 3, 3, 3])

    def test_rogue_544_fight_helper_leprechaun_kill_gold_after_first(self):
        # Rogue 5.4.4 fight.c:killed() rolls save after o_goldval = GOLDCALC.
        import rogue_fight

        rolls = []
        self.assertEqual(
            rogue_fight.leprechaun_kill_gold_after_first(2, 3, magic_saved=True, goldcalc=lambda level: rolls.append(level) or 2),
            10,
        )
        self.assertEqual(rolls, [3, 3, 3, 3])

    def test_rogue_544_fight_helper_leprechaun_kill_gold_gate_requires_max_depth_and_fallpos(self):
        # Rogue 5.4.4 fight.c:killed() requires fallpos(...) and level >= max_level before attaching gold.
        import rogue_fight

        self.assertTrue(rogue_fight.leprechaun_kill_gold_allowed(level=7, max_level=7, has_fallpos=True))
        self.assertFalse(rogue_fight.leprechaun_kill_gold_allowed(level=6, max_level=7, has_fallpos=True))
        self.assertFalse(rogue_fight.leprechaun_kill_gold_allowed(level=7, max_level=7, has_fallpos=False))

    def test_rogue_544_fallpos_can_choose_monster_occupied_places(self):
        # Rogue 5.4.4 weapons.c:fallpos() tests chat()==FLOOR/PASSAGE
        # while monsters live in p_monst; fall() updates t_oldch if needed.
        game = new_game(seed=3010)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        game.p.x, game.p.y = 20, 20
        game.tm[10][9] = rogue.T_FLOOR
        game.tm[10][11] = rogue.T_FLOOR
        game.mons = [monster_at(9, 10, "O", "orc", hp=10)]
        old_rnd = rogue.RNG.rnd
        try:
            rolls = iter([0, 1])
            rogue.RNG.rnd = lambda n: next(rolls)
            pos = game.fall_position(10, 10)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(pos, (9, 10))

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

    def test_rogue_544_killed_leprechaun_rolls_goldcalc_before_magic_save(self):
        # Rogue 5.4.4 fight.c:killed() sets o_goldval = GOLDCALC before save(VS_MAGIC).
        game = new_game(seed=3012)
        set_open_floor(game)
        game.p.depth = 3
        game.max_depth = 3
        leprechaun = monster_at(game.p.x + 1, game.p.y, "L", "leprechaun")
        game.mons = [leprechaun]
        events = []
        old_rnd = rogue.RNG.rnd
        old_save = game.save_vs_magic
        try:
            rogue.RNG.rnd = lambda n: events.append(f"rnd:{n}") or 0
            game.save_vs_magic = lambda: events.append("save") or False
            game.award_monster_kill(leprechaun)
        finally:
            rogue.RNG.rnd = old_rnd
            game.save_vs_magic = old_save

        self.assertEqual(events[:2], ["rnd:80", "save"])

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

    def test_rogue_544_do_chase_returns_minus_one_when_attack_removes_monster(self):
        # Rogue 5.4.4 fight.c:attack() returns -1 when Leprechaun/Nymph remove themselves.
        game = new_game(seed=304)
        set_open_floor(game)
        game.p.depth = 3
        game.p.gold = 10
        leprechaun = monster_at(game.p.x + 1, game.p.y, "L", "leprechaun", damage="0x0", flags="steal_gold")
        leprechaun.running = True
        game.mons = [leprechaun]
        game.roll_monster_attack = lambda m: (True, 0)
        game.save_vs_magic = lambda: True
        game.monster_hit_message = lambda name: "hit"

        result = game.do_chase(leprechaun)

        self.assertEqual(result, -1)
        self.assertNotIn(leprechaun, game.mons)

    def test_rogue_544_monster_attack_returns_zero_when_monster_remains(self):
        # Rogue 5.4.4 fight.c:attack() returns 0 when mp remains non-NULL.
        game = new_game(seed=305)
        set_open_floor(game)
        monster = monster_at(game.p.x + 1, game.p.y, "H", "hobgoblin", damage="0x0")
        game.mons = [monster]
        game.roll_monster_attack = lambda m: (True, 0)

        result = game.m_attack(monster)

        self.assertEqual(result, 0)
        self.assertIn(monster, game.mons)

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
            result = game.p_attack(xeroc)
        finally:
            game.roll_player_attack = old_roll_player_attack

        self.assertIs(result, False)
        self.assertEqual(calls, [])
        self.assertEqual(xeroc.hp, 40)
        self.assertEqual(xeroc.disguise, "X")
        self.assertIn("wait!  That's a xeroc!", game.msgs)

    def test_rogue_544_player_fight_returns_false_on_miss(self):
        # Rogue 5.4.4 fight.c:fight() returns did_hit, which is FALSE after a miss.
        game = new_game(seed=308)
        set_open_floor(game)
        monster = monster_at(game.p.x + 1, game.p.y, hp=40)
        game.roll_player_attack = lambda m, weap=None, thrown=False: (False, 0)

        result = game.p_attack(monster)

        self.assertIs(result, False)

    def test_rogue_544_player_fight_returns_true_on_hit(self):
        # Rogue 5.4.4 fight.c:fight() returns did_hit, which is TRUE after a hit.
        game = new_game(seed=309)
        set_open_floor(game)
        monster = monster_at(game.p.x + 1, game.p.y, hp=40)
        game.roll_player_attack = lambda m, weap=None, thrown=False: (True, 1)

        result = game.p_attack(monster)

        self.assertIs(result, True)

    def test_rogue_544_monster_attack_reveals_disguised_xeroc(self):
        # Rogue 5.4.4 fight.c:attack() also reveals attacking Xerocs before roll_em().
        game = new_game(seed=641)
        set_open_floor(game)
        xeroc = monster_at(game.p.x + 1, game.p.y, sym="X", name="xeroc", hp=40, level=7, armor=7, damage="4x4")
        xeroc.disguise = "?"
        game.roll_monster_attack = lambda monster: (False, 0)

        game.m_attack(xeroc)

        self.assertEqual(xeroc.disguise, "X")

    def test_rogue_544_blind_player_does_not_reveal_attacking_xeroc(self):
        # Rogue 5.4.4 fight.c:attack() gates attacking Xeroc reveal with !ISBLIND.
        game = new_game(seed=642)
        set_open_floor(game)
        game.p.blind = 5
        xeroc = monster_at(game.p.x + 1, game.p.y, sym="X", name="xeroc", hp=40, level=7, armor=7, damage="4x4")
        xeroc.disguise = "?"
        game.roll_monster_attack = lambda monster: (False, 0)

        game.m_attack(xeroc)

        self.assertEqual(xeroc.disguise, "?")

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
        x_rolls = iter(range(1, 7))
        y_rolls = iter([game.p.y + 1] * 6)
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
                if n == 10:
                    return 8
                if n == 78:
                    return next(x_rolls)
                if n == 20:
                    return next(y_rolls)
                return 0

            rogue.RNG.rnd = rnd
            rogue.make_item = lambda depth: rogue.Item(rogue.CAT_FOOD, 0)
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
        class TreasureGateRng:
            def __init__(self):
                self.treasure_gate = True

            def rnd(self, n):
                if n == rogue.rogue_dungeon.TREAS_ROOM and self.treasure_gate:
                    self.treasure_gate = False
                    return 0
                if n == 100:
                    return 99
                return 0

        try:
            rng = TreasureGateRng()
            rogue.RNG.rnd = rng.rnd
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

    def test_rogue544_put_things_interleaves_attempt_new_thing_and_floor(self):
        # Rogue 5.4.4 new_level.c:put_things() calls new_thing() and find_floor() inside each successful attempt.
        game = new_game(seed=3041)
        set_open_floor(game)
        events = []

        class PutThingsRng:
            def __init__(self):
                self.item_attempts = 0

            def rnd(self, n):
                events.append(f"rnd:{n}")
                if n == rogue.rogue_dungeon.TREAS_ROOM:
                    return 1
                if n == 100:
                    self.item_attempts += 1
                    return 0 if self.item_attempts == 1 else 99
                return 0

            def choice(self, seq):
                events.append("choice")
                return seq[0]

        old_rng = rogue.RNG
        old_make_game_item = game.make_game_item
        try:
            rogue.RNG = PutThingsRng()
            game.gitems = []
            game.make_game_item = lambda depth: events.append("new_thing") or rogue.Item(rogue.CAT_FOOD, 0)

            game._spawn_items()
        finally:
            rogue.RNG = old_rng
            game.make_game_item = old_make_game_item

        self.assertEqual(events[:6], ["rnd:20", "rnd:100", "new_thing", "rnd:1", "rnd:78", "rnd:20"])

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

    def test_rogue544_room_gold_rolls_goldcalc_before_find_floor(self):
        # Rogue 5.4.4 rooms.c:do_rooms() sets o_goldval = GOLDCALC before find_floor().
        game = new_game(seed=3042)
        set_open_floor(game)
        room = game.rooms[0]
        game.p.depth = 3
        events = []

        class GoldRng:
            def rnd(self, n):
                events.append(f"rnd:{n}")
                return 0

            def choice(self, seq):
                events.append("choice")
                return seq[0]

        old_rng = rogue.RNG
        old_usable_rooms = game.usable_rooms
        try:
            rogue.RNG = GoldRng()
            game.gitems = []
            game.usable_rooms = lambda: [room]

            game._spawn_room_gold()
        finally:
            rogue.RNG = old_rng
            game.usable_rooms = old_usable_rooms

        self.assertEqual(events[:4], ["rnd:2", "rnd:80", "rnd:78", "rnd:20"])

    def test_rogue544_room_gold_find_floor_uses_rnd_pos_not_candidate_choice(self):
        # Rogue 5.4.4 rooms.c:do_rooms() calls rooms.c:find_floor(),
        # which consumes rnd_pos() rolls instead of choosing from a candidate list.
        game = new_game(seed=30421)
        room = rogue.Room(5, 5, 5, 5)
        game.rooms = [room]
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for y in range(6, 9):
            for x in range(6, 9):
                game.tm[y][x] = rogue.T_FLOOR
        game.p.depth = 3
        game.p.x, game.p.y = 1, 1
        game.gitems = []
        game.mons = []

        class FindFloorRng:
            def __init__(self):
                self.values = [0, 0, 1, 2]
                self.calls = []

            def rnd(self, n):
                self.calls.append(n)
                return self.values.pop(0)

            def choice(self, seq):
                raise AssertionError("rooms.c:find_floor() should use rnd_pos(), not choice()")

        old_rng = rogue.RNG
        try:
            rng = FindFloorRng()
            rogue.RNG = rng
            game._spawn_room_gold()
        finally:
            rogue.RNG = old_rng

        self.assertEqual(rng.calls, [2, 80, 3, 3])
        self.assertEqual([(item.x, item.y) for item in game.gitems if item.cat == rogue.CAT_GOLD], [(7, 8)])

    def test_rogue544_find_floor_unlimited_has_no_fixed_retry_fallback(self):
        # Rogue 5.4.4 rooms.c:find_floor(..., limit=FALSE) loops until a matching square is found.
        game = new_game(seed=30423)
        room = rogue.Room(5, 5, 5, 5)
        game.rooms = [room]
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        game.tm[7][7] = rogue.T_FLOOR

        class FindFloorRng:
            def __init__(self):
                self.rolls = 0

            def rnd(self, n):
                self.rolls += 1
                if self.rolls <= (rogue.MAP_W * rogue.MAP_H + 1) * 2:
                    return 0
                return 1

        old_rng = rogue.RNG
        try:
            rogue.RNG = FindFloorRng()
            pos = game.find_floor_pos(room, limit=0, monst=False)
        finally:
            rogue.RNG = old_rng

        self.assertEqual(pos, (7, 7))

    def test_rogue544_rnd_room_retries_gone_rooms_until_usable(self):
        # Rogue 5.4.4 new_level.c:rnd_room() retries while the picked room has ISGONE.
        game = new_game(seed=30422)
        gone = rogue.Room(1, 1, 5, 5, flags={rogue.ROOM_GONE})
        usable = rogue.Room(10, 1, 5, 5)
        game.rooms = [gone, usable]

        class RndRoomRng:
            def __init__(self):
                self.values = [0] * 8 + [1]
                self.calls = []

            def rnd(self, n):
                self.calls.append(n)
                return self.values.pop(0)

        old_rng = rogue.RNG
        try:
            rng = RndRoomRng()
            rogue.RNG = rng
            picked = game.source_rnd_room()
        finally:
            rogue.RNG = old_rng

        self.assertIs(picked, usable)
        self.assertEqual(rng.calls, [2] * 9)

    def test_rogue544_room_gold_find_floor_uses_maze_passage(self):
        # Rogue 5.4.4 rooms.c:do_rooms() room gold uses find_floor(rp, ..., monst=FALSE).
        game = new_game(seed=3044)
        room = rogue.Room(5, 5, 5, 5, flags={rogue.ROOM_MAZE})
        game.rooms = [room]
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        game.tm[6][6] = rogue.T_FLOOR
        game.tm[6][7] = rogue.T_CORR
        game.p.x, game.p.y = 6, 6
        game.gitems = []
        game.mons = []

        class GoldRng:
            seen_x = False

            def rnd(self, n):
                if n == 3 and not self.seen_x:
                    self.seen_x = True
                    return 1
                return 0

            def choice(self, seq):
                return seq[0]

        old_rng = rogue.RNG
        try:
            rogue.RNG = GoldRng()
            game._spawn_room_gold()
        finally:
            rogue.RNG = old_rng

        self.assertEqual([(item.x, item.y) for item in game.gitems if item.cat == rogue.CAT_GOLD], [(7, 6)])

    def test_rogue544_put_things_find_floor_uses_maze_passage(self):
        # Rogue 5.4.4 new_level.c:put_things() object placement uses find_floor(..., monst=FALSE).
        game = new_game(seed=3045)
        room = rogue.Room(5, 5, 5, 5, flags={rogue.ROOM_MAZE})
        game.rooms = [room]
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        game.tm[6][6] = rogue.T_FLOOR
        game.tm[6][7] = rogue.T_CORR
        game.p.x, game.p.y = 6, 6
        game.gitems = []
        game.mons = []

        class PutThingsRng:
            def __init__(self):
                self.attempts = 0

            def rnd(self, n):
                if n == rogue.rogue_dungeon.TREAS_ROOM:
                    return 1
                if n == 100:
                    self.attempts += 1
                    return 0 if self.attempts == 1 else 99
                if n == 3 and not getattr(self, "seen_x", False):
                    self.seen_x = True
                    return 1
                return 0

            def choice(self, seq):
                return seq[0]

        old_rng = rogue.RNG
        old_make_game_item = game.make_game_item
        try:
            rogue.RNG = PutThingsRng()
            game.make_game_item = lambda depth: rogue.Item(rogue.CAT_FOOD, 0)
            game._spawn_items()
        finally:
            rogue.RNG = old_rng
            game.make_game_item = old_make_game_item

        self.assertEqual([(item.x, item.y) for item in game.gitems], [(7, 6)])

    def test_rogue544_treasure_room_items_find_floor_use_maze_passage(self):
        # Rogue 5.4.4 new_level.c:treas_room() treasure placement uses find_floor(rp, ..., FALSE).
        game = new_game(seed=3046)
        room = rogue.Room(5, 5, 5, 5, flags={rogue.ROOM_MAZE})
        game.rooms = [room]
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        game.tm[6][6] = rogue.T_FLOOR
        game.tm[6][7] = rogue.T_CORR
        game.p.x, game.p.y = 6, 6
        game.gitems = []
        game.mons = []
        old_counts = rogue.rogue_dungeon.treasure_room_counts
        old_choice = rogue.RNG.choice
        old_make_game_item = game.make_game_item
        try:
            rogue.rogue_dungeon.treasure_room_counts = lambda inner_area, rng: (1, 0)
            rogue.RNG.choice = lambda seq: seq[0]
            game.make_game_item = lambda depth: rogue.Item(rogue.CAT_FOOD, 0)
            game._spawn_treasure_room(room=room)
        finally:
            rogue.rogue_dungeon.treasure_room_counts = old_counts
            rogue.RNG.choice = old_choice
            game.make_game_item = old_make_game_item

        self.assertEqual([(item.x, item.y) for item in game.gitems], [(7, 6)])

    def test_rogue544_room_monster_gate_matches_do_rooms(self):
        # Rogue 5.4.4 rooms.c:do_rooms() uses 80% with gold in room, otherwise 25%.
        import rogue_dungeon

        self.assertTrue(rogue_dungeon.should_place_room_monster(SequenceRng([79]), True))
        self.assertFalse(rogue_dungeon.should_place_room_monster(SequenceRng([80]), True))
        self.assertTrue(rogue_dungeon.should_place_room_monster(SequenceRng([24]), False))
        self.assertFalse(rogue_dungeon.should_place_room_monster(SequenceRng([25]), False))

    def test_rogue544_io_helper_step_ok_matches_source_char_gate(self):
        # Rogue 5.4.4 io.c:step_ok() rejects spaces, walls, and alphabetic glyphs.
        import rogue_io

        for ch in (" ", "|", "-", "A", "z"):
            self.assertFalse(rogue_io.step_ok_char(ch))
        for ch in (".", "#", "+", "%", "^", "?", "!", "/", "=", ")", "]", ":", "*", "$", ","):
            self.assertTrue(rogue_io.step_ok_char(ch))

    def test_rogue544_io_helper_step_ok_tile_uses_tile_glyphs(self):
        # Rogue 5.4.4 io.c:step_ok() works on map glyphs returned by chat()/winat().
        import rogue_io

        self.assertFalse(rogue_io.step_ok_tile(rogue.T_VOID, rogue.TILE_CH))
        self.assertFalse(rogue_io.step_ok_tile(rogue.T_HWALL, rogue.TILE_CH))
        self.assertFalse(rogue_io.step_ok_tile(rogue.T_VWALL, rogue.TILE_CH))
        self.assertTrue(rogue_io.step_ok_tile(rogue.T_FLOOR, rogue.TILE_CH))
        self.assertTrue(rogue_io.step_ok_tile(rogue.T_DOOR, rogue.TILE_CH))
        self.assertTrue(rogue_io.step_ok_tile(rogue.T_TRAP, rogue.TILE_CH))

    def test_rogue544_find_floor_monster_candidates_match_rooms_find_floor_gate(self):
        # Rogue 5.4.4 rooms.c:find_floor(..., monst=TRUE) accepts step_ok() room cells.
        import rogue_dungeon

        room_a = object()
        room_b = object()
        tm = [
            [rogue.T_VOID, rogue.T_VOID, rogue.T_VOID, rogue.T_VOID],
            [rogue.T_VOID, rogue.T_FLOOR, rogue.T_STAIR, rogue.T_VOID],
            [rogue.T_VOID, rogue.T_TRAP, rogue.T_FLOOR, rogue.T_CORR],
        ]

        def room_at(x, y):
            if (x, y) in {(1, 1), (2, 1), (1, 2), (2, 2)}:
                return room_a
            if (x, y) == (3, 2):
                return room_b
            return None

        cands = rogue_dungeon.find_floor_monster_candidates(
            tm,
            room_at,
            occupied={(2, 2)},
            player_pos=(1, 1),
            tile_ch=rogue.TILE_CH,
            avoid={(1, 2)},
            excluded_room=room_b,
        )

        self.assertEqual(cands, [(2, 1)])

    def test_rogue544_find_floor_monster_candidates_use_step_ok_tile_gate(self):
        # Rogue 5.4.4 rooms.c:find_floor(..., monst=TRUE) gates through io.c:step_ok().
        import rogue_dungeon

        room = object()
        tm = [[rogue.T_HWALL, rogue.T_VWALL, rogue.T_FLOOR, rogue.T_DOOR]]

        def room_at(x, y):
            return room

        cands = rogue_dungeon.find_floor_monster_candidates(
            tm,
            room_at,
            occupied=set(),
            player_pos=(-1, -1),
            tile_ch=rogue.TILE_CH,
        )

        self.assertEqual(cands, [(2, 0), (3, 0)])

    def test_rogue544_find_floor_monster_candidates_can_scope_to_source_room(self):
        # Rogue 5.4.4 rooms.c:find_floor(rp, ...) only samples the supplied room.
        import rogue_dungeon

        room_a = object()
        room_b = object()
        tm = [[rogue.T_FLOOR, rogue.T_FLOOR]]

        def room_at(x, y):
            return room_a if x == 0 else room_b

        cands = rogue_dungeon.find_floor_monster_candidates(
            tm,
            room_at,
            occupied=set(),
            player_pos=(-1, -1),
            tile_ch=rogue.TILE_CH,
            only_room=room_b,
        )

        self.assertEqual(cands, [(1, 0)])

    def test_rogue544_find_floor_object_candidates_use_maze_passage_compchar(self):
        # Rogue 5.4.4 rooms.c:find_floor(..., monst=FALSE) uses PASSAGE for ISMAZE rooms.
        import rogue_dungeon

        normal = rogue.Room(0, 0, 3, 3)
        maze = rogue.Room(3, 0, 3, 3, flags={rogue.ROOM_MAZE})
        tm = [[rogue.T_FLOOR, rogue.T_CORR, rogue.T_VOID, rogue.T_FLOOR, rogue.T_CORR]]

        def room_at(x, y):
            return normal if x < 2 else maze if x >= 3 else None

        self.assertEqual(
            rogue_dungeon.find_floor_object_candidates(
                tm, room_at, rogue.T_FLOOR, rogue.T_CORR, only_room=normal
            ),
            [(0, 0)],
        )
        self.assertEqual(
            rogue_dungeon.find_floor_object_candidates(
                tm, room_at, rogue.T_FLOOR, rogue.T_CORR, only_room=maze
            ),
            [(4, 0)],
        )

    def test_rogue544_amulet_find_floor_can_place_in_maze_passage(self):
        # Rogue 5.4.4 new_level.c:put_things() places Amulet with find_floor(..., monst=FALSE).
        game = new_game(seed=3043)
        room = rogue.Room(5, 5, 5, 5, flags={rogue.ROOM_MAZE})
        game.rooms = [room]
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        game.tm[6][6] = rogue.T_CORR
        game.tm[6][7] = rogue.T_FLOOR
        game.p.depth = rogue.AMULET_LEVEL
        game.p.has_amulet = False
        game.p.x, game.p.y = 6, 7
        game.gitems = []
        game.mons = []
        old_choice = rogue.RNG.choice
        try:
            rogue.RNG.choice = lambda seq: seq[0]
            game._spawn_amulet()
        finally:
            rogue.RNG.choice = old_choice

        amulets = [item for item in game.gitems if item.cat == rogue.CAT_AMULET]
        self.assertEqual([(item.x, item.y) for item in amulets], [(6, 6)])

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
        old_choice = rogue.RNG.choice
        old_usable_rooms = game.usable_rooms
        old_random_monster_spec = game.random_monster_spec
        old_give_pack = game.give_pack
        try:
            game.mons = []
            game.gitems = []
            game.usable_rooms = lambda: [room]
            game.random_monster_spec = lambda depth: spec
            game.give_pack = lambda monster: None
            rogue.RNG.choice = lambda seq: next(pos for pos in seq if pos != (game.p.x, game.p.y))
            rogue.RNG.rnd = lambda n: 25 if n == 100 else 0
            game._spawn_mons()
            self.assertEqual(game.mons, [])

            rogue.RNG.rnd = lambda n: 24 if n == 100 else 0
            game._spawn_mons()
            self.assertEqual([m.sym for m in game.mons], ["E"])
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.RNG.choice = old_choice
            game.usable_rooms = old_usable_rooms
            game.random_monster_spec = old_random_monster_spec
            game.give_pack = old_give_pack

    def test_rogue544_spawn_mons_finds_floor_before_randmonster_false(self):
        # Rogue 5.4.4 rooms.c:do_rooms() calls find_floor(rp, ..., monst=TRUE) before randmonster(FALSE).
        game = new_game(seed=3304)
        set_open_floor(game)
        room = game.rooms[0]
        spec = next(s for s in rogue.BESTIARY if s.sym == "E")
        events = []

        class SpawnRng:
            def rnd(self, n):
                events.append(f"rnd:{n}")
                return 0

            def choice(self, seq):
                events.append("choice")
                return next(pos for pos in seq if pos != (game.p.x, game.p.y))

            def roll(self, number, sides):
                return 1

        old_rng = rogue.RNG
        old_usable_rooms = game.usable_rooms
        old_random_monster_spec = game.random_monster_spec
        old_give_pack = game.give_pack
        try:
            rogue.RNG = SpawnRng()
            game.mons = []
            game.gitems = []
            game.usable_rooms = lambda: [room]
            game.random_monster_spec = lambda depth: events.append("randmonster") or spec
            game.give_pack = lambda monster: None

            game._spawn_mons()
        finally:
            rogue.RNG = old_rng
            game.usable_rooms = old_usable_rooms
            game.random_monster_spec = old_random_monster_spec
            game.give_pack = old_give_pack

        self.assertEqual(events[:4], ["rnd:100", "rnd:78", "rnd:20", "randmonster"])

    def test_rogue_544_killed_monster_pack_items_use_fallpos(self):
        # Rogue 5.4.4 fight.c:remove_mon(..., TRUE) sets o_pos to t_pos,
        # then calls weapons.c:fall(FALSE), which uses fallpos().
        game = new_game(seed=302)
        set_open_floor(game)
        monster = monster_at(game.p.x + 1, game.p.y)
        item = rogue.Item(rogue.CAT_FOOD, 0)
        monster.pack = [item]
        game.mons = [monster]
        fall_calls = []
        old_fall_position = game.fall_position
        try:
            game.fall_position = lambda x, y: fall_calls.append((x, y)) or (monster.x + 1, monster.y)

            game.award_monster_kill(monster)
        finally:
            game.fall_position = old_fall_position

        self.assertNotIn(monster, game.mons)
        self.assertEqual(monster.pack, [])
        self.assertIn(item, game.gitems)
        self.assertEqual(fall_calls, [(monster.x, monster.y)])
        self.assertEqual((item.x, item.y), (monster.x + 1, monster.y))

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
        # Rogue 5.4.4 weapons.c:init_dam[] and extern.c:weap_info[].
        self.assertEqual(rogue.WEAPONS[0]["damage"], "2x4")
        self.assertEqual(rogue.WEAPONS[0]["hurl_damage"], "1x3")
        self.assertEqual(rogue.WEAPONS[3]["damage"], "1x1")
        self.assertEqual(rogue.WEAPONS[3]["hurl_damage"], "2x3")
        self.assertEqual(rogue.WEAPONS[3]["launcher"], 2)
        self.assertTrue(rogue.WEAPONS[3]["missile"])
        self.assertEqual([w["worth"] for w in rogue.WEAPONS], [8, 15, 15, 1, 3, 75, 2, 5, 5])

    def test_rogue_544_armor_table_worth_matches_source(self):
        # Rogue 5.4.4 extern.c:arm_info[] oi_worth values are needed by rip.c:total_winner().
        self.assertEqual([a["worth"] for a in rogue.ARMORS], [5, 30, 15, 3, 75, 80, 90, 150])

    def test_rogue_544_weapons_helper_init_dam_table_matches_source(self):
        # Rogue 5.4.4 weapons.c:init_dam[] lives in rogue_weapons.py.
        import rogue_weapons

        self.assertEqual(rogue_weapons.INIT_DAM[0], ("2x4", "1x3", None, ()))
        self.assertEqual(rogue_weapons.INIT_DAM[3], ("1x1", "2x3", 2, ("many", "missile")))

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

    def test_rogue_544_fight_helper_roll_damage_expr_requires_x_separator(self):
        # Rogue 5.4.4 fight.c:roll_em() searches for 'x'; dice-style 'd' is not a combat damage separator.
        import rogue_fight

        rolls = []

        self.assertEqual(rogue_fight.roll_damage_expr("1d4", lambda n, sides: rolls.append((n, sides)) or 4), 0)
        self.assertEqual(rolls, [])

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

    def test_rogue_544_player_unarmed_damage_uses_init_stats(self):
        # Rogue 5.4.4 extern.c:INIT_STATS gives the player s_dmg "1x4".
        game = new_game(seed=605)

        damage_expr, hplus, dplus = game.player_weapon_profile(None, False)

        self.assertEqual(damage_expr, "1x4")
        self.assertEqual(hplus, 0)
        self.assertEqual(dplus, 0)

    def test_rogue_544_fight_helper_bare_attack_profile_matches_roll_em_null_weapon(self):
        # Rogue 5.4.4 fight.c:roll_em() uses attacker s_dmg and zero pluses when weap == NULL.
        import rogue_fight

        self.assertEqual(rogue_fight.bare_attack_profile("1x4"), ("1x4", 0, 0))

    def test_rogue_544_non_weapon_throw_uses_new_thing_zero_damage(self):
        # Rogue 5.4.4 things.c:new_thing() initializes non-weapons with o_damage/o_hurldmg = "0x0".
        game = new_game(seed=5053)
        potion = rogue.Item(rogue.CAT_POT, 0)

        damage_expr, hplus, dplus = game.player_weapon_profile(potion, thrown=True)

        self.assertEqual(damage_expr, "0x0")
        self.assertEqual(hplus, 0)
        self.assertEqual(dplus, 0)

    def test_rogue_544_fight_helper_non_weapon_profile_keeps_current_item_ring_bonus(self):
        # Rogue 5.4.4 fight.c:roll_em() still applies current-weapon rings before using o_damage "0x0".
        import rogue_fight

        self.assertEqual(rogue_fight.non_weapon_profile(2, 3), ("0x0", 2, 3))

    def test_rogue_544_wielded_non_weapon_gets_ring_hit_and_damage_bonus(self):
        # Rogue 5.4.4 fight.c:roll_em() applies R_ADDHIT/R_ADDDAM when weap == cur_weapon.
        import rogue_rings

        game = new_game(seed=5066)
        potion = rogue.Item(rogue.CAT_POT, 0)
        game.p.inv.append(potion)
        game.p.wpn = potion
        game.p.ring_l = rogue.Item(rogue.CAT_RING, rogue_rings.R_ADDHIT, ench=2)
        game.p.ring_r = rogue.Item(rogue.CAT_RING, rogue_rings.R_ADDDAM, ench=3)

        damage_expr, hplus, dplus = game.player_weapon_profile(potion, thrown=False)

        self.assertEqual(damage_expr, "0x0")
        self.assertEqual(hplus, 2)
        self.assertEqual(dplus, 3)

    def test_rogue_544_wielded_stick_uses_fix_stick_damage_profile(self):
        # Rogue 5.4.4 sticks.c:fix_stick() gives staff "2x3" and wand "1x1" o_damage.
        import rogue_rings
        import rogue_sticks

        game = new_game(seed=5067)
        staff = rogue.Item(rogue.CAT_STICK, rogue_sticks.WS_LIGHT)
        game.ident.wtypes[rogue_sticks.WS_LIGHT] = "staff"
        game.p.wpn = staff
        game.p.ring_l = rogue.Item(rogue.CAT_RING, rogue_rings.R_ADDHIT, ench=2)
        game.p.ring_r = rogue.Item(rogue.CAT_RING, rogue_rings.R_ADDDAM, ench=3)

        damage_expr, hplus, dplus = game.player_weapon_profile(staff, thrown=False)

        self.assertEqual(damage_expr, "2x3")
        self.assertEqual(hplus, 2)
        self.assertEqual(dplus, 3)

    def test_rogue_544_thrown_current_weapon_gets_ring_hit_and_damage_bonus(self):
        # Rogue 5.4.4 fight.c:roll_em() applies cur_weapon ring bonuses before hurl handling.
        import rogue_rings

        game = new_game(seed=5067)
        dagger = rogue.Item(rogue.CAT_WPN, next(i for i, w in enumerate(rogue.WEAPONS) if w["name"] == "dagger"))
        game.p.wpn = dagger
        game.p.ring_l = rogue.Item(rogue.CAT_RING, rogue_rings.R_ADDHIT, ench=2)
        game.p.ring_r = rogue.Item(rogue.CAT_RING, rogue_rings.R_ADDDAM, ench=3)

        damage_expr, hplus, dplus = game.player_weapon_profile(dagger, thrown=True)

        self.assertEqual(damage_expr, dagger.data["hurl_damage"])
        self.assertEqual(hplus, dagger.hit_plus + 2)
        self.assertEqual(dplus, dagger.dam_plus + 3)

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

    def test_rogue_544_fight_helper_roll_em_damage_stops_before_malformed_part(self):
        # Rogue 5.4.4 fight.c:roll_em() breaks before swing() when a damage part has no 'x'.
        import rogue_fight

        swings = []
        hit, damage = rogue_fight.roll_em_damage(
            "1x1/bad/1x1",
            swing=lambda: swings.append(True) or True,
            roll_part=lambda part: 1,
            dplus=0,
            add_dam=0,
        )

        self.assertTrue(hit)
        self.assertEqual(damage, 1)
        self.assertEqual(swings, [True])

    def test_rogue_544_fight_helper_damage_expr_uses_atoi_prefixes(self):
        # Rogue 5.4.4 fight.c:roll_em() parses ndice/nsides with atoi(), then searches for '/'.
        import rogue_fight

        rolls = []

        self.assertEqual(
            rogue_fight.roll_damage_expr(
                "1x4junk/2x3more",
                lambda n, sides: rolls.append((n, sides)) or n * sides,
            ),
            10,
        )
        self.assertEqual(rolls, [(1, 4), (2, 3)])

    def test_rogue_544_fight_helper_roll_em_damage_uses_atoi_prefixes(self):
        # Rogue 5.4.4 fight.c:roll_em() lets atoi("4junk") mean 4 before the next '/'.
        import rogue_fight

        rolls = []
        hit, damage = rogue_fight.roll_em_damage(
            "1x4junk/1x2",
            swing=lambda: True,
            roll_part=lambda part: rogue_fight.roll_damage_expr(
                part, lambda n, sides: rolls.append((n, sides)) or n * sides
            ),
            dplus=0,
            add_dam=0,
        )

        self.assertTrue(hit)
        self.assertEqual(damage, 6)
        self.assertEqual(rolls, [(1, 4), (1, 2)])

    def test_rogue_544_fight_helper_roll_em_part_damage_clamps_negative(self):
        # Rogue 5.4.4 fight.c:roll_em() subtracts max(0, dplus + proll + add_dam[s_str]).
        import rogue_fight

        self.assertEqual(rogue_fight.roll_em_part_damage(1, dplus=-8, add_dam=2), 0)
        self.assertEqual(rogue_fight.roll_em_part_damage(4, dplus=1, add_dam=2), 7)

    def test_rogue_544_fight_helper_attack_pluses_include_strength_tables(self):
        # Rogue 5.4.4 fight.c:roll_em() adds str_plus/add_dam after defender !ISRUN and base dplus.
        import rogue_fight

        self.assertEqual(rogue_fight.attack_hit_plus(1, defender_running=False, strength=18), 6)
        self.assertEqual(rogue_fight.attack_damage_plus(2, strength=18), 4)

    def test_rogue_544_monsters_default_to_strength_10_for_roll_em(self):
        # Rogue 5.4.4 extern.c:monsters[] uses XX=10 for monster s_str, giving no str_plus/add_dam.
        monster = monster_at(1, 1)

        self.assertEqual(monster.strength, 10)

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

    def test_rogue_544_bear_trap_no_move_does_not_give_monster_plus_four(self):
        # Rogue 5.4.4 move.c:T_BEAR sets no_move but does not clear player ISRUN.
        game = new_game(seed=9)
        set_open_floor(game)
        game.p.no_move = 1
        monster = monster_at(game.p.x + 1, game.p.y, damage="1x1")
        seen_wplus = []
        game.swing_hits = lambda at_lvl, op_arm, wplus: seen_wplus.append(wplus) or False

        game.roll_monster_attack(monster)

        self.assertEqual(seen_wplus, [0])

    def test_rogue_544_fight_helper_hit_plus_adds_four_when_defender_not_running(self):
        # Rogue 5.4.4 fight.c:roll_em() adds +4 when !ISRUN on the defender.
        import rogue_fight

        self.assertEqual(rogue_fight.hit_plus_vs_defender(0, defender_running=False), 4)
        self.assertEqual(rogue_fight.hit_plus_vs_defender(2, defender_running=True), 2)

    def test_rogue_544_fight_helper_combat_message_key_uses_rnd_family_size(self):
        # Rogue 5.4.4 fight.c:hit()/miss() chooses one of four h_names/m_names with rnd(4).
        import rogue_fight

        calls = []
        key = rogue_fight.combat_message_key(
            ("hit0", "hit1", "hit2", "hit3"),
            lambda n: calls.append(n) or 2,
        )

        self.assertEqual(key, "hit2")
        self.assertEqual(calls, [4])

    def test_rogue_544_fight_helper_combat_message_key_does_not_depend_on_tuple_length(self):
        # Rogue 5.4.4 fight.c:hit()/miss() uses rnd(4), not the Python tuple length.
        import rogue_fight

        calls = []
        key = rogue_fight.combat_message_key(
            ("hit0", "hit1", "hit2", "hit3", "extra"),
            lambda n: calls.append(n) or 3,
        )

        self.assertEqual(key, "hit3")
        self.assertEqual(calls, [4])

    def test_rogue_544_fight_helper_prname_formats_player_and_monster_names(self):
        # Rogue 5.4.4 fight.c:prname() uses "you" for NULL and uppercases the first character when requested.
        import rogue_fight

        self.assertEqual(rogue_fight.prname(None, upper=False), "you")
        self.assertEqual(rogue_fight.prname(None, upper=True), "You")
        self.assertEqual(rogue_fight.prname("the rattlesnake", upper=True), "The rattlesnake")

    def test_rogue_544_fight_helper_player_defense_armor_matches_roll_em(self):
        # Rogue 5.4.4 fight.c:roll_em() uses current armor o_arm, then subtracts protection rings.
        import rogue_fight

        self.assertEqual(rogue_fight.player_defense_armor(10, armor_ac=None, protection_bonus=0), 10)
        self.assertEqual(rogue_fight.player_defense_armor(10, armor_ac=4, protection_bonus=2), 2)

    def test_rogue_544_fight_helper_player_defender_running_ignores_no_move(self):
        # Rogue 5.4.4 no_command clears ISRUN; move.c:T_BEAR no_move does not.
        import rogue_fight

        self.assertFalse(rogue_fight.player_defender_running(no_command=1))
        self.assertTrue(rogue_fight.player_defender_running(no_command=0))

    def test_rogue_544_fight_helper_monster_attack_message_gate_skips_ice(self):
        # Rogue 5.4.4 fight.c:attack() skips hit()/miss() for Ice monster.
        import rogue_fight

        self.assertFalse(rogue_fight.monster_attack_message_allowed("I"))
        self.assertTrue(rogue_fight.monster_attack_message_allowed("R"))

    def test_rogue_544_fight_helper_attack_activity_reset_matches_source(self):
        # Rogue 5.4.4 fight.c:fight()/attack() clear running/count and set quiet = 0.
        import rogue_fight

        self.assertEqual(rogue_fight.attack_activity_state(), (False, 0))

    def test_rogue_544_fight_helper_attack_special_gate_matches_iscanc(self):
        # Rogue 5.4.4 fight.c:attack() runs the special switch only when !ISCANC.
        import rogue_fight

        self.assertTrue(rogue_fight.attack_specials_allowed(cancelled=False))
        self.assertFalse(rogue_fight.attack_specials_allowed(cancelled=True))

    def test_rogue_544_fight_helper_attack_result_matches_removed_monster(self):
        # Rogue 5.4.4 fight.c:attack() returns -1 when remove_mon() sets mp = NULL.
        import rogue_fight

        self.assertEqual(rogue_fight.attack_result(monster_removed=True), -1)
        self.assertEqual(rogue_fight.attack_result(monster_removed=False), 0)

    def test_rogue_544_fight_helper_remove_mon_pack_falls_only_on_kill(self):
        # Rogue 5.4.4 fight.c:remove_mon() falls t_pack only when waskill is TRUE.
        import rogue_fight

        self.assertTrue(rogue_fight.remove_monster_pack_should_fall(was_kill=True))
        self.assertFalse(rogue_fight.remove_monster_pack_should_fall(was_kill=False))

    def test_rogue_544_fight_helper_attack_reveals_disguised_xeroc_when_not_blind(self):
        # Rogue 5.4.4 fight.c:fight()/attack() reveal X when t_disguise != 'X' and !ISBLIND.
        import rogue_fight

        self.assertTrue(rogue_fight.attack_reveals_disguised_xeroc(disguised=True, blind=False))
        self.assertFalse(rogue_fight.attack_reveals_disguised_xeroc(disguised=True, blind=True))
        self.assertFalse(rogue_fight.attack_reveals_disguised_xeroc(disguised=False, blind=False))

    def test_rogue_544_fight_helper_revealed_xeroc_stops_only_melee(self):
        # Rogue 5.4.4 fight.c:fight() returns FALSE after Xeroc reveal only when !thrown.
        import rogue_fight

        self.assertTrue(rogue_fight.revealed_xeroc_stops_attack(thrown=False))
        self.assertFalse(rogue_fight.revealed_xeroc_stops_attack(thrown=True))

    def test_rogue_544_fight_helper_confusion_message_requires_canhuh_hit_and_sight(self):
        # Rogue 5.4.4 fight.c:fight() uses did_hit && !ISBLIND for the appears-confused message.
        import rogue_fight

        self.assertTrue(rogue_fight.confusion_message_allowed(confused_by_hit=True, blind=False))
        self.assertFalse(rogue_fight.confusion_message_allowed(confused_by_hit=True, blind=True))
        self.assertFalse(rogue_fight.confusion_message_allowed(confused_by_hit=False, blind=False))

    def test_rogue_544_fight_helper_confusion_hit_effect(self):
        # Rogue 5.4.4 fight.c:fight() consumes CANHUH on a successful hit.
        import rogue_fight

        self.assertEqual(rogue_fight.confusion_hit_effect(True), (False, True))
        self.assertEqual(rogue_fight.confusion_hit_effect(False), (False, False))

    def test_rogue_544_fight_helper_thrown_message_weapon_gate(self):
        # Rogue 5.4.4 fight.c:thunk()/bounce() use "the item" only for WEAPON objects.
        import rogue_fight

        self.assertTrue(rogue_fight.thrown_message_uses_weapon_name(rogue.CAT_WPN))
        self.assertFalse(rogue_fight.thrown_message_uses_weapon_name(rogue.CAT_STICK))

    def test_rogue_544_fight_helper_thrown_message_key_matches_thunk_bounce(self):
        # Rogue 5.4.4 fight.c:thunk()/bounce() split WEAPON and non-WEAPON messages.
        import rogue_fight

        self.assertEqual(rogue_fight.thrown_message_key(rogue.CAT_WPN, hit=True), "fight.thrown_weapon_hits")
        self.assertEqual(rogue_fight.thrown_message_key(rogue.CAT_WPN, hit=False), "fight.thrown_weapon_misses")
        self.assertEqual(rogue_fight.thrown_message_key(rogue.CAT_STICK, hit=True), "fight.you_hit_target")
        self.assertEqual(rogue_fight.thrown_message_key(rogue.CAT_STICK, hit=False), "fight.you_missed_target")

    def test_rogue_544_fight_helper_killed_message_key_matches_normal_non_terse(self):
        # Rogue 5.4.4 fight.c:killed() prints "you have defeated" for normal non-terse kills.
        import rogue_fight

        self.assertEqual(
            rogue_fight.killed_message_key(pr=True, has_hit=False, terse=False),
            "fight.you_have_defeated_target",
        )

    def test_rogue_544_fight_helper_killed_exp_adds_monster_exp(self):
        # Rogue 5.4.4 fight.c:killed() does pstats.s_exp += tp->t_stats.s_exp.
        import rogue_fight

        self.assertEqual(rogue_fight.killed_experience(20, 55), 75)

    def test_rogue_544_fight_helper_weapon_profile_uses_hurl_damage_and_launcher_pluses(self):
        # Rogue 5.4.4 fight.c:roll_em() uses o_hurldmg and adds launcher pluses for matching missiles.
        import rogue_fight

        damage, hplus, dplus = rogue_fight.weapon_profile(
            weapon={"damage": "1x1", "hurl_damage": "2x3", "missile": True, "launcher": 2},
            hit_plus=1,
            dam_plus=2,
            thrown=True,
            ring_hit_bonus=0,
            ring_damage_bonus=0,
            launcher_kind=2,
            launcher_hit_plus=3,
            launcher_dam_plus=4,
        )

        self.assertEqual((damage, hplus, dplus), ("2x3", 4, 6))

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
        game.dash_steps = 4
        game.p.quiet = 19
        game.p_attack(player_target)
        self.assertFalse(game.dashing)
        self.assertEqual(game.dash_steps, 0)
        self.assertEqual(game.p.quiet, 0)

        monster = monster_at(game.p.x + 1, game.p.y, hp=20, damage="1x1")
        game.dashing = True
        game.dash_steps = 4
        game.p.quiet = 19
        game.m_attack(monster)
        self.assertFalse(game.dashing)
        self.assertEqual(game.dash_steps, 0)
        self.assertEqual(game.p.quiet, 0)

    def test_rogue_544_player_kill_message_uses_you_have_defeated(self):
        # Rogue 5.4.4 fight.c:killed() uses "you have defeated" after a normal non-terse player hit.
        game = new_game(seed=5036)
        set_open_floor(game)
        monster = monster_at(game.p.x + 1, game.p.y, "H", "hobgoblin", hp=1)
        game.mons = [monster]
        game.roll_player_attack = lambda m, weap=None, thrown=False: (True, 1)

        game.p_attack(monster)

        self.assertIn("you have defeated the hobgoblin", game.msgs)

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

    def test_rogue544_generated_seed_sample_has_one_reachable_stair(self):
        # Rogue 5.4.4 new_level.c:new_level() places stairs after passages/traps,
        # and passages.c:do_passages() connects the 3x3 room graph.
        for seed in range(64):
            with self.subTest(seed=seed):
                game = new_game(seed=seed)
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

    def test_rogue544_dungeon_generation_does_not_add_non_source_ensure_passages(self):
        # Rogue 5.4.4 new_level.c:new_level() calls rooms.c:do_rooms(), then passages.c:do_passages();
        # it does not dig a post-passages repair connection.
        random.seed(3)
        edge_counts = []
        conn_calls = []
        old_edges = rogue.DGen._passage_edges
        old_conn = rogue.DGen._conn

        def record_edges(*args, **kwargs):
            edges = old_edges(*args, **kwargs)
            edge_counts.append(len(edges))
            return edges

        def record_conn(tm, r1, r2, horiz=None):
            conn_calls.append((r1, r2, horiz))
            return old_conn(tm, r1, r2, horiz)

        try:
            rogue.DGen._passage_edges = record_edges
            rogue.DGen._conn = record_conn
            rogue.DGen.gen(depth=5)
        finally:
            rogue.DGen._passage_edges = old_edges
            rogue.DGen._conn = old_conn

        self.assertEqual(len(conn_calls), edge_counts[0])

    def test_rogue544_passage_conn_uses_rnd_turn_spot_not_randint(self):
        # Rogue 5.4.4 passages.c:conn() uses turn_spot = rnd(distance - 1) + 1.
        left = rogue.Room(2, 2, 5, 5)
        right = rogue.Room(16, 2, 5, 5)
        tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        rogue.DGen._room(tm, left)
        rogue.DGen._room(tm, right)
        old_pick = rogue.DGen._pick_wall_door
        old_rnd = rogue.RNG.rnd
        old_randint = rogue.RNG.randint
        try:
            rogue.DGen._pick_wall_door = staticmethod(
                lambda _tm, room, side: (room.x + room.w - 1, room.y + 2)
                if side == "R"
                else (room.x, room.y + 4)
            )
            rogue.RNG.rnd = lambda n: 0
            rogue.RNG.randint = lambda a, b: (_ for _ in ()).throw(AssertionError("randint used"))

            rogue.DGen._conn(tm, left, right, True)
        finally:
            rogue.DGen._pick_wall_door = old_pick
            rogue.RNG.rnd = old_rnd
            rogue.RNG.randint = old_randint

        self.assertEqual(tm[left.y + 2][left.x + left.w], rogue.T_CORR)
        self.assertEqual(tm[left.y + 4][right.x - 1], rogue.T_CORR)

    def test_rogue544_passage_conn_uses_rnd_door_positions_not_shuffle(self):
        # Rogue 5.4.4 passages.c:conn() picks door offsets with rnd(room size - 2), not shuffle/retry.
        left = rogue.Room(2, 2, 5, 5)
        right = rogue.Room(16, 2, 5, 5)
        tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        rogue.DGen._room(tm, left)
        rogue.DGen._room(tm, right)
        values = iter([0, 2, 0])
        old_rnd = rogue.RNG.rnd
        old_shuffle = rogue.RNG.shuffle
        try:
            rogue.RNG.rnd = lambda n: next(values)
            rogue.RNG.shuffle = lambda seq: (_ for _ in ()).throw(AssertionError("shuffle used"))

            rogue.DGen._conn(tm, left, right, True)
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.RNG.shuffle = old_shuffle

        self.assertEqual(tm[left.y + 1][left.x + left.w - 1], rogue.T_DOOR)
        self.assertEqual(tm[right.y + 3][right.x], rogue.T_DOOR)

    def test_rogue544_passage_conn_normalizes_reversed_horizontal_edges(self):
        # Rogue 5.4.4 passages.c:conn() normalizes r1/r2 to the lower room index,
        # so reversed horizontal edges still consume door RNG left-to-right.
        left = rogue.Room(2, 2, 5, 5)
        right = rogue.Room(16, 2, 5, 5)
        tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        rogue.DGen._room(tm, left)
        rogue.DGen._room(tm, right)
        values = iter([0, 2, 0])
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: next(values)

            rogue.DGen._conn(tm, right, left, True)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(tm[left.y + 1][left.x + left.w - 1], rogue.T_DOOR)
        self.assertEqual(tm[right.y + 3][right.x], rogue.T_DOOR)

    def test_rogue544_passage_conn_normalizes_reversed_vertical_edges(self):
        # Rogue 5.4.4 passages.c:conn() normalizes r1/r2 before a down connection,
        # so reversed vertical edges still consume door RNG top-to-bottom.
        top = rogue.Room(10, 2, 5, 5)
        bottom = rogue.Room(10, 12, 5, 5)
        tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        rogue.DGen._room(tm, top)
        rogue.DGen._room(tm, bottom)
        values = iter([0, 2, 0])
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: next(values)

            rogue.DGen._conn(tm, bottom, top, False)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(tm[top.y + top.h - 1][top.x + 1], rogue.T_DOOR)
        self.assertEqual(tm[bottom.y][bottom.x + 3], rogue.T_DOOR)

    def test_rogue544_passage_conn_hides_secret_doors_during_door_call(self):
        # Rogue 5.4.4 passages.c:door() runs the secret-door gate during conn(), not in a later map scan.
        left = rogue.Room(2, 2, 5, 5)
        right = rogue.Room(16, 2, 5, 5)
        tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        hidden = {}
        rogue.DGen._room(tm, left)
        rogue.DGen._room(tm, right)
        values = iter([0, 0, 0, 0, 0, 9])
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: next(values, 9)

            rogue.DGen._conn(tm, left, right, True, depth=2, hidden_tiles=hidden)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(hidden[(left.x + left.w - 1, left.y + 1)], rogue.T_DOOR)
        self.assertEqual(tm[left.y + 1][left.x + left.w - 1], rogue.T_VWALL)
        self.assertEqual(tm[right.y + 1][right.x], rogue.T_DOOR)

    def test_rogue544_passage_conn_hides_gone_room_putpass_during_conn(self):
        # Rogue 5.4.4 passages.c:conn() uses putpass(), not door(), for gone rooms.
        gone = rogue.Room(2, 2, 1, 1, flags={rogue.ROOM_GONE})
        right = rogue.Room(16, 2, 5, 5)
        tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        hidden = {}
        rogue.DGen._room(tm, right)
        values = iter([0, 0, 0, 0, 9])
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: next(values, 9)

            rogue.DGen._conn(tm, gone, right, True, depth=2, hidden_tiles=hidden)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(hidden[(gone.x, gone.y)], rogue.T_CORR)
        self.assertEqual(tm[gone.y][gone.x], rogue.T_VOID)

    def test_rogue544_descend_uses_passages_secret_timing_not_post_scan(self):
        # Rogue 5.4.4 new_level.c calls passages.c:do_passages(); secrets are decided in door()/putpass().
        game = new_game(seed=3050)
        game._spawn_room_gold = lambda: None
        game._spawn_mons = lambda: None
        game._populate_initial_room = lambda room: None
        game._spawn_items = lambda: None
        game._spawn_amulet = lambda: None
        game._spawn_traps = lambda: None
        game._hide_secret_features = lambda: (_ for _ in ()).throw(AssertionError("post scan used"))
        positions = iter([(5, 5), (6, 5)])
        game.find_floor_pos = lambda *a, **kw: next(positions)

        game.descend()

        self.assertEqual((game.p.x, game.p.y), (6, 5))

    def test_rogue544_passage_conn_maze_exit_uses_wall_rnd_retry(self):
        # Rogue 5.4.4 passages.c:conn() retries rnd(room size - 2) wall positions
        # while an ISMAZE room side coordinate is not F_PASS.
        maze = rogue.Room(10, 5, 7, 7, flags={rogue.ROOM_MAZE})
        tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        tm[maze.y + 2][maze.x + maze.w - 1] = rogue.T_CORR
        rnd_values = iter([0, 1])
        old_rnd = rogue.RNG.rnd
        old_choice = rogue.RNG.choice
        try:
            rogue.RNG.rnd = lambda n: next(rnd_values)
            rogue.RNG.choice = lambda seq: (_ for _ in ()).throw(AssertionError("choice used"))

            self.assertEqual(rogue.DGen._maze_exit(tm, maze, "R"), (maze.x + maze.w - 1, maze.y + 2))
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.RNG.choice = old_choice

    def test_rogue544_passage_conn_maze_exit_has_no_fixed_retry_fallback(self):
        # Rogue 5.4.4 passages.c:conn() uses a do/while loop with no retry cap
        # while an ISMAZE room side coordinate is not F_PASS.
        maze = rogue.Room(10, 5, 7, 7, flags={rogue.ROOM_MAZE})
        tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        tm[maze.y + 2][maze.x + maze.w - 1] = rogue.T_CORR
        rnd_values = iter([0] * 20 + [1])
        old_rnd = rogue.RNG.rnd
        old_choice = rogue.RNG.choice
        try:
            rogue.RNG.rnd = lambda n: next(rnd_values)
            rogue.RNG.choice = lambda seq: (_ for _ in ()).throw(AssertionError("choice used"))

            self.assertEqual(rogue.DGen._maze_exit(tm, maze, "R"), (maze.x + maze.w - 1, maze.y + 2))
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.RNG.choice = old_choice

    def test_rogue544_passage_conn_records_maze_room_exit_for_ai(self):
        # Rogue 5.4.4 passages.c:door() records room.r_exit before returning for ISMAZE.
        game = new_game(seed=524)
        maze = rogue.Room(10, 5, 7, 7, flags={rogue.ROOM_MAZE})
        game.rooms = [maze]
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        game.tm[maze.y + 2][maze.x + maze.w - 1] = rogue.T_CORR
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1

            rogue.DGen._exit(game.tm, maze, "R")
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertIn((maze.x + maze.w - 1, maze.y + 2), game.room_exits(maze))

    def test_rogue544_maze_room_uses_even_rnd_start_not_choice(self):
        # Rogue 5.4.4 rooms.c:do_maze() starts at (rnd(r_max)/2)*2 from room origin.
        maze = rogue.Room(10, 5, 7, 7, flags={rogue.ROOM_MAZE})
        tm = [[rogue.T_FLOOR for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        values = iter([0, 0, 0, 1])
        old_rnd = rogue.RNG.rnd
        old_choice = rogue.RNG.choice
        try:
            rogue.RNG.rnd = lambda n: next(values, 0)
            rogue.RNG.choice = lambda seq: (_ for _ in ()).throw(AssertionError("choice used"))

            rogue.DGen._maze_room(tm, maze)
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.RNG.choice = old_choice

        self.assertEqual(tm[maze.y][maze.x], rogue.T_CORR)
        self.assertEqual(tm[maze.y + 1][maze.x], rogue.T_CORR)
        self.assertEqual(tm[maze.y + 2][maze.x], rogue.T_CORR)

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

    def test_rogue_544_corridor_look_blocks_diagonal_behind_hidden_passage(self):
        # Rogue 5.4.4 misc.c:look() skips blank cells and blocks diagonal passage sight
        # when both orthogonal side cells fail io.c:step_ok().
        game = new_game(seed=141)
        game.rooms = []
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        game.p.x, game.p.y = 10, 10
        game.tm[10][10] = rogue.T_CORR
        game.tm[9][10] = rogue.T_VOID
        game.hidden_tiles[(10, 9)] = rogue.T_CORR
        game.tm[10][11] = rogue.T_VOID
        game.tm[9][11] = rogue.T_CORR

        game.update_fov()

        self.assertIn((10, 10), game.visible)
        self.assertNotIn((10, 9), game.visible)
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

    def test_rogue_544_gold_inv_name_uses_gold_value(self):
        # Rogue 5.4.4 things.c:inv_name() formats GOLD as "%d Gold pieces".
        ident = rogue.IdentTable()
        gold = rogue.Item(rogue.CAT_GOLD, 0)
        gold.qty = 42

        self.assertEqual(ident.name(gold, rogue.LANG_EN), "42 Gold pieces")

    def test_language_switch_changes_text_not_generated_state(self):
        en = new_game(seed=23, lang=rogue.LANG_EN)
        ja = new_game(seed=23, lang=rogue.LANG_JA)
        self.assertNotEqual(en.msgs[-1], ja.msgs[-1])
        self.assertEqual((en.p.x, en.p.y, en.p.depth), (ja.p.x, ja.p.y, ja.p.depth))
        self.assertEqual(len(en.rooms), len(ja.rooms))
        self.assertEqual(len(en.mons), len(ja.mons))
        self.assertEqual(len(en.gitems), len(ja.gitems))

    def test_language_does_not_change_quaff_read_eat_or_drop_state(self):
        # DESIGN.md: translation must not alter game state for the same seed and operations.
        def run(lang):
            game = new_game(seed=2301, lang=lang)
            set_open_floor(game)
            healing = next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "healing")
            remove = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "remove curse")
            potion = rogue.Item(rogue.CAT_POT, healing)
            scroll = rogue.Item(rogue.CAT_SCR, remove)
            food = rogue.Item(rogue.CAT_FOOD, 0)
            drop_item = rogue.Item(rogue.CAT_FOOD, 1)
            game.p.inv.extend([potion, scroll, food, drop_item])
            game.p.hp = 5
            game.p.food = 100
            old_roll = rogue.RNG.roll
            old_rnd = rogue.RNG.rnd
            try:
                rogue.RNG.roll = lambda number, sides: 3
                rogue.RNG.rnd = lambda n: 0
                game.use_pot(potion)
                game.use_scr(scroll)
                game.eat(food)
                game.drop(drop_item)
            finally:
                rogue.RNG.roll = old_roll
                rogue.RNG.rnd = old_rnd
            return state_signature(game)

        self.assertEqual(run(rogue.LANG_EN), run(rogue.LANG_JA))

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
            rogue.pyxel.colors = [0] * len(rogue.GBC_HIGH_CONTRAST_PALETTE)
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
            rogue.pyxel.colors = [0] * len(rogue.FLEXOKI_LIGHT_PALETTE)
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

        game.p.gold = 0
        game.gitems = []
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

    def test_rogue_544_add_pack_stacks_potions_and_scrolls(self):
        # Rogue 5.4.4 pack.c:add_pack() stacks ISMULT potion/scroll/food items.
        game = new_game(seed=3302)
        game.gitems = []
        potion = rogue.Item(rogue.CAT_POT, 0)
        scroll = rogue.Item(rogue.CAT_SCR, 0)
        game.p.inv = [potion, scroll]
        potion_floor = rogue.Item(rogue.CAT_POT, 0)
        scroll_floor = rogue.Item(rogue.CAT_SCR, 0)

        self.assertTrue(game.p.add_item(potion_floor))
        self.assertTrue(game.p.add_item(scroll_floor))

        self.assertEqual(game.p.inv, [potion, scroll])
        self.assertEqual(potion.qty, 2)
        self.assertEqual(scroll.qty, 2)

    def test_rogue_544_add_pack_keeps_weapon_groups_separate(self):
        # Rogue 5.4.4 weapons.c:init_weapon() assigns o_group, and pack.c:add_pack() only stacks matching groups.
        game = new_game(seed=3303)
        game.gitems = []
        first = rogue.Item(rogue.CAT_WPN, 3, qty=4)
        second = rogue.Item(rogue.CAT_WPN, 3, qty=5)
        first.group = 1
        second.group = 2
        game.p.inv = [first]

        self.assertTrue(game.p.add_item(second))

        self.assertEqual(game.p.inv, [first, second])
        self.assertEqual(first.qty, 4)
        self.assertEqual(second.qty, 5)

    def test_rogue_544_full_pack_can_stack_matching_weapon_group(self):
        # Rogue 5.4.4 pack.c:add_pack() decrements inpack before pack_room() for matching o_group weapons.
        game = new_game(seed=3306)
        game.gitems = []
        arrows = rogue.Item(rogue.CAT_WPN, 3, qty=4, group=7)
        extra = rogue.Item(rogue.CAT_WPN, 3, qty=5, group=7)
        game.p.inv = [arrows] + [
            rogue.Item(rogue.CAT_POT, i % len(rogue.POTIONS)) for i in range(rogue.INV_MAX - 1)
        ]

        self.assertTrue(game.p.add_item(extra))

        self.assertEqual(len(game.p.inv), rogue.INV_MAX)
        self.assertEqual(arrows.qty, 9)

    def test_rogue_544_add_pack_inserts_same_type_before_later_types(self):
        # Rogue 5.4.4 pack.c:add_pack() inserts near the same o_type instead of always appending.
        game = new_game(seed=3307)
        game.gitems = []
        potion = rogue.Item(rogue.CAT_POT, 0)
        armor = rogue.Item(rogue.CAT_ARM, 0)
        new_potion = rogue.Item(rogue.CAT_POT, 1)
        game.p.inv = [potion, armor]

        self.assertTrue(game.p.add_item(new_potion))

        self.assertEqual(game.p.inv, [potion, new_potion, armor])

    def test_rogue_544_add_pack_inserts_new_weapon_group_after_existing_groups(self):
        # Rogue 5.4.4 pack.c:add_pack() scans same o_group weapons before inserting a new group.
        game = new_game(seed=3308)
        game.gitems = []
        first = rogue.Item(rogue.CAT_WPN, 3, qty=4, group=1)
        second = rogue.Item(rogue.CAT_WPN, 3, qty=5, group=2)
        armor = rogue.Item(rogue.CAT_ARM, 0)
        new_group = rogue.Item(rogue.CAT_WPN, 3, qty=6, group=3)
        game.p.inv = [first, second, armor]

        self.assertTrue(game.p.add_item(new_group))

        self.assertEqual(game.p.inv, [first, second, new_group, armor])

    def test_rogue_544_leave_pack_stack_copy_preserves_scare_found_flag(self):
        # Rogue 5.4.4 pack.c:add_pack() sets ISFOUND, and leave_pack(newobj=TRUE) copies it.
        game = new_game(seed=3304)
        game.gitems = []
        scare_kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "scare monster")
        scroll = rogue.Item(rogue.CAT_SCR, scare_kind, qty=2)
        scroll.picked_up = True
        game.p.inv = [scroll]

        self.assertTrue(game.drop(scroll))

        dropped = game.gitems[-1]
        self.assertEqual(dropped.cat, rogue.CAT_SCR)
        self.assertTrue(dropped.picked_up)
        self.assertEqual(scroll.qty, 1)

    def test_rogue_544_add_pack_marks_stacked_scare_scroll_found(self):
        # Rogue 5.4.4 pack.c:add_pack() sets ISFOUND on the resulting stack.
        game = new_game(seed=3305)
        game.gitems = []
        scare_kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "scare monster")
        held = rogue.Item(rogue.CAT_SCR, scare_kind)
        floor_scroll = rogue.Item(rogue.CAT_SCR, scare_kind)
        floor_scroll.x, floor_scroll.y = game.p.x, game.p.y
        game.p.inv = [held]
        game.gitems = [floor_scroll]

        game.do_pickup()

        self.assertEqual(game.p.inv, [held])
        self.assertEqual(held.qty, 2)
        self.assertTrue(held.picked_up)

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

    def test_rogue_544_visible_monster_cell_draws_only_monster_glyph(self):
        # Rogue 5.4.4 misc.c:look() uses p_monst/t_disguise instead of stacking floor/item glyphs.
        game = new_game(seed=35)
        game.cam_x = 0
        game.cam_y = 0
        game.p.x, game.p.y = 1, 1
        game.visible = {(5, 5)}
        game.explored = {(5, 5)}
        game.tm[5][5] = rogue.T_CORR
        item = rogue.Item(rogue.CAT_POT, 0)
        item.x, item.y = 5, 5
        monster = monster_at(5, 5, "Z", "zombie")
        game.gitems = [item]
        game.mons = [monster]
        calls = []
        game.txt = lambda x, y, s, c: calls.append((x, y, str(s)))

        game.draw_zoom()

        target_x = rogue.ZV_X + 5 * rogue.TILE_W + 1
        target_y = rogue.ZV_Y + 5 * rogue.TILE_H + 1
        glyphs = [s for x, y, s in calls if (x, y) == (target_x, target_y)]
        self.assertEqual(glyphs, ["Z"])

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

    def test_rogue_544_blind_player_does_not_explore_lit_room_cells(self):
        # Rogue 5.4.4 rooms.c:enter_room() does not light rooms while ISBLIND.
        game = new_game(seed=345)
        room = rogue.Room(5, 5, 8, 6)
        game.rooms = [room]
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        rogue.DGen._room(game.tm, room)
        game.p.x, game.p.y = room.x + 2, room.y + 2
        game.p.blind = 10
        game.visible = set()
        game.explored = set()

        game.update_fov()

        self.assertEqual(game.visible, {(game.p.x, game.p.y)})
        self.assertEqual(game.explored, {(game.p.x, game.p.y)})

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
        second_item = next(c for c in inv_lines if c[2].startswith("b)"))
        last_item = next(c for c in inv_lines if c[2].startswith("z)"))
        self.assertEqual(first_item[1] - calls[0][1], 15)
        self.assertEqual(second_item[1] - first_item[1], 11)
        self.assertLessEqual(last_item[1], 320)

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

    def test_keyboard_space_holds_diagonal_assist_only_while_pressed(self):
        game = new_game(seed=35)
        set_open_floor(game)
        self.assertFalse(game.diag_assist)
        start = (game.p.x, game.p.y)

        rogue.pyxel.set_input(
            held={rogue.pyxel.KEY_SPACE, rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT},
            pressed={rogue.pyxel.KEY_SPACE, rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT},
        )
        game.update()

        self.assertTrue(game.diag_assist)
        self.assertEqual((game.p.x, game.p.y), start)

        rogue.pyxel.set_input()
        game.update()

        self.assertFalse(game.diag_assist)
        self.assertEqual((game.p.x, game.p.y), start)

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

    def test_rogue_544_death_tombstone_uses_score_purse_after_penalty(self):
        # Rogue 5.4.4 rip.c:death() subtracts 10% from purse before tombstone() and score().
        game = new_game(seed=35)
        game.p.gold = 123
        game.death_cause = "killed by a hobgoblin"
        saved = []
        old_save = rogue.save_score_entry
        old_load = rogue.load_score_entries
        try:
            rogue.save_score_entry = lambda entry: saved.append(entry)
            rogue.load_score_entries = lambda: saved[:]
            game.enter_result_state("killed")
        finally:
            rogue.save_score_entry = old_save
            rogue.load_score_entries = old_load
        calls = []
        game.txt = lambda x, y, s, c: calls.append(str(s))

        game.draw_dead()

        self.assertEqual(saved[0]["score"], 110)
        self.assertTrue(any("110 Au" in c for c in calls))
        self.assertFalse(any("123 Au" in c for c in calls))

    def test_rogue_544_death_killname_special_causes_match_rip(self):
        # Rogue 5.4.4 rip.c:killname() maps death codes to score/tombstone names.
        cases = {
            "starved to death": "starvation",
            "hypothermia": "hypothermia",
            "an arrow killed you": "arrow",
            "a poisoned dart killed you": "dart",
            "killed by a bolt": "bolt",
        }
        for cause, killer in cases.items():
            game = new_game(seed=35)
            game.death_cause = cause
            self.assertEqual(game.result_killer("killed"), killer)

    def test_rogue_544_death_score_line_omits_article_for_starvation(self):
        # Rogue 5.4.4 rip.c:killname(doart=TRUE) prints no article for starvation/hypothermia.
        line = rogue.format_score_line(
            1,
            {"score": 90, "player_name": "ROGUE", "result_flags": "killed", "level": 12, "killer": "starvation"},
        )

        self.assertEqual(line, " 1    90 ROGUE: killed on level 12 by starvation.")

    def test_rogue_544_death_tombstone_omits_article_for_starvation(self):
        # Rogue 5.4.4 rip.c:death() blanks the tombstone article for starvation/hypothermia.
        game = new_game(seed=35)
        game.death_cause = "starved to death"
        calls = []
        game.txt = lambda x, y, s, c: calls.append(str(s))

        game.draw_dead()

        self.assertTrue(any("starvation" in c for c in calls))
        self.assertFalse(any("killed by a" in c for c in calls))

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

    def test_rogue_544_total_winner_item_worth_matches_rip_source(self):
        # Rogue 5.4.4 rip.c:total_winner() sells pack items before score().
        self.assertEqual(rogue.total_winner_item_worth({"cat": rogue.CAT_FOOD, "qty": 3}), 6)
        self.assertEqual(rogue.total_winner_item_worth({
            "cat": rogue.CAT_WPN, "base_worth": 8, "hit_plus": 1, "dam_plus": 2, "qty": 1,
        }), 80)
        self.assertEqual(rogue.total_winner_item_worth({
            "cat": rogue.CAT_ARM, "base_worth": 30, "base_ac": 7, "ench": 2,
        }), 450)
        self.assertEqual(rogue.total_winner_item_worth({
            "cat": rogue.CAT_POT, "base_worth": 130, "qty": 2, "type_known": False,
        }), 130)
        self.assertEqual(rogue.total_winner_item_worth({
            "cat": rogue.CAT_RING, "name": "add strength", "base_worth": 400, "ench": -1, "known": False,
        }), 5)
        self.assertEqual(rogue.total_winner_item_worth({
            "cat": rogue.CAT_STICK, "base_worth": 250, "charges": 3, "known": True,
        }), 310)
        self.assertEqual(rogue.total_winner_item_worth({"cat": rogue.CAT_AMULET}), 1000)

    def test_rogue_544_winner_score_uses_init_stones_adjusted_ring_worth(self):
        # Rogue 5.4.4 init.c:init_stones() mutates ring_info[].oi_worth before rip.c:total_winner().
        game = new_game(seed=9446)
        ring = rogue.Item(rogue.CAT_RING, rogue.rogue_rings.R_SUSTSTR, known=False)
        game.p.inv = [ring]
        game.ident.rworth[rogue.rogue_rings.R_SUSTSTR] = 505

        self.assertEqual(game.total_winner_item_data(ring)["base_worth"], 505)
        self.assertEqual(game.total_winner_score(), 505 // 2)

    def test_rogue_544_winner_ring_worth_halves_by_item_isknow_not_type_know(self):
        # Rogue 5.4.4 rip.c:total_winner() checks obj->o_flags & ISKNOW for RING.
        game = new_game(seed=9447)
        ring = rogue.Item(rogue.CAT_RING, rogue.rogue_rings.R_SUSTSTR, known=True)
        game.p.inv = [ring]
        game.ident.rworth[rogue.rogue_rings.R_SUSTSTR] = 505
        game.ident.rk[rogue.rogue_rings.R_SUSTSTR] = False

        self.assertTrue(game.total_winner_item_data(ring)["known"])
        self.assertEqual(game.total_winner_score(), 505)

    def test_rogue_544_winner_stick_worth_halves_by_item_isknow_not_type_know(self):
        # Rogue 5.4.4 rip.c:total_winner() checks obj->o_flags & ISKNOW for STICK.
        game = new_game(seed=9448)
        stick = rogue.Item(rogue.CAT_STICK, rogue.rogue_sticks.WS_LIGHT, charges=3, known=False)
        game.p.inv = [stick]
        game.ident.wk[rogue.rogue_sticks.WS_LIGHT] = True

        self.assertFalse(game.total_winner_item_data(stick)["known"])
        self.assertEqual(game.total_winner_score(), (250 + 20 * 3) // 2)

    def test_rogue_544_winner_score_adds_pack_worth(self):
        # Rogue 5.4.4 rip.c:total_winner() adds pack worth to purse before score(purse, 2, ' ').
        game = new_game(seed=352)
        game.p.gold = 100
        game.p.inv = [
            rogue.Item(rogue.CAT_FOOD, 0, qty=2),
            rogue.Item(rogue.CAT_POT, next(i for i, p in enumerate(rogue.POTIONS) if p["name"] == "healing"), qty=1),
            rogue.Item(rogue.CAT_AMULET, 0),
        ]
        game.ident.pk[game.p.inv[1].kind] = False
        saved = []
        old_save = rogue.save_score_entry
        old_load = rogue.load_score_entries
        try:
            rogue.save_score_entry = lambda entry: saved.append(entry)
            rogue.load_score_entries = lambda: saved[:]
            game.enter_result_state("winner")
        finally:
            rogue.save_score_entry = old_save
            rogue.load_score_entries = old_load

        self.assertEqual(saved[0]["score"], 100 + 4 + 65 + 1000)

    def test_score_entry_has_stable_id_for_online_deduplication(self):
        entry = rogue.build_score_entry(
            score=0,
            result_flags="killed",
            level=3,
            killer="hobgoblin",
            player_name="WEBUSER",
            timestamp="2026-04-29T13:54:10Z",
            gold=58,
        )
        same = rogue.build_score_entry(
            score=0,
            result_flags="killed",
            level=3,
            killer="hobgoblin",
            player_name="WEBUSER",
            timestamp="2026-04-29T13:54:10Z",
            gold=58,
        )

        self.assertTrue(entry["score_id"])
        self.assertEqual(entry["score_id"], same["score_id"])

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

    def test_score_lines_use_depth_when_sheet_rows_do_not_have_level(self):
        line = rogue.format_score_line(
            7,
            {"score": 614, "player_name": "NIX", "result_flags": "killed", "depth": 8, "killer": "kestrel"},
        )

        self.assertEqual(line, " 7   614 NIX: killed on level 8 by a kestrel.")

    def test_score_period_keys_include_week_and_fixed_season(self):
        import rogue_scores

        keys = rogue_scores.score_period_keys("2026-02-01T12:00:00Z")

        self.assertEqual(keys["period_day"], "2026-02-01")
        self.assertEqual(keys["period_week"], "2026-W05")
        self.assertEqual(keys["period_season"], "2026-Winter")
        self.assertEqual(rogue_scores.score_period_keys("2025-12-01T00:00:00Z")["period_season"], "2026-Winter")

    def test_scoreboard_period_order_removes_daily_and_starts_with_local_history(self):
        self.assertEqual(
            rogue.SCOREBOARD_PERIOD_ORDER,
            (rogue.SCOREBOARD_PERIOD_LOCAL, rogue.SCOREBOARD_PERIOD_WEEKLY, rogue.SCOREBOARD_PERIOD_SEASON),
        )

    def test_user_id_is_lowercase_alnum_and_local_display_is_marked(self):
        import rogue_scores

        self.assertEqual(rogue_scores.sanitize_user_id("Rogue-54!xxxx"), "rogue54x")
        self.assertEqual(rogue_scores.sanitize_user_id("!!!"), "rogue54")
        self.assertEqual(rogue_scores.display_score_name({"user_name": "rogue54"}), "rogue54*")

    def test_online_profile_v3_uses_user_name_and_ignores_old_profile_keys(self):
        import rogue_scores

        self.assertEqual(rogue_scores.ONLINE_PROFILE_STORAGE_KEY, "pyxel-rogue-online-profile-v3")

        profile = rogue_scores.normalize_online_profile({"user_id": "ACE", "display_name": "ACE", "server_token": "tok"})

        self.assertEqual(profile["user_name"], "rogue54")
        self.assertTrue(profile["local_only"])
        self.assertEqual(profile["server_token"], "")
        self.assertFalse(profile["profile_exists"])

    def test_online_profile_v3_marks_only_local_or_tokenless_names_unverified(self):
        import rogue_scores

        local = rogue_scores.normalize_online_profile({"user_name": "ace", "local_only": True, "profile_exists": True})
        registered = rogue_scores.normalize_online_profile({
            "user_name": "ace",
            "server_token": "tok",
            "local_only": False,
            "profile_exists": True,
        })
        synced = rogue_scores.normalize_online_profile({
            "user_name": "ace",
            "server_token": "tok",
            "local_only": False,
            "last_sync_at": "2026-05-01T00:00:00Z",
            "profile_exists": True,
        })

        self.assertEqual(rogue_scores.display_score_name(local), "ace*")
        self.assertEqual(rogue_scores.display_score_name(registered), "ace")
        self.assertEqual(rogue_scores.display_score_name(synced), "ace")

    def test_daily_period_scores_are_no_longer_supported(self):
        import rogue_scores

        entries = [
            {"player_name": "ACE", "score": 10, "period_day": "2026-04-29"},
            {"player_name": "DOT", "score": 20, "period_day": "2026-04-29"},
            {"player_name": "ACE", "score": 99, "period_day": "2026-04-30"},
        ]

        daily = rogue_scores.get_period_scores(entries, "daily", "2026-04-29", limit=10)

        self.assertEqual(daily, [])

    def test_fetch_online_scores_uses_weekly_and_season_only(self):
        import rogue_scores

        calls = []
        old_http_json = rogue_scores._http_json
        try:
            rogue_scores._http_json = lambda url, payload=None: calls.append((url, payload)) or {"scores": []}
            rogue_scores.fetch_online_scores("weekly", "https://example.test/exec", "2026-04-29T12:00:00Z")
        finally:
            rogue_scores._http_json = old_http_json

        self.assertEqual(calls, [("https://example.test/exec?period=weekly&key=2026-W18", None)])

    def test_online_user_registration_payload_and_reserved_names(self):
        import rogue_scores

        calls = []
        old_http_json = rogue_scores._http_json
        try:
            rogue_scores._http_json = lambda url, payload=None: calls.append((url, payload)) or {
                "ok": True,
                "server_token": "srv-token",
                "last_sync_at": "",
            }
            self.assertFalse(rogue_scores.can_register_user_id("rogue54"))
            self.assertFalse(rogue_scores.can_register_user_id("rodney"))
            result = rogue_scores.register_online_user(
                "newuser",
                "123456",
                "https://example.test/exec",
            )
        finally:
            rogue_scores._http_json = old_http_json

        self.assertEqual(result["server_token"], "srv-token")
        self.assertEqual(calls, [(
            "https://example.test/exec",
            {
                "action": "registerUser",
                "user_name": "newuser",
                "user_password": "123456",
            },
        )])

    def test_check_online_user_posts_user_name(self):
        import rogue_scores

        calls = []
        old_http_json = rogue_scores._http_json
        try:
            rogue_scores._http_json = lambda url, payload=None: calls.append((url, payload)) or {"ok": True, "exists": True}
            result = rogue_scores.check_online_user("New-User!", "https://example.test/exec")
        finally:
            rogue_scores._http_json = old_http_json

        self.assertTrue(result["exists"])
        self.assertEqual(calls, [("https://example.test/exec", {"action": "checkUser", "user_name": "newuser"})])

    def test_server_token_obfuscation_round_trips_without_plaintext_storage(self):
        import rogue_scores

        encoded = rogue_scores.obfuscate_server_token("abc123", "newuser")

        self.assertNotEqual(encoded, "abc123")
        self.assertEqual(rogue_scores.deobfuscate_server_token(encoded, "newuser"), "abc123")

    def test_sync_online_scoreboard_posts_user_token_entries_and_returns_cooldown(self):
        import rogue_scores

        calls = []
        old_http_json = rogue_scores._http_json
        try:
            rogue_scores._http_json = lambda url, payload=None: calls.append((url, payload)) or {
                "ok": False,
                "status": "cooldown",
                "last_sync_at": "2026-05-01T00:00:00Z",
                "next_sync_at": "2026-05-02T00:00:00Z",
                "scores": {"weekly": [], "season": []},
            }
            result = rogue_scores.sync_online_scoreboard(
                {"user_name": "newuser", "server_token": "abc123"},
                [{"score": 30, "player_name": "newuser", "period_week": "2026-W18"}],
                "https://example.test/exec",
            )
        finally:
            rogue_scores._http_json = old_http_json

        self.assertEqual(result["status"], "cooldown")
        self.assertEqual(calls[0][1]["action"], "syncScoreboard")
        self.assertEqual(calls[0][1]["user_name"], "newuser")
        self.assertEqual(calls[0][1]["server_token"], "abc123")
        self.assertEqual(calls[0][1]["entries"][0]["score"], 30)

    def test_online_http_timeout_allows_apps_script_sync_response(self):
        import rogue_scores

        self.assertGreaterEqual(rogue_scores.ONLINE_HTTP_TIMEOUT_SECONDS, 15)

    def test_local_best_sync_entries_only_keeps_current_week_and_season_best(self):
        import rogue_scores

        entries = [
            {"score_id": "low", "player_name": "ace", "score": 30, "period_week": "2026-W18", "period_season": "2026-Spring"},
            {"score_id": "best", "player_name": "ace", "score": 300, "period_week": "2026-W18", "period_season": "2026-Spring"},
            {"score_id": "old", "player_name": "ace", "score": 900, "period_week": "2026-W17", "period_season": "2026-Spring"},
        ]

        sync_entries = rogue_scores.local_best_sync_entries(entries, "2026-04-29T12:00:00Z")

        self.assertEqual([entry["score_id"] for entry in sync_entries], ["best", "old"])

    def test_online_scores_deduplicate_weekly_and_season_by_player_best(self):
        import rogue_scores

        entries = [
            {"player_name": "ACE", "score": 10, "period_week": "2026-W17", "period_season": "2026-Spring"},
            {"player_name": "ACE", "score": 20, "period_week": "2026-W17", "period_season": "2026-Spring"},
            {"player_name": "DOT", "score": 15, "period_week": "2026-W17", "period_season": "2026-Spring"},
            {"player_name": "ACE", "score": 99, "period_week": "2026-W18", "period_season": "2026-Spring"},
        ]

        weekly = rogue_scores.get_period_scores(entries, "weekly", "2026-W17", limit=10)
        season = rogue_scores.get_period_scores(entries, "season", "2026-Spring", limit=10)

        self.assertEqual([(e["player_name"], e["score"]) for e in weekly], [("ACE", 20), ("DOT", 15)])
        self.assertEqual([(e["player_name"], e["score"]) for e in season], [("ACE", 99), ("DOT", 15)])

    def test_online_scores_preserve_display_name_case_when_deduplicating(self):
        import rogue_scores

        entries = [
            {"player_name": "ace", "score": 20, "period_week": "2026-W18", "period_season": "2026-Spring"},
            {"player_name": "ACE", "score": 10, "period_week": "2026-W18", "period_season": "2026-Spring"},
        ]

        weekly = rogue_scores.get_period_scores(entries, "weekly", "2026-W18", limit=10)

        self.assertEqual([(e["player_name"], e["score"]) for e in weekly], [("ace", 20)])

    def test_dummy_scores_are_sheet_rows_with_consistent_periods(self):
        import rogue_scores

        rows = rogue_scores.build_dummy_score_rows("2026-04-28T00:00:00Z", count=12, seed=3)

        self.assertEqual(len(rows), 12)
        self.assertTrue(all(row["is_dummy"] for row in rows))
        self.assertTrue(all(row["period_week"] == "2026-W18" for row in rows))
        self.assertTrue(all(row["period_season"] == "2026-Spring" for row in rows))
        self.assertTrue(all(0 < int(row["score"]) < 1800 for row in rows))
        self.assertGreaterEqual(len(rogue_scores.DUMMY_PLAYER_NAMES), 80)

    def test_sync_missing_local_best_posts_when_online_lacks_it(self):
        import rogue_scores

        local = [
            {"player_name": "ACE", "score": 300, "period_week": "2026-W18", "period_season": "2026-Spring"},
            {"player_name": "ACE", "score": 100, "period_week": "2026-W18", "period_season": "2026-Spring"},
        ]
        posted = []

        rogue_scores.sync_missing_local_best(
            local,
            [{"player_name": "ACE", "score": 250, "period_week": "2026-W18"}],
            "weekly",
            "2026-W18",
            posted.append,
        )

        self.assertEqual(len(posted), 1)
        self.assertEqual(posted[0]["score"], 300)

    def test_sync_missing_local_best_skips_duplicate_score_id(self):
        import rogue_scores

        local = [
            {"score_id": "same-run", "player_name": "ACE", "score": 300, "period_week": "2026-W18", "period_season": "2026-Spring"},
        ]
        posted = []

        did_post = rogue_scores.sync_missing_local_best(
            local,
            [{"score_id": "same-run", "player_name": "ACE", "score": 250, "period_week": "2026-W18"}],
            "weekly",
            "2026-W18",
            posted.append,
        )

        self.assertFalse(did_post)
        self.assertEqual(posted, [])

    def test_apps_script_scoreboard_deduplicates_score_id_before_append(self):
        path = os.path.join(ROOT, "docs", "apps_script_scoreboard.gs")
        with open(path, encoding="utf-8") as f:
            script = f.read()

        self.assertIn('"score_id"', script)
        self.assertIn("scoreIdExists(scoreId)", script)

    def test_apps_script_dummy_seed_uses_small_seed_set(self):
        path = os.path.join(ROOT, "docs", "apps_script_scoreboard.gs")
        with open(path, encoding="utf-8") as f:
            script = f.read()

        self.assertIn("DUMMY_PAST_WEEKS = 10", script)
        self.assertIn("ensureDummyRows(", script)
        self.assertIn("ensureScoreboardDummyContext()", script)
        self.assertIn("ensureHistoricalWeeklyRows(now, currentPeriods().period_season)", script)
        self.assertIn("ensureSeededDummyRows(", script)
        self.assertIn("currentPeriods().period_week", script)
        self.assertIn("DUMMY_TARGET_COUNT", script)
        self.assertIn("DUMMY_BACKFILL_COUNT = 1", script)
        self.assertIn("const p = periodsFor(addUtcDays(base, historicalWeeklyDayOffset(i)))", script)
        self.assertIn("if (seasonKey && p.period_season !== seasonKey) continue", script)
        self.assertIn("p.period_week", script)
        self.assertNotIn("ensureDummyRows('season'", script)
        self.assertNotIn('ensureDummyRows("season"', script)

    def test_apps_script_dummy_seed_uses_period_specific_dummy_rows(self):
        path = os.path.join(ROOT, "docs", "apps_script_scoreboard.gs")
        with open(path, encoding="utf-8") as f:
            script = f.read()

        self.assertIn("seededDummyNames(period, key)", script)
        self.assertIn("countSeededOnly", script)
        self.assertIn(": Math.max(scores.length, seeded.size)", script)
        self.assertIn("targetCount - visibleOrSeeded", script)
        self.assertIn("dummyNameOffset(period, key)", script)
        self.assertIn("dummyValue(period, key, offset,", script)
        self.assertIn("dummyScore(period, key, i, targetCount)", script)
        self.assertIn('if (period === "weekly")', script)
        self.assertIn("dummyDepth(period, key, i)", script)
        self.assertIn('dummyValue(period, key, offset, "depth", 16)', script)
        self.assertIn("const depth = dummyDepth(period, key, offset)", script)
        self.assertIn('return depth * 70 + dummyValue(period, key, offset, "score", 351)', script)
        self.assertIn("dummyKiller(period, key, i)", script)
        self.assertIn("function dummyKillersForDepth(depth)", script)
        killers = script[script.index("function dummyKillersForDepth"):]
        self.assertIn('["hobgoblin", "kestrel"]', killers)
        self.assertIn('["rattlesnake", "orc"]', killers)
        self.assertIn('["centaur", "quagga"]', killers)
        self.assertIn('["venus flytrap", "troll"]', killers)
        self.assertIn('["phantom", "vampire"]', killers)
        self.assertIn('"xeroc"', killers)
        self.assertIn("Math.min(16, depth)", killers)
        self.assertNotIn('"aquator"', killers)
        self.assertNotIn('"ice monster"', killers)
        self.assertNotIn('"nymph"', killers)
        self.assertNotIn('"leprechaun"', killers)
        self.assertIn("dummy-\" + period + \"-\" + key + \"-", script)

    def test_apps_script_weekly_and_season_dummy_rows_use_period_dates(self):
        path = os.path.join(ROOT, "docs", "apps_script_scoreboard.gs")
        with open(path, encoding="utf-8") as f:
            script = f.read()

        self.assertIn("periodsFromKey(period, key, i)", script)
        self.assertIn("dateForIsoWeek(key, offset % 7)", script)
        self.assertIn("dateForSeason(key, offset * 7)", script)
        self.assertNotIn("period_day: now.period_day", script)

    def test_apps_script_score_fetch_ensures_dummy_rows_for_requested_period(self):
        path = os.path.join(ROOT, "docs", "apps_script_scoreboard.gs")
        with open(path, encoding="utf-8") as f:
            script = f.read()

        do_get = script[script.index("function doGet"):script.index("function doPost")]
        self.assertIn('ensureDummyRows(period, key, DUMMY_TARGET_COUNT)', do_get)
        self.assertIn('if (period === "season") {', do_get)
        self.assertIn('ensureHistoricalWeeklyRows(new Date(), key)', do_get)
        self.assertIn('ensureDummyRows("weekly", currentPeriods().period_week, DUMMY_TARGET_COUNT)', do_get)
        self.assertLess(do_get.index("ensureDummyRows(period, key,"), do_get.index("topScores(period, key)"))

    def test_apps_script_sync_scoreboard_does_not_generate_dummy_or_payload_scores(self):
        path = os.path.join(ROOT, "docs", "apps_script_scoreboard.gs")
        with open(path, encoding="utf-8") as f:
            script = f.read()

        sync = script[script.index("function syncScoreboard"):script.index("function nextSyncAt")]

        self.assertNotIn("scorePayload", sync)
        self.assertNotIn("ensureDummyRows", sync)
        self.assertNotIn("topScores", sync)
        self.assertIn("posted_count", sync)
        self.assertIn("if (entries.length === 0 && !last)", sync)
        self.assertIn('next_sync_at: ""', sync)
        self.assertIn("const firstScorePost = entries.length > 0 && !hasUserScore(userName)", sync)
        self.assertIn("if (next && new Date(next).getTime() > Date.now() && !firstScorePost)", sync)
        self.assertIn("function hasUserScore(userName)", script)

    def test_apps_script_user_list_supports_token_cooldown_and_pin_lockout(self):
        path = os.path.join(ROOT, "docs", "apps_script_scoreboard.gs")
        with open(path, encoding="utf-8") as f:
            script = f.read()

        self.assertIn("USER_SHEET_NAME", script)
        self.assertIn("checkUser(body)", script)
        self.assertIn("registerUser(body)", script)
        self.assertIn("linkUser(body)", script)
        self.assertIn("syncScoreboard(body)", script)
        self.assertIn("SYNC_COOLDOWN_HOURS", script)
        self.assertIn("USER_PASSWORD_FAIL_LIMIT", script)
        self.assertIn("server_token", script)
        self.assertIn("last_sync_at", script)
        self.assertIn("isReservedUserId", script)
        self.assertIn('"user_name"', script)
        self.assertIn("USER_NAME_MAX = 8", script)

    def test_apps_script_score_names_are_lowercase_alnum(self):
        path = os.path.join(ROOT, "docs", "apps_script_scoreboard.gs")
        with open(path, encoding="utf-8") as f:
            script = f.read()

        clean_name = script[script.index("function cleanName"):script.index("function cleanUserId")]
        dummy_names = script[script.index("const DUMMY_NAMES"):script.index("];", script.index("const DUMMY_NAMES"))]

        self.assertIn(".toLowerCase()", clean_name)
        self.assertIn("replace(/[^a-z0-9]/g, \"\")", clean_name)
        self.assertIn('"dummy-" + period + "-" + key + "-" + clean', script)
        self.assertIn('"rodney"', dummy_names)
        self.assertIn('"savesc"', dummy_names)
        self.assertNotIn('"RODNEY"', dummy_names)
        self.assertNotIn('"SAVE_SC"', dummy_names)

    def test_online_score_url_defaults_to_deployed_apps_script(self):
        import rogue_scores

        self.assertEqual(
            rogue_scores.ONLINE_SCORE_URL,
            "https://script.google.com/macros/s/AKfycbx0jUvQm2puooh1rnEGpcjrltLhgbmCFwwoPRqD1qKlDieZhZRaOEdeggRYgTbFdX5t/exec",
        )

    def test_seed_dummy_online_scores_posts_seed_action(self):
        import rogue_scores

        calls = []
        old_http_json = rogue_scores._http_json
        try:
            rogue_scores._http_json = lambda url, payload=None: calls.append((url, payload)) or {"rows": 1}
            self.assertTrue(rogue_scores.seed_dummy_online_scores("https://example.test/exec"))
        finally:
            rogue_scores._http_json = old_http_json

        self.assertEqual(calls, [("https://example.test/exec?action=seedDummy", None)])

    def test_emscripten_http_json_uses_simple_cors_requests_for_apps_script(self):
        import rogue_scores

        calls = []

        class FakeXhr:
            status = 200
            responseText = '{"ok": true}'

            def open(self, method, url, async_flag):
                calls.append(("open", method, url, async_flag))

            def setRequestHeader(self, key, value):
                calls.append(("header", key, value))

            def send(self, body):
                calls.append(("send", body))

        js = types.ModuleType("js")
        js.XMLHttpRequest = types.SimpleNamespace(new=lambda: FakeXhr())
        old_js = sys.modules.get("js")
        old_platform = sys.platform
        try:
            sys.modules["js"] = js
            sys.platform = "emscripten"
            self.assertEqual(rogue_scores._http_json("https://example.test/exec"), {"ok": True})
            self.assertEqual(calls, [
                ("open", "GET", "https://example.test/exec", False),
                ("send", None),
            ])

            calls.clear()
            self.assertEqual(rogue_scores._http_json("https://example.test/exec", {"action": "submit"}), {"ok": True})
            self.assertEqual(calls, [
                ("open", "POST", "https://example.test/exec", False),
                ("header", "Content-Type", "text/plain;charset=utf-8"),
                ("send", '{"action": "submit"}'),
            ])
        finally:
            sys.platform = old_platform
            if old_js is None:
                sys.modules.pop("js", None)
            else:
                sys.modules["js"] = old_js

    def test_title_start_stops_bgm_before_preparing_game_and_showing_map(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings(language=rogue.LANG_EN)
        game.font = rogue.pyxel.Font("")
        game.st = rogue.ST_TITLE
        game.title_cursor = 0
        game.player_name = "ace"
        game.online_profile = {"user_name": "ace", "local_only": True, "profile_exists": True}

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_RETURN}, pressed={rogue.pyxel.KEY_RETURN})
        game.update()

        self.assertEqual(game.st, rogue.ST_TITLE)
        for _ in range(rogue.TITLE_BGM_STOP_WAIT_FRAMES):
            rogue.pyxel.set_input()
            game.update()
        self.assertEqual(game.st, rogue.ST_PLAY)
        self.assertEqual(game.msgs[-1], "Hello ace*, welcome to the Dungeons of Doom!")
        calls = []
        game.draw_title = lambda: calls.append("title")
        game.draw_zoom = lambda: calls.append("map")
        game.draw_stat = lambda: calls.append("hud")
        game.draw_msgs = lambda: calls.append("log")
        game.txt = lambda *args: None
        game.draw()
        self.assertEqual(calls[:4], ["title", "map", "hud", "log"])

    def test_title_name_and_online_ranking_navigation(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_TITLE
        game.title_cursor = 2
        game.player_name = "ace"
        game.online_profile = {"user_name": "ace", "local_only": True, "profile_exists": True}

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_RETURN}, pressed={rogue.pyxel.KEY_RETURN})
        game.update()
        self.assertEqual(game.st, rogue.ST_ONLINE_REGISTER)

        game.st = rogue.ST_TITLE
        game.title_cursor = 1
        rogue.pyxel.set_input(held={rogue.pyxel.KEY_RETURN}, pressed={rogue.pyxel.KEY_RETURN})
        game.update()
        self.assertEqual(game.st, rogue.ST_ONLINE_SCORE)
        self.assertEqual(game.online_return_state, rogue.ST_TITLE)
        self.assertEqual(game.online_period, rogue.SCOREBOARD_PERIOD_LOCAL)
        self.assertFalse(game.online_sync_pending)

    def test_title_online_ranking_entry_shows_local_history_without_syncing(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_TITLE
        game.title_cursor = 1
        game.player_name = "ace"
        game.online_profile = {
            "user_name": "ace",
            "local_only": False,
            "server_token": "tok",
            "last_sync_at": "2026-05-01T00:00:00Z",
            "profile_exists": True,
        }
        game.online_score_loaded = {
            rogue.SCOREBOARD_PERIOD_WEEKLY,
            rogue.SCOREBOARD_PERIOD_SEASON,
        }

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_RETURN}, pressed={rogue.pyxel.KEY_RETURN})
        game.update()

        self.assertEqual(game.st, rogue.ST_ONLINE_SCORE)
        self.assertEqual(game.online_period, rogue.SCOREBOARD_PERIOD_LOCAL)
        self.assertFalse(game.online_sync_pending)

    def test_title_online_ranking_entry_does_not_start_first_authenticated_sync(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_TITLE
        game.title_cursor = 1
        game.player_name = "ace"
        game.online_profile = {"user_name": "ace", "local_only": False, "server_token": "tok", "profile_exists": True}

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_RETURN}, pressed={rogue.pyxel.KEY_RETURN})
        game.update()

        self.assertEqual(game.st, rogue.ST_ONLINE_SCORE)
        self.assertEqual(game.online_period, rogue.SCOREBOARD_PERIOD_LOCAL)
        self.assertFalse(game.online_sync_pending)

    def test_logo_enters_online_confirm_after_logo_when_profile_missing(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_LOGO
        game.logo_frames = rogue.LOGO_TOTAL_FRAMES - 1
        game.online_profile = {"user_name": "rogue54", "local_only": True, "profile_exists": False}

        rogue.pyxel.set_input()
        game.update()

        self.assertEqual(game.st, rogue.ST_ONLINE_CONFIRM)

    def test_online_confirm_decline_saves_local_only_and_skips_next_prompt(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_ONLINE_CONFIRM
        game.online_profile = {"user_name": "rogue54", "local_only": True, "profile_exists": False}
        saved = []
        old_save = rogue.save_local_only_profile
        try:
            rogue.save_local_only_profile = lambda user_name: saved.append(user_name) or {
                "user_name": user_name,
                "local_only": True,
                "profile_exists": True,
            }

            rogue.pyxel.set_input(held={rogue.pyxel.KEY_ESCAPE}, pressed={rogue.pyxel.KEY_ESCAPE})
            game.update()
        finally:
            rogue.save_local_only_profile = old_save

        self.assertEqual(saved, ["rogue54"])
        self.assertEqual(game.st, rogue.ST_TITLE)
        self.assertTrue(game.online_profile["profile_exists"])

    def test_online_confirm_accept_opens_registration_with_rogue54_initial_name(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_ONLINE_CONFIRM
        game.online_profile = {"user_name": "ace", "local_only": True, "profile_exists": False}

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_RETURN}, pressed={rogue.pyxel.KEY_RETURN})
        game.update()

        self.assertEqual(game.st, rogue.ST_ONLINE_REGISTER)
        self.assertEqual("".join(game.name_chars).strip(), "rogue54")

    def test_online_registered_name_b_without_edit_cancels_to_title(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.online_profile = {
            "user_name": "ace",
            "local_only": False,
            "server_token": "tok",
            "last_sync_at": "2026-05-01T00:00:00Z",
            "profile_exists": True,
        }
        saved = []
        old_save = rogue.save_local_only_profile
        try:
            rogue.save_local_only_profile = lambda user_name: saved.append(user_name) or self.fail("unedited B must not localize")
            game.enter_online_register()

            rogue.pyxel.set_input(held={rogue.pyxel.KEY_ESCAPE}, pressed={rogue.pyxel.KEY_ESCAPE})
            game.update()
        finally:
            rogue.save_local_only_profile = old_save

        self.assertEqual(saved, [])
        self.assertEqual(game.st, rogue.ST_TITLE)
        self.assertFalse(game.online_profile["local_only"])

    def test_online_registered_name_screen_hides_local_only_hint_until_edit(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.lang = rogue.LANG_EN
        game.online_profile = {
            "user_name": "ace",
            "local_only": False,
            "server_token": "tok",
            "last_sync_at": "2026-05-01T00:00:00Z",
            "profile_exists": True,
        }
        game.enter_online_register()
        calls = []
        game.txt = lambda x, y, s, c: calls.append(str(s))

        game.draw_online_register_screen()
        self.assertIn("B cancels.", "\n".join(calls))
        self.assertNotIn("Local names show", "\n".join(calls))

        calls.clear()
        game.name_chars = list("newname")
        game.draw_online_register_screen()
        self.assertIn("Local names show", "\n".join(calls))

    def test_online_registered_name_b_after_edit_requires_local_only_confirm(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.online_profile = {
            "user_name": "ace",
            "local_only": False,
            "server_token": "tok",
            "last_sync_at": "2026-05-01T00:00:00Z",
            "profile_exists": True,
        }
        game.enter_online_register()
        game.name_chars = list("newname")

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_ESCAPE}, pressed={rogue.pyxel.KEY_ESCAPE})
        game.update()

        self.assertEqual(game.st, rogue.ST_ONLINE_LOCAL_CONFIRM)

    def test_online_local_only_confirm_ok_saves_edited_name_and_cancel_returns(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_ONLINE_LOCAL_CONFIRM
        game.online_profile = {"user_name": "ace", "local_only": False, "server_token": "tok", "profile_exists": True}
        game.name_chars = list("newname")
        saved = []
        old_save = rogue.save_local_only_profile
        try:
            rogue.save_local_only_profile = lambda user_name: saved.append(user_name) or {
                "user_name": user_name,
                "local_only": True,
                "profile_exists": True,
            }

            rogue.pyxel.set_input(held={rogue.pyxel.KEY_ESCAPE}, pressed={rogue.pyxel.KEY_ESCAPE})
            game.update()
            self.assertEqual(saved, [])
            self.assertEqual(game.st, rogue.ST_ONLINE_REGISTER)

            game.st = rogue.ST_ONLINE_LOCAL_CONFIRM
            rogue.pyxel.set_input(held={rogue.pyxel.KEY_RETURN}, pressed={rogue.pyxel.KEY_RETURN})
            game.update()
        finally:
            rogue.save_local_only_profile = old_save

        self.assertEqual(saved, ["newname"])
        self.assertEqual(game.online_profile["user_name"], "newname")
        self.assertTrue(game.online_profile["local_only"])
        self.assertEqual(game.st, rogue.ST_ONLINE_SCORE)

    def test_online_register_checks_server_before_pin_for_new_user(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_ONLINE_REGISTER
        game.name_chars = list("newuser")
        game.name_pos = 8
        checked = []
        old_check = rogue.check_online_user
        try:
            rogue.check_online_user = lambda user_name: checked.append(user_name) or {"ok": True, "exists": False}

            rogue.pyxel.set_input(held={rogue.pyxel.KEY_SPACE}, pressed={rogue.pyxel.KEY_SPACE})
            game.update()
            self.assertEqual(checked, [])
            self.assertEqual(game.st, rogue.ST_ONLINE_REGISTER)
            self.assertEqual(game.online_sync_status, "checking user...")
            rogue.pyxel.set_input()
            game.update()
        finally:
            rogue.check_online_user = old_check

        self.assertEqual(checked, ["newuser"])
        self.assertEqual(game.st, rogue.ST_ONLINE_PIN)
        self.assertEqual(game.online_password_mode, "register")
        self.assertEqual(game.online_sync_status, "checking user...")

    def test_online_register_existing_user_requests_pin_link(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_ONLINE_REGISTER
        game.name_chars = list("taken")
        game.name_pos = 8
        old_check = rogue.check_online_user
        try:
            rogue.check_online_user = lambda user_name: {"ok": True, "exists": True}

            rogue.pyxel.set_input(held={rogue.pyxel.KEY_SPACE}, pressed={rogue.pyxel.KEY_SPACE})
            game.update()
            rogue.pyxel.set_input()
            game.update()
        finally:
            rogue.check_online_user = old_check

        self.assertEqual(game.st, rogue.ST_ONLINE_PIN)
        self.assertEqual(game.online_password_mode, "link")

    def test_online_register_rejects_reserved_names_without_server_check(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_ONLINE_REGISTER
        game.name_chars = list("rodney")
        game.name_pos = 8
        old_check = rogue.check_online_user
        try:
            rogue.check_online_user = lambda user_name: self.fail("reserved names must not hit server")

            rogue.pyxel.set_input(held={rogue.pyxel.KEY_SPACE}, pressed={rogue.pyxel.KEY_SPACE})
            game.update()
        finally:
            rogue.check_online_user = old_check

        self.assertEqual(game.st, rogue.ST_ONLINE_REGISTER)
        self.assertIn("registered", game.online_sync_result)

    def test_online_pin_register_success_saves_profile_and_starts_sync(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_ONLINE_PIN
        game.online_pending_user_name = "newuser"
        game.online_password_mode = "register"
        game.online_password_chars = list("123456")
        saved = []
        old_register = rogue.register_online_user
        old_save = rogue.save_online_profile
        try:
            rogue.register_online_user = lambda user_name, pin: {
                "ok": True,
                "user_name": user_name,
                "server_token": "srv-token",
                "last_sync_at": "",
                "next_sync_at": "",
            }
            rogue.save_online_profile = lambda profile: saved.append(profile) or {
                **profile,
                "profile_exists": True,
            }

            rogue.pyxel.set_input(held={rogue.pyxel.KEY_SPACE}, pressed={rogue.pyxel.KEY_SPACE})
            game.update()
            self.assertEqual(saved, [])
            self.assertEqual(game.st, rogue.ST_ONLINE_PIN)
            self.assertEqual(game.online_sync_status, "registering user...")
            rogue.pyxel.set_input()
            game.update()
        finally:
            rogue.register_online_user = old_register
            rogue.save_online_profile = old_save

        self.assertEqual(saved[0]["user_name"], "newuser")
        self.assertEqual(saved[0]["server_token"], "srv-token")
        self.assertEqual(game.st, rogue.ST_ONLINE_SCORE)
        self.assertTrue(game.online_sync_pending)

    def test_online_pin_link_failure_rejects_name(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_ONLINE_PIN
        game.online_pending_user_name = "taken"
        game.online_password_mode = "link"
        game.online_password_chars = list("111111")
        old_link = rogue.link_online_user
        try:
            rogue.link_online_user = lambda user_name, pin: {"ok": False, "status": "auth_failed"}

            rogue.pyxel.set_input(held={rogue.pyxel.KEY_SPACE}, pressed={rogue.pyxel.KEY_SPACE})
            game.update()
            self.assertEqual(game.online_sync_status, "linking user...")
            rogue.pyxel.set_input()
            game.update()
        finally:
            rogue.link_online_user = old_link

        self.assertEqual(game.st, rogue.ST_ONLINE_PIN)
        self.assertIn("another player", game.online_sync_result)

    def test_online_name_entry_uses_eight_lowercase_chars(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.online_profile = {"user_name": "longname99", "local_only": True, "profile_exists": True}

        game.enter_online_register()

        self.assertEqual("".join(game.name_chars), "longname")
        self.assertEqual(game.name_pos, 7)

    def test_online_name_and_pin_input_up_increments_down_decrements(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_ONLINE_REGISTER
        game.name_chars = list("a")
        game.name_pos = 0
        game.online_profile = {"user_name": "a", "local_only": True, "profile_exists": True}

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_UP}, pressed={rogue.pyxel.KEY_UP})
        game.update()
        self.assertEqual(game.name_chars[0], "b")

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_DOWN}, pressed={rogue.pyxel.KEY_DOWN})
        game.update()
        self.assertEqual(game.name_chars[0], "a")

        game.st = rogue.ST_ONLINE_PIN
        game.online_password_chars = list("0" * 6)
        game.name_pos = 0
        rogue.pyxel.set_input(held={rogue.pyxel.KEY_UP}, pressed={rogue.pyxel.KEY_UP})
        game.update()
        self.assertEqual(game.online_password_chars[0], "1")

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_DOWN}, pressed={rogue.pyxel.KEY_DOWN})
        game.update()
        self.assertEqual(game.online_password_chars[0], "0")

    def test_online_registration_text_is_localized(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.lang = rogue.LANG_JA
        calls = []
        game.txt = lambda x, y, s, c: calls.append(str(s))

        game.draw_online_confirm_screen()
        game.draw_online_register_screen()
        game.online_pending_user_name = "ace"
        game.draw_online_pin_screen()

        text = "\n".join(calls)
        self.assertIn("オンラインスコア", text)
        self.assertIn("名前を登録", text)
        self.assertIn("通信", text)

    def test_online_score_skips_sync_when_next_sync_is_in_future(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_TITLE
        game.title_cursor = 1
        game.player_name = "ace"
        game.online_profile = {
            "user_name": "ace",
            "local_only": False,
            "server_token": "tok",
            "last_sync_at": "2026-05-03T00:00:00Z",
            "next_sync_at": "2999-01-01T00:00:00Z",
            "profile_exists": True,
        }

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_RETURN}, pressed={rogue.pyxel.KEY_RETURN})
        game.update()

        self.assertEqual(game.st, rogue.ST_ONLINE_SCORE)
        self.assertFalse(game.online_sync_pending)
        self.assertEqual(getattr(game, "online_sync_result", ""), "")

    def test_online_score_select_with_cooldown_loads_scoreboard_without_post(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_ONLINE_SCORE
        game.online_period = rogue.SCOREBOARD_PERIOD_LOCAL
        game.online_score_cache = {}
        game.online_score_loaded = set()
        game.online_rank_cache = {}
        game.online_sync_pending = False
        game.online_syncing = False
        game.online_sync_wait = 0
        game.online_profile = {
            "user_name": "ace",
            "local_only": False,
            "server_token": "tok",
            "next_sync_at": "2999-01-01T00:00:00Z",
        }
        loaded = []
        old_sync = rogue.sync_online_scoreboard
        old_load = rogue.load_score_entries
        try:
            rogue.load_score_entries = lambda: [{"score": 42, "player_name": "ace", "period_week": "2026-W18"}]
            rogue.sync_online_scoreboard = lambda profile, entries: self.fail("cooldown select must not POST sync")
            game.load_online_period_scores = lambda period, force=False: loaded.append((period, force)) or []

            rogue.pyxel.set_input(held={rogue.pyxel.KEY_TAB}, pressed={rogue.pyxel.KEY_TAB})
            game.update()
            rogue.pyxel.set_input()
            game.update()
            rogue.pyxel.set_input()
            game.update()
            rogue.pyxel.set_input()
            game.update()
        finally:
            rogue.sync_online_scoreboard = old_sync
            rogue.load_score_entries = old_load

        self.assertEqual(loaded, [
            (rogue.SCOREBOARD_PERIOD_WEEKLY, True),
            (rogue.SCOREBOARD_PERIOD_SEASON, True),
        ])
        self.assertEqual(game.online_sync_result, "Score sync available later. Ranking updated.")

    def test_online_score_screen_cancel_is_safe_before_new_game_initializes_input_guards(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_ONLINE_SCORE
        game.online_period = rogue.SCOREBOARD_PERIOD_LOCAL
        game.online_score_cache = {}
        game.online_score_loaded = set()
        game.online_sync_pending = False
        game.online_syncing = False

        rogue.pyxel.set_input()
        game.update()

        self.assertEqual(game.st, rogue.ST_ONLINE_SCORE)

    def test_score_screen_after_game_over_opens_shared_local_scoreboard_and_returns_title(self):
        game = new_game(seed=35)
        game.st = rogue.ST_SCORE

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_RETURN}, pressed={rogue.pyxel.KEY_RETURN})
        game.update()

        self.assertEqual(game.st, rogue.ST_ONLINE_SCORE)
        self.assertEqual(game.online_return_state, rogue.ST_TITLE)
        self.assertEqual(game.online_period, rogue.SCOREBOARD_PERIOD_LOCAL)
        self.assertFalse(game.online_sync_pending)

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_ESCAPE}, pressed={rogue.pyxel.KEY_ESCAPE})
        game.update()
        rogue.pyxel.set_input(held={rogue.pyxel.KEY_ESCAPE}, pressed={rogue.pyxel.KEY_ESCAPE})
        game.update()
        self.assertEqual(game.st, rogue.ST_TITLE)

    def test_game_end_saves_local_score_without_online_submit(self):
        for outcome in ("quit", "killed", "winner"):
            game = new_game(seed=35)
            game.death_cause = "killed by a kestrel"
            saved = []
            old_save = rogue.save_score_entry
            old_submit = rogue.submit_online_score
            old_load = rogue.load_score_entries
            try:
                rogue.save_score_entry = lambda entry: saved.append(entry)
                rogue.submit_online_score = lambda entry: self.fail("game end must not submit online score")
                rogue.load_score_entries = lambda: saved[:]

                game.enter_result_state(outcome)
            finally:
                rogue.save_score_entry = old_save
                rogue.submit_online_score = old_submit
                rogue.load_score_entries = old_load

            self.assertEqual(len(saved), 1, outcome)
            self.assertIn(game.st, (rogue.ST_QUIT, rogue.ST_DEAD, rogue.ST_WIN), outcome)

    def test_online_score_pending_sync_can_be_cancelled_before_fetch(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_ONLINE_SCORE
        game.online_period = rogue.SCOREBOARD_PERIOD_LOCAL
        game.online_score_cache = {}
        game.online_score_loaded = set()
        game.online_rank_cache = {}
        game.online_sync_pending = True
        game.online_syncing = True
        game.online_sync_wait = 1
        game.online_sync_force = True
        game.online_sync_periods = [rogue.SCOREBOARD_PERIOD_WEEKLY]
        game.load_online_period_scores = lambda period=None, force=False: self.fail("B must cancel before fetch")

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_ESCAPE}, pressed={rogue.pyxel.KEY_ESCAPE})
        game.update()

        self.assertEqual(game.st, rogue.ST_TITLE)
        self.assertFalse(game.online_sync_pending)
        self.assertFalse(game.online_syncing)
        self.assertEqual(game.online_sync_periods, [])

    def test_online_score_sync_posts_local_scores_inside_scoreboard(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_ONLINE_SCORE
        game.online_period = rogue.SCOREBOARD_PERIOD_LOCAL
        game.online_score_cache = {}
        game.online_score_loaded = set()
        game.online_rank_cache = {}
        game.online_sync_pending = True
        game.online_syncing = True
        game.online_sync_wait = 1
        game.online_sync_force = True
        game.online_sync_periods = [rogue.SCOREBOARD_PERIOD_WEEKLY]
        game.online_profile = {"user_name": "ace", "local_only": False, "server_token": "tok"}
        game.result_entry = {"score": 42, "player_name": "ace", "result_flags": "quit", "level": 1, "timestamp": "t"}
        game.result_online_submitted = False
        synced = []
        old_sync = rogue.sync_online_scoreboard
        old_load = rogue.load_score_entries
        try:
            rogue.load_score_entries = lambda: [game.result_entry]
            rogue.sync_online_scoreboard = lambda profile, entries: synced.append((profile, entries)) or {
                "ok": True,
                "status": "success",
                "last_sync_at": "2026-05-01T00:00:00Z",
                "next_sync_at": "2026-05-02T00:00:00Z",
                "scores": {"weekly": [], "season": []},
            }

            rogue.pyxel.set_input()
            game.update()
            rogue.pyxel.set_input()
            game.update()
        finally:
            rogue.sync_online_scoreboard = old_sync
            rogue.load_score_entries = old_load

        self.assertEqual(synced[0][1][0]["score"], game.result_entry["score"])
        self.assertEqual(game.online_sync_result, "Score synced.")

    def test_online_score_sync_without_local_scores_skips_post_and_loads_scoreboard(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_ONLINE_SCORE
        game.online_period = rogue.SCOREBOARD_PERIOD_LOCAL
        game.online_score_cache = {}
        game.online_score_loaded = set()
        game.online_rank_cache = {}
        game.online_sync_pending = True
        game.online_syncing = True
        game.online_sync_wait = 0
        game.online_sync_force = True
        game.online_sync_periods = [rogue.SCOREBOARD_PERIOD_WEEKLY]
        game.online_profile = {"user_name": "ace", "local_only": False, "server_token": "tok"}
        old_sync = rogue.sync_online_scoreboard
        old_load = rogue.load_score_entries
        loaded = []
        try:
            rogue.load_score_entries = lambda: []
            rogue.sync_online_scoreboard = lambda profile, entries: self.fail("empty local score list must not POST sync")
            game.load_online_period_scores = lambda period, force=False: loaded.append((period, force)) or []

            rogue.pyxel.set_input()
            game.update()
        finally:
            rogue.sync_online_scoreboard = old_sync
            rogue.load_score_entries = old_load

        self.assertEqual(game.online_sync_result, "Ranking updated. No local scores yet.")
        self.assertEqual(loaded, [(rogue.SCOREBOARD_PERIOD_WEEKLY, True)])

    def test_online_scoreboard_load_failure_does_not_overwrite_sync_success(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.online_score_cache = {}
        game.online_score_loaded = set()
        game.online_rank_cache = {}
        game.online_sync_periods = [rogue.SCOREBOARD_PERIOD_WEEKLY]
        game.online_profile = {"user_name": "ace", "local_only": False, "server_token": "tok"}
        old_sync = rogue.sync_online_scoreboard
        old_load = rogue.load_score_entries
        try:
            rogue.load_score_entries = lambda: [{"score": 42, "player_name": "ace", "period_week": "2026-W18"}]
            rogue.sync_online_scoreboard = lambda profile, entries: {"ok": True, "status": "success"}
            game.load_online_period_scores = lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("fetch failed"))

            game.perform_online_scoreboard_sync()
        finally:
            rogue.sync_online_scoreboard = old_sync
            rogue.load_score_entries = old_load

        self.assertEqual(game.online_sync_result, "Score synced.")
        self.assertEqual(game.online_score_load_result, "Could not load scoreboard.")

    def test_online_score_server_cooldown_loads_scoreboard_without_sync_success(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.online_score_cache = {}
        game.online_score_loaded = set()
        game.online_rank_cache = {}
        game.online_sync_periods = [rogue.SCOREBOARD_PERIOD_WEEKLY]
        game.online_profile = {"user_name": "ace", "local_only": False, "server_token": "tok"}
        loaded = []
        old_sync = rogue.sync_online_scoreboard
        old_load = rogue.load_score_entries
        try:
            rogue.load_score_entries = lambda: [{"score": 42, "player_name": "ace", "period_week": "2026-W18"}]
            rogue.sync_online_scoreboard = lambda profile, entries: {"ok": False, "status": "cooldown"}
            game.load_online_period_scores = lambda period, force=False: loaded.append((period, force)) or []

            game.perform_online_scoreboard_sync()
        finally:
            rogue.sync_online_scoreboard = old_sync
            rogue.load_score_entries = old_load

        self.assertEqual(game.online_sync_result, "Score sync available later. Ranking updated.")
        self.assertEqual(loaded, [(rogue.SCOREBOARD_PERIOD_WEEKLY, True)])

    def test_online_score_tabs_do_not_sync_and_refresh_syncs_all_periods(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_ONLINE_SCORE
        game.online_period = rogue.SCOREBOARD_PERIOD_LOCAL
        game.online_profile = {"user_name": "ace", "local_only": False, "server_token": "tok"}
        game.online_score_cache = {}
        game.online_score_loaded = set()
        game.online_rank_cache = {}
        game.online_sync_pending = False
        game.online_syncing = False
        game.online_sync_wait = 0
        calls = []
        loaded = []
        old_sync = rogue.sync_online_scoreboard
        old_load = rogue.load_score_entries
        try:
            rogue.load_score_entries = lambda: []
            rogue.sync_online_scoreboard = lambda profile, entries: calls.append((profile, entries)) or {
                "ok": True,
                "status": "success",
                "scores": {"weekly": [], "season": []},
            }
            game.load_online_period_scores = lambda period, force=False: loaded.append((period, force)) or []

            rogue.pyxel.set_input(held={rogue.pyxel.KEY_RIGHT}, pressed={rogue.pyxel.KEY_RIGHT})
            game.update()
            self.assertEqual(game.online_period, rogue.SCOREBOARD_PERIOD_WEEKLY)
            self.assertFalse(game.online_sync_pending)
            self.assertEqual(calls, [])

            rogue.pyxel.set_input(held={rogue.pyxel.KEY_TAB}, pressed={rogue.pyxel.KEY_TAB})
            game.update()
            rogue.pyxel.set_input()
            game.update()
            self.assertTrue(game.online_sync_pending)
            rogue.pyxel.set_input()
            game.update()
            rogue.pyxel.set_input()
            game.update()
        finally:
            rogue.sync_online_scoreboard = old_sync
            rogue.load_score_entries = old_load
        self.assertEqual(calls, [])
        self.assertEqual(loaded, [
            (rogue.SCOREBOARD_PERIOD_WEEKLY, True),
            (rogue.SCOREBOARD_PERIOD_SEASON, True),
        ])

    def test_online_score_fetch_merges_local_scores_without_resubmitting(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.online_period = rogue.SCOREBOARD_PERIOD_WEEKLY
        game.online_score_cache = {}
        game.online_score_loaded = set()
        game.online_rank_cache = {}
        old_fetch = rogue.fetch_online_scores
        old_load = rogue.load_score_entries
        old_sync = rogue.sync_missing_local_best
        keys = rogue.score_period_keys()
        try:
            rogue.fetch_online_scores = lambda period, timestamp=None: [
                {"player_name": "DOT", "score": 20, "period_week": keys["period_week"], "period_season": keys["period_season"]}
            ]
            rogue.load_score_entries = lambda: [
                {"player_name": "ACE", "score": 300, "period_week": keys["period_week"], "period_season": keys["period_season"]}
            ]
            rogue.sync_missing_local_best = lambda *args, **kwargs: self.fail("score fetch must not post local best")

            scores = game.load_online_period_scores(rogue.SCOREBOARD_PERIOD_WEEKLY)
        finally:
            rogue.fetch_online_scores = old_fetch
            rogue.load_score_entries = old_load
            rogue.sync_missing_local_best = old_sync

        self.assertEqual([(e["player_name"], e["score"]) for e in scores], [("ACE", 300), ("DOT", 20)])

    def test_online_score_draw_uses_rogue_score_lines_title_and_player_highlight(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.lang = rogue.LANG_EN
        game.player_name = "ace"
        game.online_profile = {
            "user_name": "ace",
            "local_only": False,
            "server_token": "tok",
            "last_sync_at": "2026-05-01T00:00:00Z",
            "profile_exists": True,
        }
        game.online_period = rogue.SCOREBOARD_PERIOD_WEEKLY
        game.online_score_cache = {
            rogue.SCOREBOARD_PERIOD_WEEKLY: [
                {"score": 346, "player_name": "masatora", "result_flags": "killed", "level": 4, "killer": "orc"},
                {"score": 194, "player_name": "ace", "result_flags": "killed", "level": 3, "killer": "bat"},
            ]
        }
        game.online_score_loaded = {rogue.SCOREBOARD_PERIOD_WEEKLY}
        game.online_syncing = True
        game.result_entry = {
            "player_name": "ace",
            "score": 12,
            "result_flags": "killed",
            "level": 2,
            "killer": "bat",
        }
        game.online_rank_cache = {rogue.SCOREBOARD_PERIOD_WEEKLY: 123}
        game.load_online_period_scores = lambda *args, **kwargs: self.fail("draw must not fetch")
        game.scoreboard_period_label = lambda period, timestamp=None: "2026-W18"
        game.scoreboard_period_ends_line = lambda period: "Ends in 03h 12m 45s  UTC 2026-05-01 00:00"
        drawn = []
        game._box = lambda *args: drawn.append(("box", args))
        game.txt = lambda x, y, s, c: drawn.append((str(s), c, x, y))
        old_load = rogue.load_score_entries
        try:
            rogue.load_score_entries = lambda: []

            game.draw_online_score_screen()
        finally:
            rogue.load_score_entries = old_load

        text = "\n".join(str(item) for item in drawn)
        self.assertIn("Weekly Rivals - 2026-W18", text)
        self.assertIn("UTC", text)
        self.assertIn("Score Name", text)
        self.assertIn(" 1   346 masatora: killed on level 4 by an orc.", text)
        self.assertIn("'sync'", text)
        self.assertIn("123", text)
        self.assertIn("ace", text)
        self.assertIn("killed", text)
        self.assertIn("bat", text)
        self.assertIn("Ends in 03h 12m 45s  UTC 2026-05-01 00:00", text)
        self.assertIn((" 2   194 ace: killed on level 3 by a bat.", 23, 120, 103), drawn)
        self.assertIn((" 1   346 masatora: killed on level 4 by an orc.", 30, 120, 90), drawn)
        self.assertIn(("123    12 ace: killed on level 2 by a bat.", 30, 120, 222), drawn)
        self.assertNotIn(("SYNCING...", 23, 410, 55), drawn)
        self.assertNotIn(("SYNCING...", 23, 120, 116), drawn)
        self.assertLess(drawn.index((" 1   346 masatora: killed on level 4 by an orc.", 30, 120, 90)), drawn.index(("box", (156, 116, 268, 82, "sync"))))

    def test_online_score_draw_merges_cached_weekly_with_local_best_without_fetching(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.lang = rogue.LANG_EN
        game.player_name = "rogue54b"
        game.online_profile = {"user_name": "rogue54b", "local_only": False, "server_token": "tok", "profile_exists": True}
        game.online_period = rogue.SCOREBOARD_PERIOD_WEEKLY
        key = rogue.score_period_keys()["period_week"]
        game.online_score_cache = {
            rogue.SCOREBOARD_PERIOD_WEEKLY: [
                {"score": 1320, "player_name": "6502", "period_week": key, "result_flags": "killed", "level": 15, "killer": "vampire"},
                {"score": 631, "player_name": "algol", "period_week": key, "result_flags": "killed", "level": 5, "killer": "orc"},
                {"score": 480, "player_name": "fortran", "period_week": key, "result_flags": "killed", "level": 3, "killer": "hobgoblin"},
            ]
        }
        game.online_score_loaded = {rogue.SCOREBOARD_PERIOD_WEEKLY}
        game.online_syncing = False
        game.online_rank_cache = {}
        old_load = rogue.load_score_entries
        try:
            rogue.load_score_entries = lambda: [
                {"score": 624, "player_name": "rogue54b", "period_week": key, "result_flags": "quit", "level": 5, "killer": ""}
            ]
            game.load_online_period_scores = lambda *args, **kwargs: self.fail("draw must not fetch")
            drawn = []
            game._box = lambda *args: drawn.append(("box", args))
            game.txt = lambda x, y, s, c: drawn.append((str(s), c, x, y))

            game.draw_online_score_screen()
        finally:
            rogue.load_score_entries = old_load

        text = "\n".join(str(item) for item in drawn)
        self.assertIn(" 2   631 algol: killed on level 5 by an orc.", text)
        self.assertIn(" 3   624 rogue54b: quit on level 5.", text)
        self.assertIn(" 4   480 fortran: killed on level 3 by a hobgoblin.", text)

    def test_online_score_result_line_does_not_overlap_period_end_line(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.lang = rogue.LANG_EN
        game.online_profile = {"user_name": "ace", "local_only": False, "server_token": "tok"}
        game.online_period = rogue.SCOREBOARD_PERIOD_WEEKLY
        game.online_score_cache = {rogue.SCOREBOARD_PERIOD_WEEKLY: []}
        game.online_score_loaded = {rogue.SCOREBOARD_PERIOD_WEEKLY}
        game.online_syncing = False
        game.online_sync_result = "No local scores yet."
        game.scoreboard_period_ends_line = lambda period: "This Week ends in 3d 00h 00m at UTC 2026-05-04 00:00"
        game.load_online_period_scores = lambda *args, **kwargs: self.fail("draw must not fetch")
        drawn = []
        game._box = lambda *args: drawn.append(("box", args))
        game.txt = lambda x, y, s, c: drawn.append((str(s), c, x, y))

        game.draw_online_score_screen()

        y_by_text = {item[0]: item[3] for item in drawn if len(item) == 4 and isinstance(item[0], str)}
        self.assertEqual(y_by_text["No local scores yet."], 56)
        self.assertEqual(y_by_text["This Week ends in 3d 00h 00m at UTC 2026-05-04 00:00"], 252)

    def test_enter_online_scoreboard_clears_stale_no_local_scores_when_local_score_exists(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.apply_palette = lambda: None
        game.online_sync_result = "No local scores yet."
        game.online_profile = {"user_name": "ace", "local_only": False, "server_token": "tok", "profile_exists": True}
        old_load = rogue.load_score_entries
        try:
            rogue.load_score_entries = lambda: [{"score": 730, "player_name": "ace", "period_week": "2026-W18"}]
            game.enter_online_scoreboard(auto_sync=False)
        finally:
            rogue.load_score_entries = old_load

        self.assertEqual(game.online_sync_result, "")

    def test_local_scoreboard_draws_my_rogue_chronicle_and_local_name_mark(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.lang = rogue.LANG_EN
        game.player_name = "ace"
        game.online_profile = {"user_name": "ace", "local_only": True, "profile_exists": True}
        game.online_period = rogue.SCOREBOARD_PERIOD_LOCAL
        game.online_score_cache = {
            rogue.SCOREBOARD_PERIOD_LOCAL: [
                {"score": 194, "player_name": "ace", "result_flags": "quit", "level": 3, "killer": ""},
            ]
        }
        game.online_syncing = False
        game.online_register_prompt = False
        game.load_online_period_scores = lambda period=None, force=False: game.online_score_cache[rogue.SCOREBOARD_PERIOD_LOCAL]
        drawn = []
        game._box = lambda *args: drawn.append(("box", args))
        game.txt = lambda x, y, s, c: drawn.append((str(s), c, x, y))

        game.draw_online_score_screen()

        text = "\n".join(str(item) for item in drawn)
        self.assertIn("My Rogue Chronicle - Local", text)
        self.assertIn("ace*: quit on level 3.", text)
        self.assertIn("Local only. Select opens online registration.", text)

    def test_online_score_period_end_lines_use_utc_rank_windows(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()

        self.assertEqual(
            game.scoreboard_period_ends_line(rogue.SCOREBOARD_PERIOD_WEEKLY, "2026-04-30T20:47:15Z"),
            "This Week ends in 3d 03h 12m at UTC 2026-05-04 00:00",
        )
        self.assertEqual(
            game.scoreboard_period_ends_line(rogue.SCOREBOARD_PERIOD_SEASON, "2026-04-30T20:47:15Z"),
            "This Season ends in 4w 3d 03h 12m at UTC 2026-06-01 00:00",
        )

    def test_online_sync_hint_line_uses_compact_utc_last_sync_for_all_boards(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.online_profile = {
            "user_name": "ace",
            "local_only": False,
            "server_token": "tok",
            "last_sync_at": "2026-05-03T03:45:12Z",
            "next_sync_at": "2026-05-04T03:45:12Z",
            "profile_exists": True,
        }

        self.assertEqual(game.scoreboard_period_label(rogue.SCOREBOARD_PERIOD_WEEKLY, "2026-04-30T20:47:15Z"), "2026-W18")
        self.assertEqual(game.scoreboard_period_label(rogue.SCOREBOARD_PERIOD_SEASON, "2026-04-30T20:47:15Z"), "2026-Spring")
        self.assertEqual(game.online_sync_hint_line(), "Last sync UTC 2026-05-03 03:45")

    def test_logo_auto_fades_on_bgm_bar_timing_and_can_be_skipped(self):
        self.assertEqual(rogue.LOGO_BGM_DELAY_FRAMES, 78)
        self.assertEqual(rogue.LOGO_HOLD_FRAMES, 78)
        self.assertEqual(rogue.LOGO_TOTAL_FRAMES, 312)
        self.assertEqual(rogue.TITLE_FADE_FRAMES, 156)
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_LOGO
        game.logo_frames = 0
        game.online_profile = {"user_name": "ace", "local_only": True, "profile_exists": True}

        for _ in range(rogue.LOGO_TOTAL_FRAMES - 1):
            rogue.pyxel.set_input()
            game.update()
        self.assertEqual(game.st, rogue.ST_LOGO)
        rogue.pyxel.set_input()
        game.update()
        self.assertEqual(game.st, rogue.ST_TITLE)

        game.st = rogue.ST_LOGO
        game.logo_frames = 0
        rogue.pyxel.set_input(held={rogue.pyxel.KEY_RETURN}, pressed={rogue.pyxel.KEY_RETURN})
        game.update()
        self.assertEqual(game.st, rogue.ST_TITLE)

    def test_logo_and_title_bgm_starts_once_and_stops_on_new_game(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_LOGO
        game.logo_frames = 0
        game.online_profile = {"user_name": "ace", "local_only": True, "profile_exists": True}
        rogue.pyxel.play_calls.clear()
        rogue.pyxel.stop_calls.clear()

        rogue.pyxel.set_input()
        game.update()
        self.assertEqual(
            rogue.pyxel.play_calls,
            [
                ((0, 0), {"loop": True}),
                ((1, 1), {"loop": True}),
                ((2, 2), {"loop": True}),
            ],
        )

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_RETURN}, pressed={rogue.pyxel.KEY_RETURN})
        game.update()
        self.assertEqual(game.st, rogue.ST_TITLE)
        self.assertEqual(len(rogue.pyxel.play_calls), 3)

        game.title_cursor = 0
        game.title_fade_frames = rogue.TITLE_FADE_FRAMES
        game.new_game = lambda: None
        game.current_player_name = lambda: "ACE"
        rogue.pyxel.set_input(held={rogue.pyxel.KEY_RETURN}, pressed={rogue.pyxel.KEY_RETURN})
        game.update()

        self.assertEqual(game.st, rogue.ST_TITLE)
        self.assertEqual(rogue.pyxel.stop_calls, [((0,), {}), ((1,), {}), ((2,), {})])
        self.assertEqual(len(rogue.pyxel.play_calls), 3)
        for _ in range(rogue.TITLE_BGM_STOP_WAIT_FRAMES - 1):
            rogue.pyxel.set_input()
            game.update()
            self.assertEqual(game.st, rogue.ST_TITLE)
        rogue.pyxel.set_input()
        game.update()

        self.assertEqual(game.st, rogue.ST_PLAY)
        self.assertEqual(rogue.pyxel.stop_calls, [((0,), {}), ((1,), {}), ((2,), {})])

    def test_logo_does_not_request_dummy_seed(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_LOGO
        game.logo_frames = 0

        rogue.pyxel.set_input()
        game.update()
        rogue.pyxel.set_input()
        game.update()

        self.assertFalse(hasattr(game, "logo_seed_requested"))

    def test_logo_and_title_use_bright_text_without_press_any_key_hint(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.player_name = "ACE"
        game.title_cursor = 0
        game.title_bg = object()
        game.title_fade_frames = rogue.TITLE_FADE_FRAMES
        calls = []
        game.txt = lambda x, y, s, c: calls.append((str(s), c, x))

        game.logo_frames = 45
        game.draw_logo_screen()
        self.assertIn(("hann-solo laboratory", 23, rogue.SCR_W // 2 - len("hann-solo laboratory") * 3), calls)
        self.assertFalse(any("PRESS ANY KEY" in text for text, _c, _x in calls))

        calls.clear()
        rogue.pyxel.blt_calls.clear()
        rogue.pyxel.rect_calls.clear()
        game.draw_title_screen()
        self.assertEqual(rogue.pyxel.blt_calls[0][0], (0, 0, game.title_bg, 0, 0, rogue.SCR_W, rogue.SCR_H))
        self.assertIn(((344, 228, 174, 84, 0), {}), rogue.pyxel.rect_calls)
        self.assertFalse(any(text == "ROGUE V5" for text, _c, _x in calls))
        self.assertFalse(any(text == "ローグ" for text, _c, _x in calls))
        self.assertFalse(any(text == "ver 5.4" for text, _c, _x in calls))
        self.assertTrue(any(text == "START" and c == 9 for text, c, _x in calls))
        self.assertFalse(any("A/Start" in text for text, _c, _x in calls))

    def test_title_background_dither_fades_in_and_input_finishes_fade(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_TITLE
        game.title_cursor = 0
        game.title_bg = object()
        game.title_fade_frames = 0
        game.player_name = "ACE"
        game.txt = lambda x, y, s, c: None

        rogue.pyxel.set_input()
        game.update()
        rogue.pyxel.dither_calls.clear()
        rogue.pyxel.rect_calls.clear()
        game.draw_title_screen()
        self.assertLess(rogue.pyxel.dither_calls[0], 1.0)
        self.assertFalse(rogue.pyxel.rect_calls)

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_DOWN}, pressed={rogue.pyxel.KEY_DOWN})
        game.update()
        self.assertEqual(game.title_fade_frames, rogue.TITLE_FADE_FRAMES)
        self.assertEqual(game.title_cursor, 0)
        rogue.pyxel.set_input(held={rogue.pyxel.KEY_DOWN}, pressed={rogue.pyxel.KEY_DOWN})
        game.update()
        self.assertEqual(game.title_cursor, 1)
        rogue.pyxel.dither_calls.clear()
        rogue.pyxel.rect_calls.clear()
        game.draw_title_screen()
        self.assertEqual(rogue.pyxel.dither_calls[0], 1.0)
        self.assertIn(((344, 228, 174, 84, 0), {}), rogue.pyxel.rect_calls)

    def test_title_start_during_fade_only_finishes_fade(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_TITLE
        game.title_cursor = 0
        game.title_fade_frames = 12
        game.player_name = "ACE"

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_RETURN}, pressed={rogue.pyxel.KEY_RETURN})
        game.update()

        self.assertEqual(game.st, rogue.ST_TITLE)
        self.assertEqual(game.title_fade_frames, rogue.TITLE_FADE_FRAMES)
        self.assertEqual(getattr(game, "title_bgm_stop_wait", 0), 0)

    def test_title_screen_uses_dedicated_palette_and_restores_game_palette_on_exit(self):
        old_colors = getattr(rogue.pyxel, "colors", None)
        try:
            rogue.pyxel.colors = [0] * len(rogue.TITLE_BG_PALETTE)
            game = rogue.Game.__new__(rogue.Game)
            game.settings = rogue.Settings()
            game.title_fade_frames = 0
            game.st = rogue.ST_LOGO

            game.enter_title_screen()
            self.assertEqual(rogue.pyxel.colors[: len(rogue.TITLE_BG_PALETTE)], list(rogue.TITLE_BG_PALETTE))

            game.open_name_input()
            self.assertEqual(
                rogue.pyxel.colors[: len(rogue.GBC_HIGH_CONTRAST_PALETTE)],
                rogue.GBC_HIGH_CONTRAST_PALETTE,
            )
        finally:
            if old_colors is None:
                del rogue.pyxel.colors
            else:
                rogue.pyxel.colors = old_colors

    def test_palette_application_does_not_append_to_fixed_pyxel_colors(self):
        class FixedColors:
            def __init__(self, size):
                self.values = [0] * size

            def __len__(self):
                return len(self.values)

            def __getitem__(self, index):
                return self.values[index]

            def __setitem__(self, index, value):
                self.values[index] = value

        game = rogue.Game.__new__(rogue.Game)
        old_colors = getattr(rogue.pyxel, "colors", None)
        try:
            rogue.pyxel.colors = FixedColors(16)
            game.apply_palette_values(rogue.TITLE_BG_PALETTE)
            self.assertEqual(rogue.pyxel.colors.values, list(rogue.TITLE_BG_PALETTE[:16]))
        finally:
            if old_colors is None:
                del rogue.pyxel.colors
            else:
                rogue.pyxel.colors = old_colors

    def test_palette_application_extends_appendable_pyxel_colors(self):
        game = rogue.Game.__new__(rogue.Game)
        old_colors = getattr(rogue.pyxel, "colors", None)
        try:
            rogue.pyxel.colors = [0] * 16
            game.apply_palette_values(rogue.TITLE_BG_PALETTE)
            self.assertEqual(rogue.pyxel.colors, list(rogue.TITLE_BG_PALETTE))
        finally:
            if old_colors is None:
                del rogue.pyxel.colors
            else:
                rogue.pyxel.colors = old_colors

    def test_logo_dither_fades_in_holds_and_fades_out(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.txt = lambda x, y, s, c: None

        rogue.pyxel.dither_calls.clear()
        game.logo_frames = rogue.LOGO_BGM_DELAY_FRAMES - 1
        game.draw_logo_screen()
        delayed = rogue.pyxel.dither_calls[:]

        rogue.pyxel.dither_calls.clear()
        game.logo_frames = rogue.LOGO_BGM_DELAY_FRAMES + 1
        game.draw_logo_screen()
        early = rogue.pyxel.dither_calls[:]

        rogue.pyxel.dither_calls.clear()
        game.logo_frames = rogue.LOGO_BGM_DELAY_FRAMES + rogue.LOGO_FADE_FRAMES
        game.draw_logo_screen()
        hold = rogue.pyxel.dither_calls[:]

        rogue.pyxel.dither_calls.clear()
        game.logo_frames = (
            rogue.LOGO_BGM_DELAY_FRAMES
            + rogue.LOGO_FADE_FRAMES
            + rogue.LOGO_HOLD_FRAMES
            + rogue.LOGO_FADE_FRAMES // 2
        )
        game.draw_logo_screen()
        late = rogue.pyxel.dither_calls[:]

        rogue.pyxel.dither_calls.clear()
        game.logo_frames = rogue.LOGO_TOTAL_FRAMES
        game.draw_logo_screen()
        black_hold = rogue.pyxel.dither_calls[:]

        self.assertEqual(delayed[0], 0.0)
        self.assertLess(early[0], 1.0)
        self.assertEqual(hold[0], 1.0)
        self.assertLess(late[0], 1.0)
        self.assertEqual(black_hold[0], 0.0)
        self.assertEqual((delayed[-1], early[-1], hold[-1], late[-1], black_hold[-1]), (1.0, 1.0, 1.0, 1.0, 1.0))

    def test_name_input_confirms_with_start_and_backspace_deletes(self):
        game = rogue.Game.__new__(rogue.Game)
        game.settings = rogue.Settings()
        game.st = rogue.ST_NAME
        game.name_chars = list("ACE")
        game.name_pos = 2
        game.name_pick = 0
        game.player_name = "ACE"
        game.title_cursor = 2

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_ESCAPE}, pressed={rogue.pyxel.KEY_ESCAPE})
        game.update()
        self.assertEqual("".join(game.name_chars).strip(), "AC")

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_SPACE}, pressed={rogue.pyxel.KEY_SPACE})
        game.update()
        self.assertEqual(game.st, rogue.ST_TITLE)
        self.assertEqual(game.player_name, "ac")

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

    def test_result_screens_advance_to_shared_local_scoreboard(self):
        for state in (rogue.ST_DEAD, rogue.ST_WIN, rogue.ST_QUIT):
            game = new_game(seed=35)
            game.st = state

            rogue.pyxel.set_input(held={rogue.pyxel.KEY_RETURN}, pressed={rogue.pyxel.KEY_RETURN})
            game.update()

            self.assertEqual(game.st, rogue.ST_ONLINE_SCORE, state)
            self.assertEqual(game.online_period, rogue.SCOREBOARD_PERIOD_LOCAL)
            self.assertFalse(game.online_sync_pending)

    def test_legacy_score_screen_confirm_opens_shared_local_scoreboard(self):
        game = new_game(seed=35)
        game.st = rogue.ST_SCORE
        game.turn = 12

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_RETURN}, pressed={rogue.pyxel.KEY_RETURN})
        game.update()

        self.assertEqual(game.st, rogue.ST_ONLINE_SCORE)
        self.assertEqual(game.turn, 12)

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

    def test_rogue_544_thrown_attack_resets_quiet_and_runto(self):
        # Rogue 5.4.4 weapons.c:missile() resolves through fight.c:fight(..., thrown=TRUE).
        game = new_game(seed=373)
        set_open_floor(game)
        arrow = rogue.Item(rogue.CAT_WPN, 3, qty=1)
        monster = monster_at(game.p.x + 2, game.p.y, hp=10, exp=0)
        monster.running = False
        monster.held = 3
        game.p.quiet = 9
        game.roll_player_attack = lambda m, weap=None, thrown=False: (False, 0)

        game.resolve_throw_anim({"outcome": {"kind": "monster", "monster": monster, "item": arrow, "x": monster.x, "y": monster.y}})

        self.assertEqual(game.p.quiet, 0)
        self.assertTrue(monster.running)
        self.assertEqual(monster.held, 0)

    def test_rogue_544_thrown_hit_consumes_monster_confusion(self):
        # Rogue 5.4.4 fight.c:fight(..., thrown=TRUE) applies CANHUH on a hit.
        game = new_game(seed=374)
        set_open_floor(game)
        arrow = rogue.Item(rogue.CAT_WPN, 3, qty=1)
        monster = monster_at(game.p.x + 2, game.p.y, name="hobgoblin", hp=10, exp=0)
        game.p.can_confuse_monster = True
        game.roll_player_attack = lambda m, weap=None, thrown=False: (True, 1)

        game.resolve_throw_anim({"outcome": {"kind": "monster", "monster": monster, "item": arrow, "x": monster.x, "y": monster.y}})

        self.assertFalse(game.p.can_confuse_monster)
        self.assertEqual(monster.confused, 1)
        self.assertIn("your hands stop glowing red", game.msgs)
        self.assertIn("the hobgoblin appears confused", game.msgs)

    def test_rogue_544_blind_thrown_confusion_hit_suppresses_appears_confused(self):
        # Rogue 5.4.4 fight.c:fight() prints appears confused only when !ISBLIND.
        game = new_game(seed=375)
        set_open_floor(game)
        arrow = rogue.Item(rogue.CAT_WPN, 3, qty=1)
        monster = monster_at(game.p.x + 2, game.p.y, name="hobgoblin", hp=10, exp=0)
        game.p.blind = 5
        game.p.can_confuse_monster = True
        game.roll_player_attack = lambda m, weap=None, thrown=False: (True, 1)

        game.resolve_throw_anim({"outcome": {"kind": "monster", "monster": monster, "item": arrow, "x": monster.x, "y": monster.y}})

        self.assertEqual(monster.confused, 1)
        self.assertNotIn("the hobgoblin appears confused", game.msgs)

    def test_rogue_544_thrown_existing_confusion_does_not_print_appears_confused(self):
        # Rogue 5.4.4 fight.c:fight() prints appears confused only when CANHUH was consumed.
        game = new_game(seed=376)
        set_open_floor(game)
        arrow = rogue.Item(rogue.CAT_WPN, 3, qty=1)
        monster = monster_at(game.p.x + 2, game.p.y, name="hobgoblin", hp=10, exp=0)
        monster.confused = 2
        game.roll_player_attack = lambda m, weap=None, thrown=False: (True, 1)

        game.resolve_throw_anim({"outcome": {"kind": "monster", "monster": monster, "item": arrow, "x": monster.x, "y": monster.y}})

        self.assertNotIn("the hobgoblin appears confused", game.msgs)

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

        self.assertEqual((game.p.hp, game.p.max_hp), (14, 14))

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

        self.assertEqual((game.p.hp, game.p.max_hp), (13, 13))

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

    def test_rogue_544_come_down_blind_suppresses_boring_message(self):
        # Rogue 5.4.4 daemons.c:come_down() returns before msg() while ISBLIND.
        game = new_game(seed=399)
        game.p.hallucinating = 10
        game.p.blind = 10

        game.come_down()

        self.assertEqual(game.p.hallucinating, 0)
        self.assertNotIn("Everything looks SO boring now.", game.msgs)

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

        self.assertEqual((game.p.hp, game.p.max_hp), (13, 13))
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
            held={rogue.pyxel.GAMEPAD1_BUTTON_START, rogue.pyxel.GAMEPAD1_BUTTON_B, rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT},
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
                rogue.pyxel.GAMEPAD1_BUTTON_START,
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

    def test_rogue_544_dash_look_ignores_unseen_diagonal_trap_behind_hidden_passage(self):
        # Rogue 5.4.4 misc.c:look() applies F_PASS/diagonal gates before door_stop checks.
        game = new_game(seed=464)
        game.rooms = []
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        game.p.x, game.p.y = 10, 10
        game.tm[10][10] = rogue.T_CORR
        game.tm[11][10] = rogue.T_CORR
        game.tm[9][10] = rogue.T_VOID
        game.hidden_tiles[(10, 9)] = rogue.T_CORR
        game.tm[10][11] = rogue.T_VOID
        game.tm[9][11] = rogue.T_TRAP
        game.update_fov()
        game.dash_steps = 1

        self.assertFalse(game.dash_look_stop(1, 0))

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
        self.assertEqual(rogue.MENU_ACTIONS[game.mcur][0], "Wear")

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

    def test_pad_action_menu_uses_radial_grid_with_eat_initial_cursor(self):
        game = new_game(seed=471)

        game.open_menu()
        self.assertEqual(rogue.MENU_ACTIONS[game.mcur][0], "Eat")

        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_LEFT},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_LEFT},
        )
        game.update()
        self.assertEqual(rogue.MENU_ACTIONS[game.mcur][0], "Quaff")

        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_UP},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_UP},
        )
        game.update()
        self.assertEqual(rogue.MENU_ACTIONS[game.mcur][0], "Zap")

        game.open_menu()
        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT},
        )
        game.update()
        self.assertEqual(rogue.MENU_ACTIONS[game.mcur][0], "Read")

        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_DOWN},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_DPAD_DOWN},
        )
        game.update()
        self.assertEqual(rogue.MENU_ACTIONS[game.mcur][0], "Take off")

    def test_pad_action_menu_can_open_call_discoveries_and_drop(self):
        game = new_game(seed=472)

        game.open_menu()
        game.mcur = next(i for i, (name, _cat) in enumerate(rogue.MENU_ACTIONS) if name == "Call")
        rogue.pyxel.set_input(held={rogue.pyxel.GAMEPAD1_BUTTON_A}, pressed={rogue.pyxel.GAMEPAD1_BUTTON_A})
        game.update()
        self.assertEqual(game.st, rogue.ST_CALL)

        game.open_menu()
        game.mcur = next(i for i, (name, _cat) in enumerate(rogue.MENU_ACTIONS) if name == "Discoveries")
        rogue.pyxel.set_input(held={rogue.pyxel.GAMEPAD1_BUTTON_A}, pressed={rogue.pyxel.GAMEPAD1_BUTTON_A})
        game.update()
        self.assertEqual(game.st, rogue.ST_DISC)

        game.open_menu()
        game.mcur = next(i for i, (name, _cat) in enumerate(rogue.MENU_ACTIONS) if name == "Drop")
        rogue.pyxel.set_input(held={rogue.pyxel.GAMEPAD1_BUTTON_A}, pressed={rogue.pyxel.GAMEPAD1_BUTTON_A})
        game.update()
        self.assertEqual(game.cact, "Drop")
        self.assertEqual(game.st, rogue.ST_ITEM)

    def test_select_tap_opens_inventory_then_select_tap_switches_to_assist(self):
        game = new_game(seed=473)

        rogue.pyxel.set_input(held={rogue.pyxel.GAMEPAD1_BUTTON_BACK}, pressed={rogue.pyxel.GAMEPAD1_BUTTON_BACK})
        game.update()
        self.assertEqual(game.st, rogue.ST_PLAY)

        rogue.pyxel.set_input()
        game.update()
        self.assertEqual(game.st, rogue.ST_INVENTORY)

        rogue.pyxel.set_input(held={rogue.pyxel.GAMEPAD1_BUTTON_BACK}, pressed={rogue.pyxel.GAMEPAD1_BUTTON_BACK})
        game.update()
        self.assertEqual(game.st, rogue.ST_INVENTORY)

        rogue.pyxel.set_input()
        game.update()
        self.assertEqual(game.st, rogue.ST_AUX)

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

    def test_rogue_544_invalid_diagonal_move_stops_running_without_turn(self):
        # Rogue 5.4.4 move.c:do_move() clears running and after=FALSE on !diag_ok().
        game = new_game(seed=489)
        set_open_floor(game)
        game.p.x, game.p.y = 5, 5
        game.tm[4][5] = rogue.T_HWALL
        game.dashing = True
        game.dash_steps = 2

        self.assertFalse(game.try_move(1, -1))
        self.assertFalse(game.dashing)
        self.assertEqual(game.turn, 0)
        self.assertEqual((game.p.x, game.p.y), (5, 5))

    def test_rogue_544_wall_move_stops_running_without_turn(self):
        # Rogue 5.4.4 move.c:do_move() hit_bound/wall branch clears running and after=FALSE.
        game = new_game(seed=488)
        set_open_floor(game)
        game.p.x, game.p.y = 5, 5
        game.tm[5][6] = rogue.T_VWALL
        game.dashing = True
        game.dash_steps = 2

        self.assertFalse(game.try_move(1, 0))
        self.assertFalse(game.dashing)
        self.assertEqual(game.turn, 0)
        self.assertEqual((game.p.x, game.p.y), (5, 5))

    def test_rogue_544_stair_move_stops_running_after_move(self):
        # Rogue 5.4.4 move.c:do_move() STAIRS falls through default and clears running.
        game = new_game(seed=487)
        set_open_floor(game)
        game.p.x, game.p.y = 5, 5
        game.tm[5][6] = rogue.T_STAIR
        game.dashing = True

        self.assertTrue(game.try_move(1, 0))
        self.assertFalse(game.dashing)
        self.assertEqual((game.p.x, game.p.y), (6, 5))
        self.assertTrue(game.seen_stairs)

    def test_rogue_544_item_move_stops_running_after_move(self):
        # Rogue 5.4.4 move.c:do_move() item winat() reaches default and clears running.
        game = new_game(seed=486)
        set_open_floor(game)
        game.p.x, game.p.y = 5, 5
        game.auto_pickup = False
        item = rogue.Item(rogue.CAT_FOOD, 0)
        item.x, item.y = 6, 5
        game.gitems = [item]
        game.dashing = True

        self.assertTrue(game.try_move(1, 0))
        self.assertFalse(game.dashing)
        self.assertEqual((game.p.x, game.p.y), (6, 5))
        self.assertIn("ration", game.msgs[-1])

    def test_rogue_544_door_move_stops_running_after_move(self):
        # Rogue 5.4.4 move.c:do_move() DOOR branch clears running before move_stuff.
        game = new_game(seed=485)
        set_open_floor(game)
        game.p.x, game.p.y = 5, 5
        game.tm[5][6] = rogue.T_DOOR
        game.dashing = True

        self.assertTrue(game.try_move(1, 0))
        self.assertFalse(game.dashing)
        self.assertEqual((game.p.x, game.p.y), (6, 5))

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

    def test_rogue_544_move_wakes_monsters_visible_before_command(self):
        # Rogue 5.4.4 command.c:command() calls misc.c:look(TRUE) before move.c:do_move().
        game = new_game(seed=5011)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 6, 5
        monster = monster_at(7, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.update_fov()

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            game.try_move(-1, 0)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertTrue(monster.running)
        self.assertEqual((monster.x, monster.y), (6, 5))

    def test_rogue_544_move_does_not_wake_newly_visible_monster_until_next_command(self):
        # Rogue 5.4.4 move.c:do_move() does not call look(TRUE) after hero movement.
        game = new_game(seed=5012)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        monster = monster_at(7, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.update_fov()

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            game.try_move(1, 0)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertFalse(monster.running)
        self.assertEqual((monster.x, monster.y), (7, 5))

    def test_rogue_544_no_command_turn_wakes_visible_monsters_before_decrement(self):
        # Rogue 5.4.4 command.c:command() calls misc.c:look(TRUE) before the no_command branch.
        game = new_game(seed=5013)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}
        game.p.no_command = 1

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            game.upd_play()
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertTrue(monster.running)
        self.assertEqual(monster.x, 7)

    def test_rogue_544_rest_command_wakes_visible_monsters_before_runners(self):
        # Rogue 5.4.4 command.c:command() calls misc.c:look(TRUE) before when '.': rest.
        game = new_game(seed=5014)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            game.do_wait()
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertTrue(monster.running)
        self.assertEqual(monster.x, 7)

    def test_rogue_544_search_command_wakes_visible_monsters_before_runners(self):
        # Rogue 5.4.4 command.c:command() calls misc.c:look(TRUE) before when 's': search().
        game = new_game(seed=5015)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            game.do_search(quiet_fail=True)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertTrue(monster.running)
        self.assertEqual(monster.x, 7)

    def test_rogue_544_pickup_command_wakes_visible_monsters_before_runners(self):
        # Rogue 5.4.4 command.c:command() calls misc.c:look(TRUE) before when ',': pick_up().
        game = new_game(seed=5016)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        item = rogue.Item(rogue.CAT_FOOD, 0)
        item.x, item.y = 5, 5
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.p.inv = []
        game.gitems = [item]
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            game.do_pickup()
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertTrue(monster.running)
        self.assertEqual(monster.x, 7)
        self.assertIn(item, game.p.inv)

    def test_rogue_544_pack_command_wakes_visible_monsters_before_drop(self):
        # Rogue 5.4.4 command.c:command() calls misc.c:look(TRUE) before pack commands such as drop().
        game = new_game(seed=5017)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        item = rogue.Item(rogue.CAT_FOOD, 0)
        game.p.inv = [item]
        game.gitems = []
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}
        game.cact = "Drop"

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            game.confirm_item(item)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertTrue(monster.running)
        self.assertEqual(monster.x, 7)
        self.assertEqual([(it.x, it.y) for it in game.gitems], [(5, 5)])

    def test_rogue_544_throw_command_wakes_visible_monsters_before_missile(self):
        # Rogue 5.4.4 command.c:command() calls misc.c:look(TRUE) before weapons.c:missile().
        game = new_game(seed=5019)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        item = rogue.Item(rogue.CAT_FOOD, 0)
        game.p.inv = [item]
        game.gitems = []
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}
        game.cact = "Throw"
        game.throw_dir = (0, -1)

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            game.confirm_item(item)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertTrue(monster.running)
        self.assertEqual(monster.x, 7)

    def test_rogue_544_zap_command_wakes_visible_monsters_before_do_zap(self):
        # Rogue 5.4.4 command.c:command() calls misc.c:look(TRUE) before sticks.c:do_zap().
        game = new_game(seed=5018)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        nothing = next(i for i, stick in enumerate(rogue.STICKS) if stick["name"] == "nothing")
        stick = rogue.Item(rogue.CAT_STICK, nothing, charges=1)
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.zap_item = stick
        game.dact = "Zap"
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            game.dir_confirm(1, 0)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertTrue(monster.running)
        self.assertEqual(monster.x, 7)
        self.assertEqual(stick.charges, 0)

    def test_rogue_544_pack_command_cancel_wakes_visible_monsters_at_prompt(self):
        # Rogue 5.4.4 command.c:command() calls misc.c:look(TRUE) before get_item() can cancel.
        game = new_game(seed=5020)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        item = rogue.Item(rogue.CAT_FOOD, 0)
        game.p.inv = [item]
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            game.start_item_action("Drop")
            game.close_menu()
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertTrue(monster.running)
        self.assertEqual(monster.x, 8)
        self.assertEqual(game.p.inv, [item])

    def test_rogue_544_menu_pack_command_cancel_wakes_visible_monsters_at_prompt(self):
        # Pyxel menu selection maps to Rogue 5.4.4 command.c readchar before pack.c:get_item().
        game = new_game(seed=5025)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        item = rogue.Item(rogue.CAT_FOOD, 0)
        game.p.inv = [item]
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}
        game.st = rogue.ST_MENU

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            game.start_item_action("Drop")
            game.close_menu()
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertTrue(monster.running)
        self.assertEqual(monster.x, 8)
        self.assertEqual(game.p.inv, [item])

    def test_rogue_544_pack_command_prompt_wakes_visible_monsters_once(self):
        # Rogue 5.4.4 command.c:command() has one misc.c:look(TRUE) before readchar/get_item.
        game = new_game(seed=5021)
        set_open_floor(game)
        game.p.x, game.p.y = 5, 5
        item = rogue.Item(rogue.CAT_FOOD, 0)
        game.p.inv = [item]
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}
        calls = []
        game.wake_visible_monsters = lambda: calls.append("wake")

        game.start_item_action("Drop")
        game.confirm_item(item)

        self.assertEqual(calls, ["wake"])

    def test_rogue_544_inventory_command_wakes_visible_monsters_without_turn(self):
        # Rogue 5.4.4 command.c:command() calls misc.c:look(TRUE) before when 'i': inventory().
        game = new_game(seed=5022)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            rogue.pyxel.set_input(pressed=[rogue.pyxel.KEY_I])
            game.begin_input()
            game.upd_play()
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.pyxel.set_input()

        self.assertTrue(monster.running)
        self.assertEqual((monster.x, monster.y), (8, 5))
        self.assertEqual(game.turn, 0)
        self.assertEqual(game.st, rogue.ST_INVENTORY)

    def test_rogue_544_discoveries_command_wakes_visible_monsters_without_turn(self):
        # Rogue 5.4.4 command.c:command() calls misc.c:look(TRUE) before when 'D': discovered().
        game = new_game(seed=5023)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            game.open_discoveries()
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertTrue(monster.running)
        self.assertEqual((monster.x, monster.y), (8, 5))
        self.assertEqual(game.turn, 0)
        self.assertEqual(game.st, rogue.ST_DISC)

    def test_rogue_544_trap_inspect_command_wakes_visible_monsters_without_turn(self):
        # Rogue 5.4.4 command.c:command() calls misc.c:look(TRUE) before when '^': trap inspect.
        game = new_game(seed=5024)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            game.inspect_trap(1, 0)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertTrue(monster.running)
        self.assertEqual((monster.x, monster.y), (8, 5))
        self.assertEqual(game.turn, 0)

    def test_rogue_544_help_command_wakes_visible_monsters_without_turn(self):
        # Rogue 5.4.4 command.c:command() calls misc.c:look(TRUE) before when '?': help().
        game = new_game(seed=5026)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            rogue.pyxel.set_input(pressed=[rogue.pyxel.KEY_QUESTION])
            game.begin_input()
            game.upd_play()
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.pyxel.set_input()

        self.assertTrue(monster.running)
        self.assertEqual((monster.x, monster.y), (8, 5))
        self.assertEqual(game.turn, 0)
        self.assertEqual(game.st, rogue.ST_HELP)

    def test_rogue_544_version_command_wakes_visible_monsters_without_turn(self):
        # Rogue 5.4.4 command.c:command() calls misc.c:look(TRUE) before when 'v': version.
        game = new_game(seed=5027)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            rogue.pyxel.set_input(pressed=[rogue.pyxel.KEY_V])
            game.begin_input()
            game.upd_play()
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.pyxel.set_input()

        self.assertTrue(monster.running)
        self.assertEqual((monster.x, monster.y), (8, 5))
        self.assertEqual(game.turn, 0)
        self.assertIn("version", game.msgs[-1])

    def test_rogue_544_illegal_command_wakes_visible_monsters_without_turn(self):
        # Rogue 5.4.4 command.c:command() calls misc.c:look(TRUE) before otherwise: illcom().
        game = new_game(seed=5028)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            rogue.pyxel.set_input(pressed=[rogue.pyxel.KEY_G])
            game.begin_input()
            game.upd_play()
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.pyxel.set_input()

        self.assertTrue(monster.running)
        self.assertEqual((monster.x, monster.y), (8, 5))
        self.assertEqual(game.turn, 0)
        self.assertIn("illegal command", game.msgs[-1])

    def test_rogue_544_options_command_wakes_visible_monsters_without_turn(self):
        # Rogue 5.4.4 command.c:command() calls misc.c:look(TRUE) before when 'o': option().
        game = new_game(seed=5029)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            rogue.pyxel.set_input(pressed=[rogue.pyxel.KEY_O])
            game.begin_input()
            game.upd_play()
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.pyxel.set_input()

        self.assertTrue(monster.running)
        self.assertEqual((monster.x, monster.y), (8, 5))
        self.assertEqual(game.turn, 0)
        self.assertEqual(game.st, rogue.ST_AUX)

    def test_rogue_544_move_on_command_moves_without_auto_pickup(self):
        # Rogue 5.4.4 command.c:'m' sets move_on before do_move(); pack.c:pick_up() only reports the item.
        game = new_game(seed=5030)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        item = rogue.Item(rogue.CAT_FOOD, 0)
        item.x, item.y = 6, 5
        game.gitems = [item]
        pack_before = list(game.p.inv)
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            rogue.pyxel.set_input(pressed=[rogue.pyxel.KEY_M])
            game.begin_input()
            game.upd_play()
            rogue.pyxel.set_input(held={rogue.pyxel.KEY_RIGHT}, pressed={rogue.pyxel.KEY_RIGHT})
            game.begin_input()
            game.upd_dir()
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.pyxel.set_input()

        self.assertTrue(monster.running)
        self.assertEqual((game.p.x, game.p.y), (6, 5))
        self.assertEqual(game.gitems, [item])
        self.assertEqual(game.p.inv, pack_before)
        self.assertIn("moved onto", game.msgs[-1])
        self.assertEqual(game.turn, 1)

    def test_rogue_544_current_weapon_command_wakes_visible_monsters_without_turn(self):
        # Rogue 5.4.4 command.c:command() calls misc.c:look(TRUE) before when ')': current weapon.
        game = new_game(seed=5031)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        weapon = rogue.Item(rogue.CAT_WPN, 0)
        game.p.inv = [weapon]
        game.p.wpn = weapon
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            rogue.pyxel.set_input(
                held={rogue.pyxel.KEY_SHIFT, rogue.pyxel.KEY_0},
                pressed=[rogue.pyxel.KEY_0],
            )
            game.begin_input()
            game.upd_play()
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.pyxel.set_input()

        self.assertTrue(monster.running)
        self.assertEqual(game.turn, 0)
        self.assertIn("you are wielding", game.msgs[-1])
        self.assertIn("a)", game.msgs[-1])

    def test_rogue_544_current_armor_command_wakes_visible_monsters_without_turn(self):
        # Rogue 5.4.4 command.c:command() calls misc.c:look(TRUE) before when ']': current armor.
        game = new_game(seed=5032)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        armor = rogue.Item(rogue.CAT_ARM, 0)
        game.p.inv = [armor]
        game.p.arm = armor
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            rogue.pyxel.set_input(pressed=[rogue.pyxel.KEY_RIGHTBRACKET])
            game.begin_input()
            game.upd_play()
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.pyxel.set_input()

        self.assertTrue(monster.running)
        self.assertEqual(game.turn, 0)
        self.assertIn("you are wearing", game.msgs[-1])

    def test_rogue_544_current_rings_command_wakes_visible_monsters_without_turn(self):
        # Rogue 5.4.4 command.c:command() calls misc.c:look(TRUE) before when '=': current rings.
        game = new_game(seed=5033)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        ring = rogue.Item(rogue.CAT_RING, 0)
        game.p.inv = [ring]
        game.p.ring_l = ring
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            rogue.pyxel.set_input(pressed=[rogue.pyxel.KEY_EQUALS])
            game.begin_input()
            game.upd_play()
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.pyxel.set_input()

        self.assertTrue(monster.running)
        self.assertEqual(game.turn, 0)
        self.assertIn("on left hand", game.msgs[-2])
        self.assertIn("on right hand", game.msgs[-1])

    def test_rogue_544_status_command_wakes_visible_monsters_without_turn(self):
        # Rogue 5.4.4 command.c:command() calls misc.c:look(TRUE) before when '@': status.
        game = new_game(seed=5034)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            rogue.pyxel.set_input(pressed=[rogue.pyxel.KEY_AT])
            game.begin_input()
            game.upd_play()
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.pyxel.set_input()

        self.assertTrue(monster.running)
        self.assertEqual(game.turn, 0)
        self.assertEqual(game.st, rogue.ST_PLAY)

    def test_rogue_544_repeat_message_command_wakes_visible_monsters_without_turn(self):
        # Rogue 5.4.4 command.c:command() calls misc.c:look(TRUE) before CTRL('P'): msg(huh).
        game = new_game(seed=5035)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        game.msg_text("old message")
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            rogue.pyxel.set_input(
                held={rogue.pyxel.KEY_CTRL, rogue.pyxel.KEY_P},
                pressed=[rogue.pyxel.KEY_P],
            )
            game.begin_input()
            game.upd_play()
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.pyxel.set_input()

        self.assertTrue(monster.running)
        self.assertEqual(game.turn, 0)
        self.assertEqual(game.msgs[-1], "old message")

    def test_rogue_544_redraw_command_wakes_visible_monsters_without_turn(self):
        # Rogue 5.4.4 command.c:command() calls misc.c:look(TRUE) before CTRL('R'): wrefresh(curscr).
        game = new_game(seed=5036)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        game.msg_text("keep me")
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            rogue.pyxel.set_input(
                held={rogue.pyxel.KEY_CTRL, rogue.pyxel.KEY_R},
                pressed=[rogue.pyxel.KEY_R],
            )
            game.begin_input()
            game.upd_play()
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.pyxel.set_input()

        self.assertTrue(monster.running)
        self.assertEqual(game.turn, 0)
        self.assertEqual(game.msgs[-1], "keep me")
        self.assertEqual(game.st, rogue.ST_PLAY)
        self.assertIsNone(game.cact)

    def test_rogue_544_space_command_wakes_visible_monsters_without_turn(self):
        # Rogue 5.4.4 command.c:command() calls misc.c:look(TRUE) before when ' ': after = FALSE.
        game = new_game(seed=5037)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        game.msg_text("keep me")
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            rogue.pyxel.set_input(
                held={rogue.pyxel.KEY_SPACE},
                pressed=[rogue.pyxel.KEY_SPACE],
            )
            game.begin_input()
            game.upd_play()
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.pyxel.set_input()

        self.assertTrue(monster.running)
        self.assertEqual(game.turn, 0)
        self.assertEqual(game.msgs[-1], "keep me")

    def test_rogue_544_identify_symbol_command_wakes_and_prompts_without_turn(self):
        # Rogue 5.4.4 command.c:command() calls misc.c:look(TRUE) before when '/': identify().
        game = new_game(seed=5038)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            rogue.pyxel.set_input(pressed=[rogue.pyxel.KEY_SLASH])
            game.begin_input()
            game.upd_play()
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.pyxel.set_input()

        self.assertTrue(monster.running)
        self.assertEqual(game.turn, 0)
        self.assertEqual(game.st, rogue.ST_PLAY)
        self.assertTrue(game.identify_symbol_pending)
        self.assertIn("what do you want identified?", game.msgs[-1])

    def test_rogue_544_identify_symbol_reports_table_entry_without_turn(self):
        # Rogue 5.4.4 command.c:identify() maps PLAYER to "you".
        game = new_game(seed=5039)
        game.identify_symbol_pending = True
        game.msg_text("what do you want identified? ")

        rogue.pyxel.set_input(pressed=[rogue.pyxel.KEY_AT])
        game.begin_input()
        game.upd_play()
        rogue.pyxel.set_input()

        self.assertEqual(game.turn, 0)
        self.assertFalse(game.identify_symbol_pending)
        self.assertEqual(game.msgs[-1], "'@': you")

    def test_rogue_544_identify_symbol_reports_monster_name_without_turn(self):
        # Rogue 5.4.4 command.c:identify() maps uppercase A-Z through extern.c:monsters[].
        game = new_game(seed=5040)
        game.identify_symbol_pending = True
        game.msg_text("what do you want identified? ")

        rogue.pyxel.set_input(
            held={rogue.pyxel.KEY_SHIFT, rogue.pyxel.KEY_D},
            pressed=[rogue.pyxel.KEY_D],
        )
        game.begin_input()
        game.upd_play()
        rogue.pyxel.set_input()

        self.assertEqual(game.turn, 0)
        self.assertFalse(game.identify_symbol_pending)
        self.assertEqual(game.msgs[-1], "'D': dragon")

    def test_help_text_lists_rogue_identify_symbol_command(self):
        # Rogue 5.4.4 extern.c:helpstr[] lists '/' as identify.
        game = new_game(seed=5041)
        calls = []
        game.txt = lambda x, y, s, c: calls.append(str(s))

        game.draw_help()

        self.assertIn("/ Identify", "\n".join(calls))

    def test_rogue_544_picky_inventory_empty_wakes_and_spends_no_turn(self):
        # Rogue 5.4.4 command.c:'I' calls pack.c:picky_inven(); empty pack prints and after=FALSE.
        game = new_game(seed=5042)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        game.p.inv = []
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            rogue.pyxel.set_input(
                held={rogue.pyxel.KEY_SHIFT, rogue.pyxel.KEY_I},
                pressed=[rogue.pyxel.KEY_I],
            )
            game.begin_input()
            game.upd_play()
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.pyxel.set_input()

        self.assertTrue(monster.running)
        self.assertEqual(game.turn, 0)
        self.assertEqual(game.st, rogue.ST_PLAY)
        self.assertIn("you aren't carrying anything", game.msgs)

    def test_rogue_544_picky_inventory_single_item_prints_without_prompt(self):
        # Rogue 5.4.4 pack.c:picky_inven() prints the lone item directly.
        game = new_game(seed=5043)
        food = rogue.Item(rogue.CAT_FOOD, 0)
        game.p.inv = [food]

        rogue.pyxel.set_input(
            held={rogue.pyxel.KEY_SHIFT, rogue.pyxel.KEY_I},
            pressed=[rogue.pyxel.KEY_I],
        )
        game.begin_input()
        game.upd_play()
        rogue.pyxel.set_input()

        self.assertEqual(game.turn, 0)
        self.assertEqual(game.st, rogue.ST_PLAY)
        self.assertIn("a)", game.msgs[-1])

    def test_rogue_544_picky_inventory_multiple_prompts_then_prints_letter(self):
        # Rogue 5.4.4 pack.c:picky_inven() prompts and accepts a pack letter.
        game = new_game(seed=5044)
        food = rogue.Item(rogue.CAT_FOOD, 0)
        potion = rogue.Item(rogue.CAT_POT, 0)
        game.p.inv = [food, potion]

        rogue.pyxel.set_input(
            held={rogue.pyxel.KEY_SHIFT, rogue.pyxel.KEY_I},
            pressed=[rogue.pyxel.KEY_I],
        )
        game.begin_input()
        game.upd_play()
        rogue.pyxel.set_input()

        self.assertEqual(game.turn, 0)
        self.assertEqual(game.st, rogue.ST_ITEM)
        self.assertEqual(game.cact, "Picky inventory")
        self.assertIn("which item do you wish to inventory", game.msgs[-1])

        rogue.pyxel.set_input(pressed=[rogue.pyxel.KEY_B])
        game.begin_input()
        game.upd_item()
        rogue.pyxel.set_input()

        self.assertEqual(game.turn, 0)
        self.assertEqual(game.st, rogue.ST_PLAY)
        self.assertIn("b)", game.msgs[-1])

    def test_rogue_544_picky_inventory_invalid_letter_stays_in_prompt(self):
        # Rogue 5.4.4 pack.c:picky_inven() reports "'x' not in pack" and consumes no turn.
        game = new_game(seed=5045)
        game.p.inv = [rogue.Item(rogue.CAT_FOOD, 0)]
        game.cact = "Picky inventory"
        game.fitems = list(game.p.inv)
        game.st = rogue.ST_ITEM

        rogue.pyxel.set_input(pressed=[rogue.pyxel.KEY_M])
        game.begin_input()
        game.upd_item()
        rogue.pyxel.set_input()

        self.assertEqual(game.turn, 0)
        self.assertEqual(game.st, rogue.ST_ITEM)
        self.assertIn("'m' not in pack", game.msgs)

    def test_rogue_544_down_stairs_command_wakes_and_rejects_floor_without_turn(self):
        # Rogue 5.4.4 command.c:command() calls misc.c:look(TRUE) before when '>': d_level().
        game = new_game(seed=5046)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        for x in (5, 6, 7, 8):
            game.tm[5][x] = rogue.T_CORR
        game.rooms = []
        game.p.x, game.p.y = 5, 5
        monster = monster_at(8, 5, hp=10, armor=100, exp=5, flags="mean")
        game.mons = [monster]
        game.visible = {(monster.x, monster.y)}

        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            rogue.pyxel.set_input(
                held={rogue.pyxel.KEY_SHIFT, rogue.pyxel.KEY_PERIOD},
                pressed=[rogue.pyxel.KEY_PERIOD],
            )
            game.begin_input()
            game.upd_play()
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.pyxel.set_input()

        self.assertTrue(monster.running)
        self.assertEqual(game.turn, 0)
        self.assertIn("I see no way down", game.msgs)

    def test_rogue_544_down_stairs_command_descends_even_with_amulet(self):
        # Rogue 5.4.4 command.c:d_level() ignores amulet and always goes down on stairs.
        game = new_game(seed=5047)
        set_open_floor(game)
        game.tm[game.p.y][game.p.x] = rogue.T_STAIR
        game.p.has_amulet = True
        old_depth = game.p.depth

        rogue.pyxel.set_input(
            held={rogue.pyxel.KEY_SHIFT, rogue.pyxel.KEY_PERIOD},
            pressed=[rogue.pyxel.KEY_PERIOD],
        )
        game.begin_input()
        game.upd_play()
        rogue.pyxel.set_input()

        self.assertEqual(game.turn, 1)
        self.assertEqual(game.p.depth, old_depth + 1)
        self.assertNotEqual(game.st, rogue.ST_WIN)

    def test_rogue_544_up_stairs_command_blocks_without_amulet_without_turn(self):
        # Rogue 5.4.4 command.c:u_level() blocks upward stairs without amulet.
        game = new_game(seed=5048)
        set_open_floor(game)
        game.tm[game.p.y][game.p.x] = rogue.T_STAIR
        old_depth = game.p.depth

        rogue.pyxel.set_input(
            held={rogue.pyxel.KEY_SHIFT, rogue.pyxel.KEY_COMMA},
            pressed=[rogue.pyxel.KEY_COMMA],
        )
        game.begin_input()
        game.upd_play()
        rogue.pyxel.set_input()

        self.assertEqual(game.turn, 0)
        self.assertEqual(game.p.depth, old_depth)
        self.assertIn("your way is magically blocked", game.msgs)

    def test_rogue_544_up_stairs_command_wins_on_depth_one_with_amulet(self):
        # Rogue 5.4.4 command.c:u_level() calls total_winner() when level reaches zero.
        game = new_game(seed=5049)
        set_open_floor(game)
        game.tm[game.p.y][game.p.x] = rogue.T_STAIR
        game.p.depth = 1
        game.p.has_amulet = True

        rogue.pyxel.set_input(
            held={rogue.pyxel.KEY_SHIFT, rogue.pyxel.KEY_COMMA},
            pressed=[rogue.pyxel.KEY_COMMA],
        )
        game.begin_input()
        game.upd_play()
        rogue.pyxel.set_input()

        self.assertEqual(game.st, rogue.ST_WIN)
        self.assertIn("You escaped with the Amulet of Yendor!", game.msgs)

    def test_visible_mean_monster_can_wake_and_run(self):
        game = new_game(seed=502)
        set_open_floor(game)
        monster = monster_at(game.p.x + 2, game.p.y, hp=10, armor=100, exp=5, flags="mean")
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
        self.assertIn("you are frozen by the ice monster", game.msgs)

    def test_rogue_544_ice_monster_hit_has_no_hit_message(self):
        # Rogue 5.4.4 fight.c:attack() skips hit() when mp->t_type == 'I'.
        game = new_game(seed=5031)
        set_open_floor(game)
        monster = monster_at(game.p.x + 1, game.p.y, "I", "ice monster", 10, 20, 100, "0x0", 5, "freeze")
        game.roll_monster_attack = lambda m: (True, 0)
        game.monster_hit_message = lambda subject: "ice hit"

        game.m_attack(monster)

        self.assertNotIn("ice hit", game.msgs)
        self.assertIn("you are frozen by the ice monster", game.msgs)

    def test_rogue_544_ice_monster_freeze_message_names_attacker(self):
        # Rogue 5.4.4 fight.c:attack() non-terse text appends "by the %s".
        game = new_game(seed=5032)
        set_open_floor(game)
        monster = monster_at(game.p.x + 1, game.p.y, "I", "ice monster", 10, 20, 100, "0x0", 5, "freeze")
        game.roll_monster_attack = lambda m: (True, 0)

        game.m_attack(monster)

        self.assertIn("you are frozen by the ice monster", game.msgs)

    def test_rogue_544_unseen_monster_attack_uses_something_name(self):
        # Rogue 5.4.4 fight.c:set_mname() uses "something" when !see_monst() && !SEEMONST.
        game = new_game(seed=5033)
        set_open_floor(game)
        game.p.blind = 1
        monster = monster_at(game.p.x + 1, game.p.y, "R", "rattlesnake", 10, 20, 100, "1x1", 5, "poison")
        game.roll_monster_attack = lambda m: (True, 0)
        game.monster_hit_message = lambda subject: f"{subject} hit you"

        game.m_attack(monster)

        self.assertIn("Something hit you", game.msgs)
        self.assertNotIn("The rattlesnake hit you", game.msgs)

    def test_rogue_544_hallucinating_monster_attack_uses_random_monster_name(self):
        # Rogue 5.4.4 fight.c:set_mname() uses the hallucinated A-Z screen glyph as the monster name.
        game = new_game(seed=5034)
        set_open_floor(game)
        game.p.hallucinating = 10
        monster = monster_at(game.p.x + 1, game.p.y, "H", "hobgoblin", 10, 20, 100, "1x1", 5, "")
        game.roll_monster_attack = lambda m: (True, 0)
        game.monster_hit_message = lambda subject: f"{subject} hit you"
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 3 if n == 26 else 0
            game.m_attack(monster)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertIn("The dragon hit you", game.msgs)
        self.assertNotIn("The hobgoblin hit you", game.msgs)

    def test_rogue_544_unseen_ice_freeze_message_keeps_the_prefix(self):
        # Rogue 5.4.4 fight.c:attack() appends " by the %s" even when set_mname() returns "something".
        game = new_game(seed=5035)
        set_open_floor(game)
        game.p.blind = 1
        monster = monster_at(game.p.x + 1, game.p.y, "I", "ice monster", 10, 20, 100, "0x0", 5, "freeze")
        game.roll_monster_attack = lambda m: (True, 0)

        game.m_attack(monster)

        self.assertIn("you are frozen by the something", game.msgs)

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

    def test_rogue_544_ice_freeze_thaws_by_no_command_decrement_without_refreeze(self):
        # Rogue 5.4.4 command.c:command() decrements no_command each command loop.
        game = new_game(seed=5036)
        set_open_floor(game)
        monster = monster_at(game.p.x + 1, game.p.y, "I", "ice monster", 10, 20, 100, "0x0", 5, "freeze")
        game.roll_monster_attack = lambda m: (True, 0)
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 0
            game.m_attack(monster)
        finally:
            rogue.RNG.rnd = old_rnd
        game.mons = []

        self.assertEqual(game.p.no_command, 2)
        game.update()
        self.assertEqual(game.p.no_command, 1)
        game.update()
        self.assertEqual(game.p.no_command, 0)
        self.assertIn("you can move again", game.msgs)

    def test_rogue_544_ice_monster_miss_has_no_miss_message(self):
        # Rogue 5.4.4 fight.c:attack() skips miss() when mp->t_type == 'I'.
        game = new_game(seed=504)
        set_open_floor(game)
        monster = monster_at(game.p.x + 1, game.p.y, "I", "ice monster", 10, 20, 100, "0x0", 5, "freeze")
        game.roll_monster_attack = lambda m: (False, 0)
        game.monster_miss_message = lambda subject: "ice missed"

        game.m_attack(monster)

        self.assertNotIn("ice missed", game.msgs)

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
        # Rogue 5.4.4 fight.c:attack() calls chg_str(-1), which clamps at 3 but still reports weakness.
        import rogue_fight

        self.assertEqual(rogue_fight.poison_bite_strength(10, poison_saved=False, sustain_strength=False), (9, "weakened"))
        self.assertEqual(rogue_fight.poison_bite_strength(10, poison_saved=False, sustain_strength=True), (10, "sustained"))
        self.assertEqual(rogue_fight.poison_bite_strength(10, poison_saved=True, sustain_strength=False), (10, None))
        self.assertEqual(rogue_fight.poison_bite_strength(3, poison_saved=False, sustain_strength=False), (3, "weakened"))

    def test_rogue_544_fight_helper_poison_bite_message_key_matches_attack_non_terse(self):
        # Rogue 5.4.4 fight.c:attack() has distinct non-terse messages for weakened and sustained poison bites.
        import rogue_fight

        self.assertEqual(
            rogue_fight.poison_bite_message_key("weakened", terse=False),
            "fight.you_feel_a_bite_in_your_leg_and_now_feel_weaker",
        )
        self.assertEqual(
            rogue_fight.poison_bite_message_key("sustained", terse=False),
            "fight.a_bite_momentarily_weakens_you",
        )
        self.assertIsNone(rogue_fight.poison_bite_message_key(None, terse=False))

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

    def test_rogue_544_move_helper_confused_player_random_gate_uses_rnd5(self):
        # Rogue 5.4.4 move.c:do_move() gates player rndmove() with rnd(5) != 0.
        import rogue_move

        calls = []
        self.assertFalse(rogue_move.confused_player_uses_random_move(False, lambda n: calls.append(n) or 1))
        self.assertEqual(calls, [])
        self.assertFalse(rogue_move.confused_player_uses_random_move(True, lambda n: calls.append(n) or 0))
        self.assertTrue(rogue_move.confused_player_uses_random_move(True, lambda n: calls.append(n) or 1))
        self.assertEqual(calls, [5, 5])

    def test_rogue_544_move_helper_held_gate_blocks_non_f_destinations(self):
        # Rogue 5.4.4 move.c:do_move() ISHELD gate checks destination ch != 'F'.
        import rogue_move

        self.assertTrue(rogue_move.held_move_blocked(True, False))
        self.assertFalse(rogue_move.held_move_blocked(True, True))
        self.assertFalse(rogue_move.held_move_blocked(False, False))

    def test_rogue_544_player_confused_move_uses_input_direction_when_rnd5_zero(self):
        # Rogue 5.4.4 move.c:do_move() only calls rndmove() when ISHUH && rnd(5) != 0.
        game = new_game(seed=516)
        set_open_floor(game)
        game.daemons.kill("runners")
        game.daemons.kill("doctor")
        game.daemons.kill("stomach")
        game.p.x, game.p.y = 10, 10
        game.p.confused = 10
        old_rnd = rogue.RNG.rnd
        old_choice = rogue.RNG.choice
        try:
            rogue.RNG.rnd = lambda n: 0
            rogue.RNG.choice = lambda seq: -1
            game.try_move(1, 0)
        finally:
            rogue.RNG.rnd = old_rnd
            rogue.RNG.choice = old_choice

        self.assertEqual((game.p.x, game.p.y), (11, 10))

    def test_rogue_544_player_confused_rndmove_rejects_normal_monster(self):
        # Rogue 5.4.4 move.c:rndmove() uses winat()/step_ok(); normal monster glyphs are not step_ok().
        game = new_game(seed=531)
        set_open_floor(game)
        game.daemons.kill("runners")
        game.daemons.kill("doctor")
        game.daemons.kill("stomach")
        game.p.x, game.p.y = 10, 10
        game.p.confused = 5
        monster = monster_at(11, 10)
        game.mons = [monster]
        rng = SequenceRng([1, 1, 2])
        old_rnd = rogue.RNG.rnd
        attacks = []
        try:
            rogue.RNG.rnd = rng.rnd
            game.p_attack = lambda mo: attacks.append(mo)
            turn = game.turn
            moved = game.try_move(0, 1)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertFalse(moved)
        self.assertEqual(attacks, [])
        self.assertEqual((game.p.x, game.p.y), (10, 10))
        self.assertEqual(game.turn, turn)
        self.assertEqual(rng.calls, [5, 3, 3])

    def test_rogue_544_player_confused_rndmove_rejects_scare_scroll(self):
        # Rogue 5.4.4 move.c:rndmove() rejects S_SCARE after a SCROLL winat() result.
        game = new_game(seed=532)
        set_open_floor(game)
        game.daemons.kill("runners")
        game.daemons.kill("doctor")
        game.daemons.kill("stomach")
        game.p.x, game.p.y = 10, 10
        game.p.confused = 5
        scare_kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "scare monster")
        scroll = rogue.Item(rogue.CAT_SCR, scare_kind)
        scroll.x, scroll.y = 11, 10
        game.gitems = [scroll]
        rng = SequenceRng([1, 1, 2])
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = rng.rnd
            turn = game.turn
            moved = game.try_move(0, 1)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertFalse(moved)
        self.assertEqual((game.p.x, game.p.y), (10, 10))
        self.assertEqual(game.gitems, [scroll])
        self.assertEqual(game.turn, turn)
        self.assertEqual(rng.calls, [5, 3, 3])

    def test_rogue_544_held_player_move_away_spends_turn_without_moving(self):
        # Rogue 5.4.4 move.c:do_move() reports ISHELD after the destination checks and leaves after true.
        game = new_game(seed=517)
        set_open_floor(game)
        game.daemons.kill("runners")
        game.daemons.kill("doctor")
        game.daemons.kill("stomach")
        game.p.x, game.p.y = 10, 10
        flytrap = monster_at(11, 10, "F", "venus flytrap", hp=10, damage="0x0", flags="hold")
        game.p.held_by = flytrap
        game.mons = [flytrap]

        turn = game.turn
        moved = game.try_move(0, -1)

        self.assertTrue(moved)
        self.assertEqual((game.p.x, game.p.y), (10, 10))
        self.assertEqual(game.turn, turn + 1)
        self.assertIn("you are being held", game.msgs)

    def test_rogue_544_hidden_trap_preempts_held_move_gate(self):
        # Rogue 5.4.4 move.c:do_move() reveals hidden FLOOR traps before the ISHELD gate.
        game = new_game(seed=519)
        set_open_floor(game)
        game.daemons.kill("runners")
        game.daemons.kill("doctor")
        game.daemons.kill("stomach")
        game.p.x, game.p.y = 10, 10
        flytrap = monster_at(11, 10, "F", "venus flytrap", hp=10, damage="0x0", flags="hold")
        game.p.held_by = flytrap
        game.mons = [flytrap]
        kind = next(i for i, t in enumerate(rogue.TRAPS) if t["name"] == "bear trap")
        game.traps[(10, 9)] = kind

        turn = game.turn
        moved = game.try_move(0, -1)

        self.assertTrue(moved)
        self.assertEqual((game.p.x, game.p.y), (10, 9))
        self.assertEqual(game.tm[9][10], rogue.T_TRAP)
        self.assertEqual(game.p.no_move, rogue.BEARTIME)
        self.assertEqual(game.turn, turn + 1)
        self.assertIn("you are caught in a bear trap", game.msgs)
        self.assertNotIn("you are being held", game.msgs)

    def test_rogue_544_hidden_trap_under_monster_does_not_preempt_held_gate(self):
        # Rogue 5.4.4 move.c:do_move() only takes the hidden trap branch when winat() is FLOOR.
        game = new_game(seed=520)
        set_open_floor(game)
        game.daemons.kill("runners")
        game.daemons.kill("doctor")
        game.daemons.kill("stomach")
        game.p.x, game.p.y = 10, 10
        flytrap = monster_at(11, 10, "F", "venus flytrap", hp=10, damage="0x0", flags="hold")
        hobgoblin = monster_at(10, 9, hp=10)
        game.p.held_by = flytrap
        game.mons = [flytrap, hobgoblin]
        kind = next(i for i, t in enumerate(rogue.TRAPS) if t["name"] == "bear trap")
        game.traps[(10, 9)] = kind
        attacks = []
        game.p_attack = lambda monster: attacks.append(monster)

        turn = game.turn
        moved = game.try_move(0, -1)

        self.assertTrue(moved)
        self.assertEqual(attacks, [])
        self.assertEqual((game.p.x, game.p.y), (10, 10))
        self.assertEqual(game.tm[9][10], rogue.T_FLOOR)
        self.assertEqual(game.p.no_move, 0)
        self.assertEqual(game.turn, turn + 1)
        self.assertIn("you are being held", game.msgs)

    def test_rogue_544_held_player_can_attack_any_venus_flytrap_destination(self):
        # Rogue 5.4.4 move.c:do_move() ISHELD gate checks ch != 'F', not holder identity.
        game = new_game(seed=521)
        set_open_floor(game)
        game.daemons.kill("runners")
        game.daemons.kill("doctor")
        game.daemons.kill("stomach")
        game.p.x, game.p.y = 10, 10
        holder = monster_at(11, 10, "F", "venus flytrap", hp=10, damage="0x0", flags="hold")
        other = monster_at(10, 9, "F", "venus flytrap", hp=10, damage="0x0", flags="hold")
        game.p.held_by = holder
        game.mons = [holder, other]
        attacks = []
        game.p_attack = lambda monster: attacks.append(monster)

        turn = game.turn
        moved = game.try_move(0, -1)

        self.assertTrue(moved)
        self.assertEqual(attacks, [other])
        self.assertEqual((game.p.x, game.p.y), (10, 10))
        self.assertEqual(game.turn, turn + 1)
        self.assertNotIn("you are being held", game.msgs)

    def test_rogue_544_confused_held_player_blocks_random_move_away_after_rndmove(self):
        # Rogue 5.4.4 move.c:do_move() applies ISHELD after confused rndmove() chooses nh.
        game = new_game(seed=518)
        set_open_floor(game)
        game.daemons.kill("runners")
        game.daemons.kill("doctor")
        game.daemons.kill("stomach")
        game.p.x, game.p.y = 10, 10
        game.p.confused = 10
        flytrap = monster_at(11, 10, "F", "venus flytrap", hp=10, damage="0x0", flags="hold")
        game.p.held_by = flytrap
        game.mons = [flytrap]
        old_rnd = rogue.RNG.rnd
        try:
            rolls = iter([1, 0, 1])
            rogue.RNG.rnd = lambda n: next(rolls)
            turn = game.turn
            moved = game.try_move(1, 0)
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertTrue(moved)
        self.assertEqual((game.p.x, game.p.y), (10, 10))
        self.assertEqual(game.turn, turn + 1)
        self.assertIn("you are being held", game.msgs)

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

    def test_rogue_544_chase_ignores_non_source_scared_flag(self):
        # Rogue 5.4.4 chase.c:chase() has no monster flee/scared branch.
        game = new_game(seed=508)
        set_open_floor(game)
        game.p.x, game.p.y = 5, 5
        monster = monster_at(7, 5, hp=10, armor=100, exp=5)
        monster.scared = 2
        game.mons = [monster]

        game.chase(monster, (game.p.x, game.p.y))

        self.assertEqual((monster.x, monster.y), (6, 5))
        self.assertEqual(monster.scared, 2)

    def test_rogue_544_chase_helper_confusion_clears_on_rnd20_zero(self):
        # Rogue 5.4.4 chase.c:chase() always rolls rnd(20) after random movement.
        import rogue_chase

        rng = SequenceRng([0])
        self.assertTrue(rogue_chase.confusion_clears_after_random_move(1, rng.rnd))
        self.assertEqual(rng.calls, [20])

        rng = SequenceRng([1])
        self.assertFalse(rogue_chase.confusion_clears_after_random_move(1, rng.rnd))
        self.assertEqual(rng.calls, [20])

        rng = SequenceRng([0])
        self.assertFalse(rogue_chase.confusion_clears_after_random_move(0, rng.rnd))
        self.assertEqual(rng.calls, [20])

    def test_rogue_544_confused_chase_rndmove_uses_winat_for_item_disguised_xeroc(self):
        # Rogue 5.4.4 move.c:rndmove() uses winat()/step_ok() and does not apply chase.c's Xeroc moat skip.
        game = new_game(seed=524)
        set_open_floor(game)
        game.p.x, game.p.y = 20, 20
        monster = monster_at(5, 5)
        monster.confused = 1
        xeroc = monster_at(6, 5, "X", "xeroc")
        xeroc.disguise = "?"
        game.mons = [monster, xeroc]
        rng = SequenceRng([1, 1, 2, 1])
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = rng.rnd
            game.chase(monster, (10, 5))
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual(rng.calls, [5, 3, 3, 20])
        self.assertEqual((monster.x, monster.y), (6, 5))
        self.assertEqual(xeroc.disguise, "?")

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

    def test_rogue_544_chase_helper_candidate_offsets_match_source_scan_order(self):
        # Rogue 5.4.4 chase.c:chase() loops x from left to right, with y inner.
        import rogue_chase

        self.assertEqual(
            rogue_chase.chase_candidate_offsets(),
            [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)],
        )

    def test_rogue_544_chase_uses_source_candidate_scan_order_for_ties(self):
        # Rogue 5.4.4 chase.c:chase() scans x outer, y inner before rnd(++plcnt) tie choice.
        game = new_game(seed=518)
        set_open_floor(game)
        monster = monster_at(5, 5)
        game.mons = [monster]
        game.p.x, game.p.y = 20, 20
        game.tm[6][4] = rogue.T_VOID
        old_rnd = rogue.RNG.rnd
        try:
            rogue.RNG.rnd = lambda n: 1
            game.chase(monster, (3, 7))
        finally:
            rogue.RNG.rnd = old_rnd

        self.assertEqual((monster.x, monster.y), (4, 5))

    def test_rogue_544_chase_attacks_hero_when_blocking_item_destination(self):
        # Rogue 5.4.4 chase.c:chase() lets PLAYER be chosen even when t_dest is not hero.
        game = new_game(seed=528)
        set_open_floor(game)
        game.p.x, game.p.y = 6, 5
        monster = monster_at(5, 5, hp=10, armor=100, exp=5)
        game.mons = [monster]
        attacks = []
        game.m_attack = lambda mo: attacks.append(mo)

        result = game.chase(monster, (7, 5))

        self.assertEqual(result, "attack")
        self.assertEqual(attacks, [monster])
        self.assertEqual((monster.x, monster.y), (5, 5))

    def test_rogue_544_chase_attacks_hero_standing_on_scare_scroll(self):
        # Rogue 5.4.4 rogue.h:winat() returns PLAYER before the SCROLL under the hero.
        game = new_game(seed=529)
        set_open_floor(game)
        game.p.x, game.p.y = 6, 5
        scare_kind = next(i for i, s in enumerate(rogue.SCROLLS) if s["name"] == "scare monster")
        scroll = rogue.Item(rogue.CAT_SCR, scare_kind)
        scroll.x, scroll.y = game.p.x, game.p.y
        monster = monster_at(5, 5, hp=10, armor=100, exp=5)
        game.gitems = [scroll]
        game.mons = [monster]
        attacks = []
        game.m_attack = lambda mo: attacks.append(mo)

        result = game.chase(monster, (game.p.x, game.p.y))

        self.assertEqual(result, "attack")
        self.assertEqual(attacks, [monster])
        self.assertEqual((monster.x, monster.y), (5, 5))

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

    def test_held_monster_direct_turn_does_not_count_down_hold(self):
        # Rogue 5.4.4 chase.c:move_monst() does not decrement ISHELD; runners() owns the held skip.
        game = new_game(seed=506)
        set_open_floor(game)
        game.p.x, game.p.y = 5, 5
        monster = monster_at(7, 5, hp=10, armor=100, exp=5)
        monster.running = True
        monster.held = 2
        game.mons = [monster]

        game.m_turn(monster)

        self.assertEqual(monster.held, 2)
        self.assertNotEqual((monster.x, monster.y), (7, 5))

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
        self.assertEqual(searched, [])
        self.assertEqual(game.st, rogue.ST_DIR)
        self.assertEqual(game.cact, "Throw")

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
        self.assertEqual(searched, [])
        self.assertEqual(game.st, rogue.ST_DIR)
        self.assertEqual(game.cact, "Throw")

        game = new_game(seed=47)
        set_open_floor(game)
        searched = []
        game.do_search = lambda front_only=False: searched.append(front_only)
        rogue.pyxel.set_input(
            held={rogue.pyxel.KEY_TAB, rogue.pyxel.KEY_ESCAPE},
            pressed={rogue.pyxel.KEY_ESCAPE},
        )
        game.update()
        self.assertEqual(searched, [False])
        self.assertEqual(game.st, rogue.ST_PLAY)

    def test_select_a_prompts_throw_and_select_b_searches(self):
        game = new_game(seed=48)
        set_open_floor(game)
        searched = []
        game.do_search = lambda front_only=False: searched.append(front_only)

        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_BACK, rogue.pyxel.GAMEPAD1_BUTTON_A},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_A},
        )
        game.update()
        self.assertEqual(searched, [])
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

        game = new_game(seed=49)
        set_open_floor(game)
        searched = []
        game.do_search = lambda front_only=False: searched.append(front_only)

        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_BACK, rogue.pyxel.GAMEPAD1_BUTTON_B},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_B},
        )
        game.update()
        self.assertEqual(searched, [False])
        self.assertEqual(game.st, rogue.ST_PLAY)

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

    def test_rogue_544_fall_position_allows_monster_square_candidate(self):
        # Rogue 5.4.4 weapons.c:fallpos() checks chat() terrain and only skips the hero, not p_monst.
        game = new_game(seed=5608)
        px, py = game.p.x, game.p.y
        game.mons = [rogue.Monster(px + 2, py, "B", "bat", 1, 1, 8, "1x2", 1, "")]

        for yy in range(py - 1, py + 2):
            for xx in range(px + 1, px + 4):
                if 0 <= xx < rogue.MAP_W and 0 <= yy < rogue.MAP_H:
                    game.tm[yy][xx] = rogue.T_HWALL
        game.tm[py][px + 2] = rogue.T_FLOOR

        self.assertEqual(game.fall_position(px + 2, py), (px + 2, py))

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

    def test_rogue_544_things_helper_set_order_matches_print_disc(self):
        # Rogue 5.4.4 things.c:set_order() shuffles by swapping i-1 with rnd(i).
        import rogue_things

        rolls = [0, 1, 0, 0]
        calls = []

        def rnd(n):
            calls.append(n)
            return rolls.pop(0)

        self.assertEqual(rogue_things.discovery_order(4, rnd), [2, 3, 1, 0])
        self.assertEqual(calls, [4, 3, 2, 1])

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
                rogue.pyxel.GAMEPAD1_BUTTON_START,
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
            held={rogue.pyxel.GAMEPAD1_BUTTON_BACK, rogue.pyxel.GAMEPAD1_BUTTON_A},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_A},
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
            (rogue.pyxel.KEY_D, set(), "Drop"),
            (rogue.pyxel.KEY_W, set(), "Wear"),
            (rogue.pyxel.KEY_Z, set(), "Zap"),
            (rogue.pyxel.KEY_W, {rogue.pyxel.KEY_SHIFT}, "Wield"),
            (rogue.pyxel.KEY_T, {rogue.pyxel.KEY_SHIFT}, "Take off armor"),
            (rogue.pyxel.KEY_P, {rogue.pyxel.KEY_SHIFT}, "Put on"),
            (rogue.pyxel.KEY_R, {rogue.pyxel.KEY_SHIFT}, "Remove ring"),
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

    def test_rogue_544_item_overlay_pack_letter_can_select_filtered_out_type(self):
        # Rogue 5.4.4 pack.c:get_item() filters only the '*' inventory list;
        # a typed pack letter returns that object and lets quaff() reject the type.
        game = new_game(seed=551)
        scroll = rogue.Item(rogue.CAT_SCR, 0)
        potion = rogue.Item(rogue.CAT_POT, 0)
        game.p.inv = [scroll, potion]
        game.start_item_action("Quaff")

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_A}, pressed={rogue.pyxel.KEY_A})
        game.update()

        self.assertEqual(game.st, rogue.ST_PLAY)
        self.assertIn(scroll, game.p.inv)
        self.assertIn(potion, game.p.inv)
        self.assertIn("yuk! Why would you want to drink that?", game.msgs)

    def test_rogue_544_keyboard_quaff_still_prompts_when_no_potions_but_pack_has_items(self):
        # Rogue 5.4.4 potions.c:quaff() calls pack.c:get_item() before the type gate,
        # so a non-empty pack still reaches the item prompt even without POTION objects.
        game = new_game(seed=5511)
        scroll = rogue.Item(rogue.CAT_SCR, 0)
        game.p.inv = [scroll]

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_Q}, pressed={rogue.pyxel.KEY_Q})
        game.update()

        self.assertEqual(game.st, rogue.ST_ITEM)

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_A}, pressed={rogue.pyxel.KEY_A})
        game.update()

        self.assertEqual(game.st, rogue.ST_PLAY)
        self.assertIn(scroll, game.p.inv)
        self.assertIn("yuk! Why would you want to drink that?", game.msgs)

    def test_rogue_544_call_pack_letter_can_select_food_and_reject_without_name_prompt(self):
        # Rogue 5.4.4 command.c:call() can receive FOOD from pack.c:get_item()
        # by typed letter even though inventory(... CALLABLE) omits it.
        game = new_game(seed=552)
        food = rogue.Item(rogue.CAT_FOOD, 0)
        weapon = rogue.Item(rogue.CAT_WPN, 0)
        game.p.inv = [food, weapon]
        game.start_item_action("Call")

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_A}, pressed={rogue.pyxel.KEY_A})
        game.update()

        self.assertEqual(game.st, rogue.ST_PLAY)
        self.assertIsNone(game.call_item)
        self.assertIn("you can't call that anything", game.msgs)

    def test_rogue_544_call_escape_from_keyboard_command_returns_to_play(self):
        # Rogue 5.4.4 command.c:call() starts with pack.c:get_item(); ESC aborts.
        game = new_game(seed=5521)
        potion = rogue.Item(rogue.CAT_POT, 0)
        game.p.inv = [potion]

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_C}, pressed={rogue.pyxel.KEY_C})
        game.update()

        self.assertEqual(game.st, rogue.ST_CALL)

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_ESCAPE}, pressed={rogue.pyxel.KEY_ESCAPE})
        game.update()

        self.assertEqual(game.st, rogue.ST_PLAY)
        self.assertEqual(game.turn, 0)
        self.assertEqual(game.p.inv, [potion])

    def test_call_escape_from_menu_returns_to_menu(self):
        game = new_game(seed=5522)
        potion = rogue.Item(rogue.CAT_POT, 0)
        game.p.inv = [potion]
        game.open_menu()
        game.start_item_action("Call")

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_ESCAPE}, pressed={rogue.pyxel.KEY_ESCAPE})
        game.update()

        self.assertEqual(game.st, rogue.ST_MENU)

    def test_rogue_544_item_overlay_invalid_pack_letter_keeps_prompt(self):
        # Rogue 5.4.4 pack.c:get_item() reports invalid o_packch and keeps asking.
        game = new_game(seed=553)
        potion = rogue.Item(rogue.CAT_POT, 0)
        game.p.inv = [potion]
        game.start_item_action("Quaff")

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_M}, pressed={rogue.pyxel.KEY_M})
        game.update()

        self.assertEqual(game.st, rogue.ST_ITEM)
        self.assertIn("'m' is not a valid item", game.msgs)

    def test_rogue_544_item_overlay_invalid_pack_letter_is_translated(self):
        # Rogue 5.4.4 pack.c:get_item() invalid o_packch message goes through TextCatalog.
        game = new_game(seed=5531, lang=rogue.LANG_JA)
        potion = rogue.Item(rogue.CAT_POT, 0)
        game.p.inv = [potion]
        game.start_item_action("Quaff")

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_M}, pressed={rogue.pyxel.KEY_M})
        game.update()

        self.assertEqual(game.st, rogue.ST_ITEM)
        self.assertIn("「m」は持ちものではない。", game.msgs)

    def test_rogue_544_item_overlay_shift_letter_is_invalid_uppercase_packch(self):
        # Rogue 5.4.4 pack.c:get_item() compares readchar() to lowercase o_packch;
        # Shift+A is 'A', not pack letter 'a'.
        game = new_game(seed=5532)
        potion = rogue.Item(rogue.CAT_POT, 0)
        game.p.inv = [potion]
        game.start_item_action("Quaff")

        rogue.pyxel.set_input(
            held={rogue.pyxel.KEY_SHIFT, rogue.pyxel.KEY_A},
            pressed={rogue.pyxel.KEY_A},
        )
        game.update()

        self.assertEqual(game.st, rogue.ST_ITEM)
        self.assertIn("'A' is not a valid item", game.msgs)

    def test_rogue_544_keyboard_item_command_empty_pack_uses_get_item_message(self):
        # Rogue 5.4.4 pack.c:get_item() reports an empty pack before command type gates.
        game = new_game(seed=554)
        game.p.inv = []

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_Q}, pressed={rogue.pyxel.KEY_Q})
        game.update()

        self.assertEqual(game.st, rogue.ST_PLAY)
        self.assertIn("you aren't carrying anything", game.msgs)

    def test_rogue_544_get_item_escape_from_keyboard_command_returns_to_play(self):
        # Rogue 5.4.4 pack.c:get_item() ESC aborts the command with after=FALSE.
        game = new_game(seed=555)
        potion = rogue.Item(rogue.CAT_POT, 0)
        game.p.inv = [potion]

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_Q}, pressed={rogue.pyxel.KEY_Q})
        game.update()

        self.assertEqual(game.st, rogue.ST_ITEM)

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_ESCAPE}, pressed={rogue.pyxel.KEY_ESCAPE})
        game.update()

        self.assertEqual(game.st, rogue.ST_PLAY)
        self.assertEqual(game.turn, 0)
        self.assertEqual(game.p.inv, [potion])

    def test_rogue_544_get_dir_escape_from_keyboard_zap_returns_to_play(self):
        # Rogue 5.4.4 command.c:'z' sets after=FALSE when misc.c:get_dir() returns FALSE.
        game = new_game(seed=5551)
        stick = rogue.Item(rogue.CAT_STICK, 0, charges=1)
        game.p.inv = [stick]

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_Z}, pressed={rogue.pyxel.KEY_Z})
        game.update()
        rogue.pyxel.set_input(held={rogue.pyxel.KEY_A}, pressed={rogue.pyxel.KEY_A})
        game.update()

        self.assertEqual(game.st, rogue.ST_DIR)

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_ESCAPE}, pressed={rogue.pyxel.KEY_ESCAPE})
        game.update()

        self.assertEqual(game.st, rogue.ST_PLAY)
        self.assertEqual(game.turn, 0)
        self.assertEqual(stick.charges, 1)

    def test_item_overlay_escape_from_menu_returns_to_menu(self):
        game = new_game(seed=556)
        potion = rogue.Item(rogue.CAT_POT, 0)
        game.p.inv = [potion]
        game.open_menu()
        game.start_item_action("Quaff")

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_ESCAPE}, pressed={rogue.pyxel.KEY_ESCAPE})
        game.update()

        self.assertEqual(game.st, rogue.ST_MENU)

    def test_zap_direction_escape_from_menu_returns_to_menu(self):
        game = new_game(seed=5561)
        stick = rogue.Item(rogue.CAT_STICK, 0, charges=1)
        game.p.inv = [stick]
        game.open_menu()
        game.start_item_action("Zap")

        rogue.pyxel.set_input(held={rogue.pyxel.KEY_A}, pressed={rogue.pyxel.KEY_A})
        game.update()
        rogue.pyxel.set_input(held={rogue.pyxel.KEY_ESCAPE}, pressed={rogue.pyxel.KEY_ESCAPE})
        game.update()

        self.assertEqual(game.st, rogue.ST_MENU)
        self.assertEqual(stick.charges, 1)

    def test_rogue_544_remove_ring_action_filters_equipped_rings(self):
        # Rogue 5.4.4 command.c:'R' calls rings.c:ring_off(), not armor.c:take_off().
        import rogue_rings

        game = new_game(seed=557)
        armor = rogue.Item(rogue.CAT_ARM, 0)
        worn = rogue.Item(rogue.CAT_RING, rogue_rings.R_REGEN)
        unworn = rogue.Item(rogue.CAT_RING, rogue_rings.R_PROTECT)
        game.p.inv = [armor, worn, unworn]
        game.p.arm = armor
        game.p.ring_l = worn

        game.start_item_action("Remove ring")

        self.assertEqual(game.st, rogue.ST_ITEM)
        self.assertEqual(game.fitems, [worn])

    def test_rogue_544_remove_ring_no_rings_uses_ring_off_message(self):
        # Rogue 5.4.4 rings.c:ring_off() reports no rings and does not spend a turn.
        game = new_game(seed=558)
        game.p.inv = [rogue.Item(rogue.CAT_ARM, 0)]

        game.start_item_action("Remove ring")

        self.assertEqual(game.st, rogue.ST_PLAY)
        self.assertEqual(game.turn, 0)
        self.assertIn("you aren't wearing any rings", game.msgs)

    def test_rogue_544_take_off_armor_action_filters_current_armor(self):
        # Rogue 5.4.4 command.c:'T' calls armor.c:take_off(), not rings.c:ring_off().
        import rogue_rings

        game = new_game(seed=559)
        armor = rogue.Item(rogue.CAT_ARM, 0)
        ring = rogue.Item(rogue.CAT_RING, rogue_rings.R_REGEN)
        game.p.inv = [armor, ring]
        game.p.arm = armor
        game.p.ring_l = ring

        game.start_item_action("Take off armor")

        self.assertEqual(game.st, rogue.ST_ITEM)
        self.assertEqual(game.fitems, [armor])

    def test_rogue_544_take_off_armor_no_armor_uses_take_off_message(self):
        # Rogue 5.4.4 armor.c:take_off() reports no armor and sets after=FALSE.
        import rogue_rings

        game = new_game(seed=560)
        ring = rogue.Item(rogue.CAT_RING, rogue_rings.R_REGEN)
        game.p.inv = [ring]
        game.p.arm = None
        game.p.ring_l = ring

        game.start_item_action("Take off armor")

        self.assertEqual(game.st, rogue.ST_PLAY)
        self.assertEqual(game.turn, 0)
        self.assertIn("you aren't wearing any armor", game.msgs)

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
        self.assertIn("</> Stairs", text)
        self.assertIn("q Quaff", text)
        self.assertIn("d Drop", text)
        self.assertIn("I Inv item", text)
        self.assertIn("P Put on", text)
        self.assertIn("R Remove", text)
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

    def test_rogue544_trap_placement_find_floor_does_not_skip_monster_square(self):
        # Rogue 5.4.4 new_level.c trap placement uses find_floor(..., FALSE), which ignores p_monst.
        game = new_game(seed=3047)
        room = rogue.Room(5, 5, 5, 5)
        game.rooms = [room]
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        game.tm[6][6] = rogue.T_FLOOR
        game.p.depth = 4
        game.p.x, game.p.y = 7, 7
        game.gitems = []
        game.traps = {}
        game.mons = [monster_at(6, 6)]

        class TrapRng:
            def rnd(self, n):
                return 0

            def choice(self, seq):
                return seq[0]

            def shuffle(self, seq):
                pass

        old_rng = rogue.RNG
        try:
            rogue.RNG = TrapRng()
            game._spawn_traps()
        finally:
            rogue.RNG = old_rng

        self.assertIn((6, 6), game.traps)

    def test_rogue544_trap_placement_interleaves_find_floor_and_kind_rolls(self):
        # Rogue 5.4.4 new_level.c:new_level() repeats find_floor() then rnd(NTRAPS) for each trap.
        game = new_game(seed=3048)
        room = rogue.Room(5, 5, 5, 5)
        game.rooms = [room]
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        game.tm[6][6] = rogue.T_FLOOR
        game.tm[6][7] = rogue.T_FLOOR
        game.p.depth = 8
        game.p.x, game.p.y = 7, 7
        game.gitems = []
        game.traps = {}
        events = []

        class TrapRng:
            def __init__(self):
                self.floor_rolls = iter([0, 0, 0, 0, 1, 0])

            def rnd(self, n):
                events.append(f"rnd:{n}")
                if n == 10:
                    return 0
                if n == 2:
                    return 1
                if n in (1, 3):
                    return next(self.floor_rolls)
                return 0

            def choice(self, seq):
                raise AssertionError("new_level.c trap placement should use find_floor(), not choice()")

            def shuffle(self, seq):
                events.append("shuffle")

        old_rng = rogue.RNG
        try:
            rogue.RNG = TrapRng()
            game._spawn_traps()
        finally:
            rogue.RNG = old_rng

        self.assertEqual(
            events[:10],
            ["rnd:10", "rnd:2", "rnd:1", "rnd:3", "rnd:3", "rnd:8", "rnd:1", "rnd:3", "rnd:3", "rnd:8"],
        )

    def test_rogue544_trap_placement_floor_gate_has_no_fixed_retry_fallback(self):
        # Rogue 5.4.4 new_level.c:new_level() repeats find_floor() until chat() == FLOOR.
        game = new_game(seed=3049)
        room = rogue.Room(5, 5, 5, 5)
        game.rooms = [room]
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        game.tm[6][6] = rogue.T_CORR
        game.tm[7][7] = rogue.T_FLOOR
        game.p.depth = 4
        game.gitems = []
        game.traps = {}
        cap = rogue.MAP_W * rogue.MAP_H * len(game.rooms)
        positions = iter([(6, 6)] * (cap + 1) + [(7, 7)])
        game.find_floor_pos = lambda *args, **kwargs: next(positions)

        class TrapRng:
            def rnd(self, n):
                return 0

        old_rng = rogue.RNG
        try:
            rogue.RNG = TrapRng()
            game._spawn_traps()
        finally:
            rogue.RNG = old_rng

        self.assertEqual(game.traps, {(7, 7): 0})

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

    def test_rogue544_search_does_not_reveal_hidden_trap_under_item(self):
        # Rogue 5.4.4 command.c:search() reveals hidden traps only when chat() is FLOOR.
        game = new_game(seed=584)
        set_open_floor(game)
        px, py = game.p.x, game.p.y
        game.traps[(px + 1, py)] = 3
        item = rogue.Item(rogue.CAT_FOOD, 0)
        item.x, item.y = px + 1, py
        game.gitems = [item]
        old_randrange = rogue.random.randrange
        try:
            rogue.random.randrange = lambda n: 0
            game.do_search()
        finally:
            rogue.random.randrange = old_randrange

        self.assertEqual(game.tm[py][px + 1], rogue.T_FLOOR)
        self.assertEqual(game.gitems, [item])
        self.assertNotIn("You found something!", game.msgs)

    def test_rogue544_search_does_not_reveal_hidden_trap_under_stairs(self):
        # Rogue 5.4.4 command.c:search() reveals hidden traps only when chat() is FLOOR.
        game = new_game(seed=583)
        set_open_floor(game)
        px, py = game.p.x, game.p.y
        game.traps[(px + 1, py)] = 3
        game.tm[py][px + 1] = rogue.T_STAIR
        old_randrange = rogue.random.randrange
        try:
            rogue.random.randrange = lambda n: 0
            game.do_search()
        finally:
            rogue.random.randrange = old_randrange

        self.assertEqual(game.tm[py][px + 1], rogue.T_STAIR)
        self.assertNotIn("You found something!", game.msgs)

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

    def test_rogue544_hidden_trap_under_item_does_not_trigger_on_move(self):
        # Rogue 5.4.4 move.c:do_move() reveals hidden traps only when winat() is FLOOR.
        game = new_game(seed=592)
        set_open_floor(game)
        game.daemons.kill("runners")
        game.daemons.kill("doctor")
        game.daemons.kill("stomach")
        x, y = game.p.x + 1, game.p.y
        game.traps[(x, y)] = 3
        item = rogue.Item(rogue.CAT_FOOD, 0)
        item.x, item.y = x, y
        game.gitems = [item]
        food_qty = sum(i.qty for i in game.p.inv if i.cat == rogue.CAT_FOOD and i.kind == 0)

        game.try_move(1, 0)

        self.assertEqual((game.p.x, game.p.y), (x, y))
        self.assertEqual(game.tm[y][x], rogue.T_FLOOR)
        self.assertEqual(game.p.stuck, 0)
        self.assertEqual(game.gitems, [])
        self.assertEqual(
            sum(i.qty for i in game.p.inv if i.cat == rogue.CAT_FOOD and i.kind == 0),
            food_qty + 1,
        )
        self.assertNotIn("you are caught in a bear trap", game.msgs)

    def test_rogue544_hidden_trap_under_stairs_does_not_trigger_on_move(self):
        # Rogue 5.4.4 move.c:do_move() reveals hidden traps only when winat() is FLOOR.
        game = new_game(seed=591)
        set_open_floor(game)
        x, y = game.p.x + 1, game.p.y
        game.traps[(x, y)] = 3
        game.tm[y][x] = rogue.T_STAIR

        game.try_move(1, 0)

        self.assertEqual((game.p.x, game.p.y), (x, y))
        self.assertEqual(game.tm[y][x], rogue.T_STAIR)
        self.assertEqual(game.p.stuck, 0)
        self.assertTrue(game.seen_stairs)
        self.assertNotIn("you are caught in a bear trap", game.msgs)

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

    def test_rogue_544_trap_trigger_clears_running_count_before_effect(self):
        # Rogue 5.4.4 move.c:be_trapped() clears running/count before the trap switch.
        game = new_game(seed=620)
        set_open_floor(game)
        x, y = game.p.x + 1, game.p.y
        kind = next(i for i, t in enumerate(rogue.TRAPS) if t["name"] == "bear trap")
        game.traps[(x, y)] = kind
        game.dashing = True
        game.dash_steps = 5

        game.trigger_trap(x, y)

        self.assertFalse(game.dashing)
        self.assertEqual(game.dash_steps, 0)

    def test_rogue_544_move_helper_simple_trap_state_additions_match_source(self):
        # Rogue 5.4.4 move.c:be_trapped() T_BEAR/T_SLEEP add fixed constants.
        import rogue_move

        self.assertEqual(rogue_move.bear_trap_no_move(4, rogue.BEARTIME), 4 + rogue.BEARTIME)
        self.assertEqual(rogue_move.sleep_trap_no_command(7, rogue.SLEEPTIME), 7 + rogue.SLEEPTIME)

    def test_rogue_544_stepping_arrow_trap_miss_drops_from_old_hero_position(self):
        # Rogue 5.4.4 move.c:do_move() calls be_trapped(&nh) before hero = nh.
        game = new_game(seed=630)
        set_open_floor(game)
        game.daemons.kill("runners")
        game.daemons.kill("doctor")
        game.daemons.kill("stomach")
        game.p.x, game.p.y = 10, 10
        kind = next(i for i, t in enumerate(rogue.TRAPS) if t["name"] == "arrow trap")
        game.traps[(11, 10)] = kind
        game.trap_hits = lambda bonus=0: False
        drops = []
        game.drop_thrown = lambda item, x, y, around=True: drops.append((item.cat, item.kind, item.qty, x, y, around))

        game.try_move(1, 0)

        self.assertEqual((game.p.x, game.p.y), (11, 10))
        self.assertEqual(drops, [(rogue.CAT_WPN, 3, 1, 10, 10, True)])

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

    def test_rogue_544_arrow_trap_miss_vanishes_when_fallpos_has_no_candidate(self):
        # Rogue 5.4.4 weapons.c:fall(FALSE) discards the object if fallpos() fails;
        # it does not fall back to the impact coordinate.
        game = new_game(seed=71)
        game.tm = [[rogue.T_VOID for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
        game.p.x, game.p.y = 10, 10
        game.tm[10][10] = rogue.T_FLOOR
        x, y = game.p.x + 1, game.p.y
        kind = next(i for i, t in enumerate(rogue.TRAPS) if t["name"] == "arrow trap")
        game.traps[(x, y)] = kind
        game.trap_hits = lambda bonus=0: False
        game.gitems = []

        game.trigger_trap(x, y)

        self.assertEqual(game.gitems, [])

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

    def test_rogue_544_call_action_includes_weapon_armor_and_excludes_food_amulet(self):
        # Rogue 5.4.4 pack.c:inventory(... CALLABLE) includes non-FOOD/non-AMULET items.
        weapon = rogue.Item(rogue.CAT_WPN, 0)
        armor = rogue.Item(rogue.CAT_ARM, 1)
        food = rogue.Item(rogue.CAT_FOOD, 0)
        amulet = rogue.Item(rogue.CAT_AMULET, 0)
        potion = rogue.Item(rogue.CAT_POT, 0)
        self.g.p.inv = [weapon, armor, food, amulet, potion]

        self.g.start_item_action("Call")

        self.assertIn(weapon, self.g.fitems)
        self.assertIn(armor, self.g.fitems)
        self.assertIn(potion, self.g.fitems)
        self.assertNotIn(food, self.g.fitems)
        self.assertNotIn(amulet, self.g.fitems)

    def test_rogue_544_call_known_type_rejects_without_clearing_guess(self):
        # Rogue 5.4.4 command.c:call() returns "already identified" before editing oi_guess.
        potion = rogue.Item(rogue.CAT_POT, 0, known=True)
        self.g.ident.pk[0] = True
        self.g.ident.pg[0] = "old"

        self.assertFalse(self.g.apply_call_name(potion, "new"))

        self.assertEqual(self.g.ident.pg[0], "old")
        self.assertIn("that has already been identified", self.g.msgs)

    def test_rogue_544_call_food_and_amulet_are_rejected(self):
        # Rogue 5.4.4 CALLABLE excludes FOOD and AMULET from inventory().
        food = rogue.Item(rogue.CAT_FOOD, 0)
        amulet = rogue.Item(rogue.CAT_AMULET, 0)

        self.assertFalse(self.g.apply_call_name(food, "snack"))
        self.assertFalse(self.g.apply_call_name(amulet, "yendor"))

        self.assertIn("you can't call that anything", self.g.msgs)


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

    def test_rogue_544_print_disc_omits_ring_bonus_and_stick_charges(self):
        # Rogue 5.4.4 things.c:print_disc() uses a dummy object with o_flags=0.
        import rogue_rings
        import rogue_sticks

        self.g.ident.rk[rogue_rings.R_PROTECT] = True
        self.g.ident.wk[rogue_sticks.WS_LIGHT] = True

        texts = [t for _, t in self.g._disc_lines()]

        self.assertTrue(any("ring of protection" in t for t in texts))
        self.assertTrue(any("of light" in t for t in texts))
        self.assertFalse(any("[+0]" in t for t in texts))
        self.assertFalse(any("charges" in t for t in texts))

    def test_rogue_544_open_discoveries_consumes_print_disc_rng_once(self):
        # Rogue 5.4.4 things.c:print_disc() calls set_order() once per category display.
        calls = []
        old_rnd = rogue.RNG.rnd
        try:
            self.g.mons = []
            self.g.visible = set()
            rogue.RNG.rnd = lambda n: calls.append(n) or 0
            self.g.open_discoveries()
            expected = len(rogue.POTIONS) + len(rogue.SCROLLS) + len(rogue.RINGS) + len(rogue.STICKS)
            self.assertEqual(len(calls), expected)
            self.g._box = lambda *args, **kwargs: None
            self.g.txt = lambda *args, **kwargs: None
            self.g.draw_disc()
            self.assertEqual(len(calls), expected)
        finally:
            rogue.RNG.rnd = old_rnd


if __name__ == "__main__":
    unittest.main()
