"""Rogue 5.4.4 chase.c helpers."""
from __future__ import annotations


def runners(monsters, monster_turn) -> None:
    """Rogue 5.4.4 chase.c:runners() ISHELD/ISRUN gate."""
    for monster in list(monsters):
        if getattr(monster, "held", 0) > 0 or not getattr(monster, "running", False):
            continue
        monster_turn(monster)


def monster_turn(monster, move_monst, distance_to_hero) -> None:
    """Rogue 5.4.4 chase.c:runners() per-monster move plus ISFLY extra move."""
    if not getattr(monster, "alive", False) or not getattr(monster, "running", False):
        return
    move_monst(monster)
    if getattr(monster, "alive", False) and "fly" in getattr(monster, "flags", set()) and distance_to_hero(monster) >= 3:
        move_monst(monster)
