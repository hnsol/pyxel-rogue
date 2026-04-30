"""Rogue 5.4.4 weapons.c helpers."""
from __future__ import annotations

INIT_DAM = [
    ("2x4", "1x3", None, ()),
    ("3x4", "1x2", None, ()),
    ("1x1", "1x1", None, ()),
    ("1x1", "2x3", 2, ("many", "missile")),
    ("1x6", "1x4", None, ("missile",)),
    ("4x4", "1x2", None, ()),
    ("1x1", "1x3", None, ("many", "missile")),
    ("1x2", "2x4", None, ("many", "missile")),
    ("2x3", "1x6", None, ("missile",)),
]

_GROUP = 2


def apply_init_dam(weapon: dict, index: int) -> dict:
    """Apply Rogue 5.4.4 weapons.c:init_dam[] fields to a weapon row."""
    damage, hurl_damage, launcher, flags = INIT_DAM[index]
    weapon["damage"] = damage
    weapon["hurl_damage"] = hurl_damage
    if launcher is not None:
        weapon["launcher"] = launcher
    if "many" in flags:
        weapon["stack"] = True
    if "missile" in flags:
        weapon["missile"] = True
    return weapon


def next_weapon_group() -> int:
    """Rogue 5.4.4 weapons.c:init_weapon() static group++."""
    global _GROUP
    group = _GROUP
    _GROUP += 1
    return group


def is_fallpos_candidate(pos, hero_pos, tile) -> bool:
    """Rogue 5.4.4 weapons.c:fallpos() candidate tile gate."""
    return pos != hero_pos and tile in ("FLOOR", "PASSAGE")


def choose_fallpos(choice, count: int, candidate, rnd):
    """Rogue 5.4.4 weapons.c:fallpos() rnd(++cnt)==0 selection."""
    count += 1
    if rnd(count) == 0:
        choice = candidate
    return choice, count


def fall_result(fallpos, pr: bool):
    """Rogue 5.4.4 weapons.c:fall() outcome."""
    if fallpos is not None:
        return "drop", fallpos
    return ("vanish" if pr else "discard"), None


def initial_weapon_count(weapon_name: str, is_many: bool, rnd) -> int:
    """Rogue 5.4.4 weapons.c:init_weapon() initial stack count."""
    if weapon_name == "dagger":
        return rnd(4) + 2
    if is_many:
        return rnd(8) + 8
    return 1


def initial_weapon_group(weapon_name: str, is_many: bool) -> int:
    """Rogue 5.4.4 weapons.c:init_weapon() o_group assignment."""
    if weapon_name == "dagger" or is_many:
        return next_weapon_group()
    return 0


def new_thing_weapon_enchant(roll100: int, rnd):
    """Rogue 5.4.4 things.c:new_thing() weapon curse/enchant branch."""
    if roll100 < 10:
        return -(rnd(3) + 1), True
    if roll100 < 15:
        return rnd(3) + 1, False
    return 0, False


def wield_result(current_cursed: bool, item_is_armor: bool, is_current: bool) -> str:
    """Rogue 5.4.4 weapons.c:wield() gate result."""
    if current_cursed:
        return "cursed"
    if item_is_armor:
        return "armor"
    if is_current:
        return "current"
    return "wield"
