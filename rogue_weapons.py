"""Rogue 5.4.4 weapons.c helpers."""
from __future__ import annotations


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


def new_thing_weapon_enchant(roll100: int, rnd):
    """Rogue 5.4.4 things.c:new_thing() weapon curse/enchant branch."""
    if roll100 < 10:
        return -(rnd(3) + 1), True
    if roll100 < 15:
        return rnd(3) + 1, False
    return 0, False
