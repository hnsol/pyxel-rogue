"""Rogue 5.4.4 fight.c helpers."""
from __future__ import annotations


def swing(at_lvl: int, op_arm: int, wplus: int, rnd) -> bool:
    """Rogue 5.4.4 fight.c:swing()."""
    need = (20 - at_lvl) - op_arm
    return rnd(20) + wplus >= need


def magic_item_to_steal(inventory, equipped_items, is_magic_item, rnd):
    """Rogue 5.4.4 fight.c:attack() Nymph steal selection."""
    steal = None
    nobj = 0
    for item in inventory:
        if item in equipped_items:
            continue
        if is_magic_item(item):
            nobj += 1
            if rnd(nobj) == 0:
                steal = item
    return steal


def goldcalc(level: int, rnd) -> int:
    """Rogue 5.4.4 rogue.h:GOLDCALC."""
    return rnd(50 + 10 * level) + 2


def roll_damage_expr(expr: str, roll) -> int:
    """Rogue 5.4.4 fight.c:roll_em() damage expression roll."""
    total = 0
    for part in expr.split("/"):
        sep = "x" if "x" in part else "d"
        n, sides = part.split(sep)
        total += roll(int(n), int(sides))
    return total
