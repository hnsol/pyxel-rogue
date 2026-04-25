"""Rogue 5.4.4 chase.c helpers."""
from __future__ import annotations


def runners(monsters, monster_turn) -> None:
    """Rogue 5.4.4 chase.c:runners() ISHELD/ISRUN gate."""
    for monster in list(monsters):
        if getattr(monster, "held", 0) > 0 or not getattr(monster, "running", False):
            continue
        monster_turn(monster)
