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
