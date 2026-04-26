"""Rogue 5.4.4 armor/things helpers."""
from __future__ import annotations


def new_thing_armor_enchant(roll100: int, rnd):
    """Rogue 5.4.4 things.c:new_thing() armor curse/enchant branch."""
    if roll100 < 20:
        return -(rnd(3) + 1), True
    if roll100 < 28:
        return rnd(3) + 1, False
    return 0, False
