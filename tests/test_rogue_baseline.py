import importlib
import os
import random
import sys
import types
import unittest


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
    game.tm = [[rogue.T_FLOOR for _ in range(rogue.MAP_W)] for _ in range(rogue.MAP_H)]
    game.rooms = [rogue.Room(1, 1, rogue.MAP_W - 2, rogue.MAP_H - 2)]
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
    def test_full_map_layout_baseline(self):
        self.assertEqual((rogue.SCR_W, rogue.SCR_H), (512, 320))
        self.assertEqual((rogue.ZV_COLS, rogue.ZV_ROWS), (rogue.MAP_W, rogue.MAP_H))
        self.assertEqual((rogue.ZV_PX_W, rogue.ZV_PX_H), (336, 288))
        self.assertEqual(rogue.AUX_ACTIONS, ["Status", "Help", "Search", "Trap", "Pickup", "Language"])

        game = new_game(seed=5)
        game.cam_x = 99
        game.cam_y = 99
        game.update_cam()
        self.assertEqual((game.cam_x, game.cam_y), (0, 0))

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
        old_randint = rogue.random.randint
        try:
            rogue.random.randint = lambda a, b: b
            self.assertEqual(rogue.roll_damage_expr("1x8"), 8)
            self.assertEqual(rogue.roll_damage_expr("1x2/1x5/1x5"), 12)
            self.assertEqual(rogue.roll_damage_expr("0x0"), 0)
        finally:
            rogue.random.randint = old_randint

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
        self.assertIn(item, game.p.inv)

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
        self.assertIn(item, game.p.inv)
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
        self.assertIn(item, game.p.inv)
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

    def test_status_and_hud_show_exp_denominator_and_armor_label(self):
        game = new_game(seed=35)
        calls = []
        game.txt = lambda x, y, s, c: calls.append(str(s))
        game.draw_stat()
        game.draw_status()
        self.assertTrue(any("Exp 0/10" in c for c in calls))
        self.assertTrue(any("Exp:   0/10" in c for c in calls))
        self.assertTrue(any("Arm " in c or c.startswith("Armor:") for c in calls))
        self.assertTrue(any("Pickup ON" in c for c in calls))
        self.assertTrue(any("Lang EN" in c for c in calls))

    def test_message_log_uses_three_rows_with_latest_highlighted(self):
        game = new_game(seed=35)
        calls = []
        game.txt = lambda x, y, s, c: calls.append((str(s), c))
        game.msgs = ["old", "middle", "latest"]

        game.draw_msgs()

        self.assertEqual(rogue.MSG_LINES, 3)
        self.assertEqual([text for text, _ in calls], ["old", "middle", "latest"])
        self.assertEqual([color for _, color in calls], [5, 5, 7])

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

    def test_direction_pending_merges_cardinal_inputs_into_one_diagonal(self):
        game = new_game(seed=36)
        rogue.pyxel.set_input(
            held={rogue.pyxel.KEY_LEFT},
            pressed={rogue.pyxel.KEY_LEFT},
        )
        self.assertIsNone(game.dir_press())
        self.assertEqual(game.dir_pending, (-1, 0))

        rogue.pyxel.set_input(
            held={rogue.pyxel.KEY_LEFT, rogue.pyxel.KEY_UP},
            pressed={rogue.pyxel.KEY_UP},
        )
        self.assertEqual(game.dir_press(), (-1, -1))
        self.assertIsNone(game.dir_pending)
        rogue.pyxel.set_input()

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

    def test_keyboard_status_help_and_vi_diagonals_remain_supported(self):
        game = new_game(seed=36)
        rogue.pyxel.set_input(held={rogue.pyxel.KEY_I}, pressed={rogue.pyxel.KEY_I})
        game.update()
        self.assertEqual(game.st, rogue.ST_STATUS)

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
        old_randint = rogue.random.randint
        try:
            rogue.random.randint = lambda a, b: b
            game.p_attack(monster)
        finally:
            rogue.random.randint = old_randint
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
        old_randint = rogue.random.randint
        try:
            rogue.random.randint = lambda a, b: 1
            game.use_pot(potion)
        finally:
            rogue.random.randint = old_randint

        self.assertEqual(game.p.hp, game.p.max_hp - 4)
        self.assertIn("You feel much better. (+1)", game.msgs)

    def test_random_weapon_generation_changes_hit_plus_only(self):
        old_random = rogue.random.random
        old_randint = rogue.random.randint
        old_randrange = rogue.random.randrange
        seq = iter([9, 2])
        try:
            rogue.random.random = lambda: 0.70
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
        old_randint = rogue.random.randint
        try:
            rogue.random.randint = lambda a, b: b
            hit, dmg = game.roll_player_attack(monster, arrow, thrown=True)
        finally:
            rogue.random.randint = old_randint
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
            held={rogue.pyxel.GAMEPAD1_BUTTON_BACK, rogue.pyxel.GAMEPAD1_BUTTON_B},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_B},
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

    def test_select_a_prompts_throw_direction_before_item_selection(self):
        game = new_game(seed=48)
        rogue.pyxel.set_input(
            held={rogue.pyxel.GAMEPAD1_BUTTON_BACK, rogue.pyxel.GAMEPAD1_BUTTON_A},
            pressed={rogue.pyxel.GAMEPAD1_BUTTON_A},
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
