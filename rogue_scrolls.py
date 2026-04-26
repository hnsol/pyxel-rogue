"""Rogue 5.4.4 scrolls.c helpers."""
from __future__ import annotations


def enchant_weapon(weapon, rnd) -> bool:
    """Apply Rogue 5.4.4 scrolls.c:S_ENCH to the current weapon."""
    if weapon is None:
        return False
    weapon.cursed = False
    if rnd(2) == 0:
        weapon.hit_plus += 1
    else:
        weapon.dam_plus += 1
    weapon.ench = weapon.hit_plus
    return True
